"""
Quiz Solver Module
Orchestrates the quiz solving process using LLM-generated scripts
"""
import os
import time
import logging
import subprocess
import tempfile
from typing import Optional, Dict, Any
import httpx
from scraper import QuizScraper
from prompts import get_script_generation_prompt, SYSTEM_PROMPT_DEFENSE, USER_PROMPT_ATTACK

logger = logging.getLogger(__name__)

# AI Pipe API Configuration
AI_PIPE_API_URL = "https://aipipe.ai/v1/chat/completions"
DEFAULT_MODEL = "gpt-4.1-nano"
FALLBACK_MODELS = ["gpt-4.1-nano"]

# Time limits
MAX_TOTAL_TIME = 180  # 3 minutes total
SCRIPT_TIMEOUT = 150  # 2.5 minutes for script execution

class QuizSolver:
    """Manages the quiz solving workflow"""
    
    def __init__(self, email: str, secret: str):
        self.email = email
        self.secret = secret
        self.ai_pipe_token = os.getenv("AI_PIPE_TOKEN")
        if not self.ai_pipe_token:
            raise ValueError("AI_PIPE_TOKEN not found in environment")
        
        self.scraper = QuizScraper()
        self.start_time = time.time()
    
    def _check_time_limit(self) -> bool:
        """Check if we're still within the 3-minute time limit"""
        elapsed = time.time() - self.start_time
        remaining = MAX_TOTAL_TIME - elapsed
        if remaining <= 0:
            logger.error("Time limit exceeded!")
            return False
        logger.info(f"Time remaining: {remaining:.1f} seconds")
        return True
    
    async def call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = 4000
    ) -> Optional[str]:
        """
        Call AI Pipe API to get LLM response
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            model: Model to use
            max_tokens: Maximum tokens in response
            
        Returns:
            LLM response text or None if failed
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.ai_pipe_token}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            logger.info(f"Calling AI Pipe API with model: {model}")
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    AI_PIPE_API_URL,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                logger.info(f"LLM response received ({len(content)} chars)")
                return content
                
        except Exception as e:
            logger.error(f"Error calling LLM with model {model}: {e}")
            return None
    
    def execute_script(self, script_path: str) -> tuple[bool, str]:
        """
        Execute the generated Python script
        
        Args:
            script_path: Path to the script file
            
        Returns:
            Tuple of (success, output/error)
        """
        try:
            # Prepare environment with all necessary tokens
            env = os.environ.copy()
            env["AI_PIPE_TOKEN"] = self.ai_pipe_token
            env["EMAIL"] = self.email
            env["SECRET_KEY"] = self.secret
            
            logger.info(f"Executing script: {script_path}")
            result = subprocess.run(
                ["python3", script_path],
                capture_output=True,
                text=True,
                timeout=SCRIPT_TIMEOUT,
                env=env
            )
            
            if result.returncode == 0:
                logger.info("Script executed successfully")
                logger.info(f"Script output: {result.stdout}")
                return True, result.stdout
            else:
                logger.error(f"Script failed with return code {result.returncode}")
                logger.error(f"Script stderr: {result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            logger.error(f"Script execution timed out after {SCRIPT_TIMEOUT}s")
            return False, "Script execution timeout"
        except Exception as e:
            logger.error(f"Error executing script: {e}")
            return False, str(e)
    
    async def solve_quiz_chain(self, initial_url: str):
        """
        Solve a chain of quizzes starting from the initial URL
        
        Args:
            initial_url: First quiz URL to solve
        """
        current_url = initial_url
        quiz_count = 0
        
        while current_url and self._check_time_limit():
            quiz_count += 1
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing Quiz #{quiz_count}: {current_url}")
            logger.info(f"{'='*60}\n")
            
            try:
                # Step 1: Scrape the quiz page
                logger.info("Step 1: Scraping quiz page...")
                quiz_content = await self.scraper.fetch_quiz_content(current_url)
                
                if not quiz_content or not quiz_content.get("question"):
                    logger.error("Failed to extract quiz question")
                    break
                
                logger.info(f"Question extracted: {quiz_content['question'][:200]}...")
                
                # Step 2: Generate solving script using LLM
                logger.info("Step 2: Generating solution script with LLM...")
                script_prompt = get_script_generation_prompt(
                    question=quiz_content["question"],
                    quiz_url=current_url,
                    submit_url=quiz_content.get("submit_url", ""),
                    email=self.email,
                    secret=self.secret
                )
                
                # Try primary model first
                script_code = await self.call_llm(script_prompt, model=DEFAULT_MODEL)
                
                # Try fallback models if primary fails
                if not script_code:
                    for fallback_model in FALLBACK_MODELS:
                        logger.warning(f"Trying fallback model: {fallback_model}")
                        script_code = await self.call_llm(script_prompt, model=fallback_model)
                        if script_code:
                            break
                
                if not script_code:
                    logger.error("Failed to generate script with all models")
                    break
                
                # Extract Python code from markdown if needed
                if "```python" in script_code:
                    script_code = script_code.split("```python")[1].split("```")[0].strip()
                elif "```" in script_code:
                    script_code = script_code.split("```")[1].split("```")[0].strip()
                
                # Step 3: Save and execute the script
                logger.info("Step 3: Executing generated script...")
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix='.py',
                    delete=False,
                    dir='/tmp'
                ) as f:
                    f.write(script_code)
                    script_path = f.name
                
                try:
                    success, output = self.execute_script(script_path)
                    
                    if success:
                        logger.info(f"Quiz #{quiz_count} solved successfully!")
                        # Parse output for next URL
                        # The script should print the next URL if available
                        if "url" in output.lower() and "http" in output:
                            # Extract next URL from output
                            lines = output.split('\n')
                            for line in lines:
                                if "next" in line.lower() and "http" in line:
                                    # Simple extraction, can be improved
                                    import re
                                    urls = re.findall(r'https?://[^\s<>"]+', line)
                                    if urls:
                                        current_url = urls[0]
                                        logger.info(f"Found next URL: {current_url}")
                                        break
                            else:
                                current_url = None
                        else:
                            logger.info("No next URL found. Quiz chain complete!")
                            current_url = None
                    else:
                        logger.error(f"Quiz #{quiz_count} failed: {output}")
                        break
                        
                finally:
                    # Clean up script file
                    try:
                        os.unlink(script_path)
                    except:
                        pass
                        
            except Exception as e:
                logger.error(f"Error processing quiz #{quiz_count}: {e}", exc_info=True)
                break
        
        total_time = time.time() - self.start_time
        logger.info(f"\n{'='*60}")
        logger.info(f"Quiz solving completed!")
        logger.info(f"Total quizzes processed: {quiz_count}")
        logger.info(f"Total time: {total_time:.1f} seconds")
        logger.info(f"{'='*60}\n")

def solve_quiz_task(email: str, secret: str, url: str):
    """
    Background task to solve quiz
    This function is called by FastAPI's BackgroundTasks
    """
    import asyncio
    
    try:
        logger.info(f"Starting quiz solver for {email}")
        solver = QuizSolver(email=email, secret=secret)
        asyncio.run(solver.solve_quiz_chain(url))
        logger.info("Quiz solver completed successfully")
    except Exception as e:
        logger.error(f"Fatal error in quiz solver: {e}", exc_info=True)
