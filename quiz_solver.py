"""
Quiz solving engine - orchestrates the entire quiz solving process
"""
import os
import sys
import json
import logging
import asyncio
import httpx
import subprocess
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

from scraper import fetch_quiz_sync
from prompts import get_script_generation_prompt, get_aipipe_request

logger = logging.getLogger(__name__)

# Configuration
AI_PIPE_TOKEN = os.getenv("AI_PIPE_TOKEN")
AI_PIPE_URL = "https://aipipe.ai/api/v1/chat/completions"
SCRIPT_TIMEOUT = 150  # 2.5 minutes (leaving 30s buffer from 3min limit)
MAX_RETRIES = 2
DEFAULT_MODEL = "gpt-4o-mini"  # Fast and cost-effective


class QuizSolver:
    """Main quiz solving orchestrator"""
    
    def __init__(self, email: str, secret: str):
        self.email = email
        self.secret = secret
        self.start_time = datetime.now()
        self.time_limit = timedelta(minutes=3)
        
        if not AI_PIPE_TOKEN:
            logger.error("AI_PIPE_TOKEN not set in environment")
            raise ValueError("AI_PIPE_TOKEN is required")
    
    def _check_time_limit(self) -> bool:
        """Check if we're within the 3-minute time limit"""
        elapsed = datetime.now() - self.start_time
        remaining = self.time_limit - elapsed
        
        if remaining.total_seconds() <= 0:
            logger.warning("Time limit exceeded!")
            return False
        
        logger.info(f"Time remaining: {remaining.total_seconds():.1f}s")
        return True
    
    async def call_llm(self, prompt: str, model: str = DEFAULT_MODEL) -> str:
        """
        Call AI Pipe API to get LLM response
        
        Args:
            prompt: The prompt to send
            model: Model to use
        
        Returns:
            LLM response text
        """
        try:
            headers = {
                "Authorization": f"Bearer {AI_PIPE_TOKEN}",
                "Content-Type": "application/json"
            }
            
            payload = get_aipipe_request(prompt, model=model, max_tokens=4000)
            
            logger.info(f"Calling AI Pipe API with model: {model}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    AI_PIPE_URL,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                logger.info(f"Received response from AI Pipe ({len(content)} chars)")
                return content
                
        except Exception as e:
            logger.error(f"Error calling AI Pipe API: {e}", exc_info=True)
            raise
    
    def extract_code_from_response(self, response: str) -> str:
        """
        Extract Python code from LLM response
        
        Args:
            response: LLM response that may contain code blocks
        
        Returns:
            Extracted Python code
        """
        # Look for code blocks
        if "```python" in response:
            # Extract code between ```python and ```
            start = response.find("```python") + 9
            end = response.find("```", start)
            code = response[start:end].strip()
        elif "```" in response:
            # Generic code block
            start = response.find("```") + 3
            end = response.find("```", start)
            code = response[start:end].strip()
        else:
            # No code blocks, assume entire response is code
            code = response.strip()
        
        return code
    
    async def generate_and_execute_script(
        self, 
        quiz_content: Dict[str, Any],
        retry_count: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a Python script using LLM and execute it
        
        Args:
            quiz_content: Parsed quiz content
            retry_count: Current retry attempt
        
        Returns:
            Execution result or None if failed
        """
        try:
            if not self._check_time_limit():
                return None
            
            # Prepare quiz content for prompt
            quiz_text = quiz_content.get('text', '')
            
            # Include decoded base64 content if available
            if quiz_content.get('base64_content'):
                for b64_item in quiz_content['base64_content']:
                    quiz_text += "\n\n[DECODED CONTENT]:\n" + b64_item['decoded']
            
            # Get submit URL
            submit_url = quiz_content.get('submit_url') or f"{quiz_content['url']}/submit"
            
            logger.info(f"Generating script for quiz (attempt {retry_count + 1})")
            
            # Generate prompt
            prompt = get_script_generation_prompt(
                quiz_content=quiz_text,
                quiz_url=quiz_content['url'],
                submit_url=submit_url,
                email=self.email,
                secret=self.secret
            )
            
            # Call LLM to generate script
            llm_response = await self.call_llm(prompt, model=DEFAULT_MODEL)
            
            # Extract code
            script_code = self.extract_code_from_response(llm_response)
            
            logger.info(f"Generated script ({len(script_code)} chars)")
            
            # Save script to file
            script_path = Path("generated_script.py")
            with open(script_path, "w") as f:
                f.write(script_code)
            
            logger.info(f"Saved script to {script_path}")
            
            # Execute script
            result = await self.execute_script(script_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating/executing script: {e}", exc_info=True)
            if retry_count < MAX_RETRIES:
                logger.info(f"Retrying... (attempt {retry_count + 2})")
                return await self.generate_and_execute_script(quiz_content, retry_count + 1)
            return None
    
    async def execute_script(self, script_path: Path) -> Dict[str, Any]:
        """
        Execute generated Python script
        
        Args:
            script_path: Path to script file
        
        Returns:
            Execution result
        """
        try:
            logger.info(f"Executing script: {script_path}")
            
            # Prepare environment with necessary tokens
            env = os.environ.copy()
            env['AI_PIPE_TOKEN'] = AI_PIPE_TOKEN
            env['EMAIL'] = self.email
            env['SECRET'] = self.secret
            
            # Execute script with timeout
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=SCRIPT_TIMEOUT
                )
                
                stdout_text = stdout.decode('utf-8', errors='replace')
                stderr_text = stderr.decode('utf-8', errors='replace')
                
                logger.info(f"Script execution completed with return code: {process.returncode}")
                
                if stdout_text:
                    logger.info(f"Script output:\n{stdout_text}")
                if stderr_text:
                    logger.warning(f"Script errors:\n{stderr_text}")
                
                return {
                    'success': process.returncode == 0,
                    'stdout': stdout_text,
                    'stderr': stderr_text,
                    'return_code': process.returncode
                }
                
            except asyncio.TimeoutError:
                logger.error(f"Script execution timed out after {SCRIPT_TIMEOUT}s")
                process.kill()
                return {
                    'success': False,
                    'error': 'Script execution timeout'
                }
                
        except Exception as e:
            logger.error(f"Error executing script: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    async def solve_quiz_chain(self, initial_url: str):
        """
        Solve a chain of quizzes starting from initial URL
        
        Args:
            initial_url: The first quiz URL
        """
        current_url = initial_url
        quiz_count = 0
        max_quizzes = 10  # Safety limit
        
        while current_url and quiz_count < max_quizzes:
            if not self._check_time_limit():
                logger.warning("Time limit reached, stopping quiz chain")
                break
            
            quiz_count += 1
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing quiz #{quiz_count}: {current_url}")
            logger.info(f"{'='*60}\n")
            
            try:
                # Fetch quiz content
                quiz_content = fetch_quiz_sync(current_url)
                
                # Generate and execute solution script
                result = await self.generate_and_execute_script(quiz_content)
                
                if not result or not result.get('success'):
                    logger.error(f"Failed to solve quiz at {current_url}")
                    break
                
                # Check output for next URL or completion message
                output = result.get('stdout', '')
                
                # Look for next URL in output
                import re
                next_url_match = re.search(r'"url":\s*"(https?://[^"]+)"', output)
                if next_url_match:
                    current_url = next_url_match.group(1)
                    logger.info(f"Moving to next quiz: {current_url}")
                else:
                    logger.info("No next URL found - quiz chain completed!")
                    break
                    
            except Exception as e:
                logger.error(f"Error solving quiz {current_url}: {e}", exc_info=True)
                break
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Quiz solving completed! Solved {quiz_count} quiz(es)")
        logger.info(f"Total time: {(datetime.now() - self.start_time).total_seconds():.1f}s")
        logger.info(f"{'='*60}\n")


def solve_quiz_task(email: str, secret: str, url: str):
    """
    Main entry point for solving quiz task (called from background task)
    
    Args:
        email: User email
        secret: User secret
        url: Quiz URL to solve
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Starting quiz solver for: {url}")
    logger.info(f"{'='*60}\n")
    
    try:
        solver = QuizSolver(email=email, secret=secret)
        asyncio.run(solver.solve_quiz_chain(url))
    except Exception as e:
        logger.error(f"Fatal error in quiz solver: {e}", exc_info=True)


if __name__ == "__main__":
    # For testing
    import sys
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        test_email = os.getenv("EMAIL", "test@example.com")
        test_secret = os.getenv("SECRET_KEY", "test_secret")
        
        solve_quiz_task(test_email, test_secret, test_url)
    else:
        print("Usage: python quiz_solver.py <quiz_url>")
