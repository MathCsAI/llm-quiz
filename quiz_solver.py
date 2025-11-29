"""
Quiz Solver Module
Orchestrates the quiz solving process using LLM-generated scripts
"""
import os
import time
import logging
import subprocess
import tempfile
import asyncio
from typing import Optional, Dict, Any
import httpx
from scraper import QuizScraper
from prompts import get_script_generation_prompt, SYSTEM_PROMPT_DEFENSE, USER_PROMPT_ATTACK

logger = logging.getLogger(__name__)

# Gemini API Configuration
GEMINI_API_URL = os.getenv("GEMINI_API_URL", "").strip() or "https://generativelanguage.googleapis.com/v1beta/models"
# Model configuration (override via env)
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
_fallback_env = os.getenv("GEMINI_FALLBACK_MODELS", "gemini-2.5-pro,gemini-3-pro-preview,gemini-2.0-flash-lite,gemini-2.0-flash,gemini-2.5-flash-lite").strip()
FALLBACK_MODELS = [m.strip() for m in _fallback_env.split(',') if m.strip()]

# Time limits
MAX_TOTAL_TIME = 180  # 3 minutes total
SCRIPT_TIMEOUT = 150  # 2.5 minutes for script execution

class QuizSolver:
    """Manages the quiz solving workflow"""
    
    def __init__(self, email: str, secret: str):
        self.email = email
        self.secret = secret
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
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
        model: Optional[str] = DEFAULT_MODEL,
        max_tokens: int = 4000
    ) -> Optional[str]:
        """
        Call Gemini API to get LLM response
        
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
                "Content-Type": "application/json"
            }
            
            # Build Gemini API request
            contents = []
            if system_prompt:
                contents.append({"role": "user", "parts": [{"text": system_prompt}]})
                contents.append({"role": "model", "parts": [{"text": "Understood."}]})
            contents.append({"role": "user", "parts": [{"text": prompt}]})
            
            payload = {
                "contents": contents,
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": 0.7
                }
            }
            
            api_url = f"{GEMINI_API_URL}/{model}:generateContent?key={self.gemini_api_key}"
            logger.info(f"Calling Gemini API with model: {model}")
            
            async with httpx.AsyncClient(timeout=90.0) as client:
                try:
                    response = await client.post(
                        api_url,
                        headers=headers,
                        json=payload
                    )
                except httpx.TimeoutException as e:
                    logger.error(f"Timeout contacting Gemini API: {e}")
                    return None
                except Exception as e:
                    logger.error(f"Network error contacting Gemini API: {type(e).__name__}: {e}")
                    return None

                logger.info(f"API Response Status: {response.status_code}")
                if response.status_code != 200:
                    logger.error(f"Gemini API Error: {response.status_code} - {response.text}")
                    return None

                result = response.json()

                # Basic structural validation
                candidates = result.get("candidates", []) or []
                if not candidates:
                    logger.error(f"Invalid Gemini API response (no candidates): {result}")
                    return None

                # Robust extraction of text parts
                def extract_text(r: Dict[str, Any]) -> Optional[str]:
                    try:
                        for cand in r.get("candidates", []):
                            content_obj = cand.get("content", {}) or {}
                            parts = content_obj.get("parts")
                            if isinstance(parts, list):
                                for part in parts:
                                    # Common field
                                    if isinstance(part, dict) and "text" in part and part["text"]:
                                        return part["text"]
                                    # Sometimes inlineData may appear (ignore for now unless no text)
                                    if isinstance(part, dict) and "inlineData" in part:
                                        data = part["inlineData"].get("data")
                                        if data:
                                            return data
                            # Fallback: if parts missing but content has direct text
                            if "text" in content_obj:
                                return content_obj.get("text")
                            # Some experimental responses may put text directly in candidate
                            if "output" in cand and isinstance(cand["output"], str):
                                return cand["output"]
                        return None
                    except Exception as e:  # noqa: BLE001
                        logger.error(f"Error extracting text from Gemini response: {type(e).__name__}: {e}")
                        return None

                content = extract_text(result)
                if not content:
                    logger.error(f"Unable to extract 'text' from Gemini response: {result}")
                    return None

                logger.info(f"LLM response received ({len(content)} chars)")
                return content
                
        except httpx.TimeoutException as e:
            logger.error(f"Timeout calling Gemini with model {model}: {e}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling Gemini with model {model}: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error calling Gemini with model {model}: {type(e).__name__} - {e}")
            import traceback
            logger.error(traceback.format_exc())
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
            env["GEMINI_API_KEY"] = self.gemini_api_key
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

                # Deterministic fallback for known demo patterns when LLM is unreachable
                if not script_code:
                    logger.warning("LLM generation failed; attempting deterministic fallback")
                    question_text = quiz_content.get("question", "")
                    if "window.location.origin" in question_text:
                        from urllib.parse import urlparse
                        parsed = urlparse(current_url)
                        origin = f"{parsed.scheme}://{parsed.netloc}"
                        script_code = (
                            "from urllib.parse import urlparse\n"
                            f"url = '{current_url}'\n"
                            "p = urlparse(url)\n"
                            "origin = f'{p.scheme}://{p.netloc}'\n"
                            "print('ANSWER:', origin)\n"
                        )
                        logger.info(f"Deterministic fallback applied. Computed origin: {origin}")
                    else:
                        logger.error("Failed to generate script with all models")
                        break
                
                # Extract Python code from markdown if needed
                if "```python" in script_code:
                    script_code = script_code.split("```python")[1].split("```")[0].strip()
                elif "```" in script_code:
                    script_code = script_code.split("```")[1].split("```")[0].strip()

                # Sanitize and validate generated script to reduce trivial syntax errors
                def sanitize_script(code: str) -> str:
                    cleaned = code.strip()
                    # Remove leading stray backticks
                    while cleaned.startswith("`"):
                        cleaned = cleaned[1:].lstrip()
                    lines = cleaned.splitlines()
                    # Heuristic fixes
                    fixed_lines = []
                    for line in lines:
                        s = line.strip()
                        # Remove bare identifiers that can break blocks (e.g., 'logging')
                        if s in {"logging"}:
                            continue
                        # Ensure except/finally have a trailing colon
                        if s.startswith("except") and not s.endswith(":"):
                            line = line.rstrip() + ":"
                        if s.startswith("finally") and not s.endswith(":"):
                            line = line.rstrip() + ":"
                        # Ensure logging format strings are closed if truncated
                        if "format=" in line and "%(message)" in line and line.count("'") % 2 == 1:
                            line = line + "'"
                        fixed_lines.append(line)
                    candidate = "\n".join(fixed_lines)
                    # Try compiling; on common SyntaxErrors, apply secondary fixes
                    import ast
                    try:
                        ast.parse(candidate)
                        return candidate
                    except SyntaxError as se:  # noqa: BLE001
                        msg = str(se)
                        # Attempt to fix missing colon in except/finally if not caught above
                        if "expected ':'" in msg:
                            tmp = []
                            for ln in fixed_lines:
                                st = ln.strip()
                                if (st.startswith("except") or st.startswith("finally")) and not st.endswith(":"):
                                    ln = ln.rstrip() + ":"
                                tmp.append(ln)
                            candidate2 = "\n".join(tmp)
                            try:
                                ast.parse(candidate2)
                                return candidate2
                            except Exception:
                                pass
                        # If still failing, return original code to preserve output
                        return code

                script_code = sanitize_script(script_code)
                
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
                        # Look for patterns like: NEXT_URL: <url>, "url": "<url>", or just URLs
                        import re
                        current_url = None
                        
                        # Try to find NEXT_URL: pattern first (most explicit)
                        next_url_match = re.search(r'NEXT_URL:\s*(https?://[^\s<>"]+)', output, re.IGNORECASE)
                        if next_url_match:
                            current_url = next_url_match.group(1)
                            logger.info(f"Found next URL (explicit): {current_url}")
                        else:
                            # Try to find "url": "..." pattern in JSON output
                            json_url_match = re.search(r'"url"\s*:\s*"(https?://[^"]+)"', output)
                            if json_url_match:
                                current_url = json_url_match.group(1)
                                logger.info(f"Found next URL (JSON): {current_url}")
                            else:
                                # Last resort: look for any line with "next" and a URL
                                lines = output.split('\n')
                                for line in lines:
                                    if "next" in line.lower() and "http" in line:
                                        urls = re.findall(r'https?://[^\s<>"]+', line)
                                        if urls:
                                            current_url = urls[0]
                                            logger.info(f"Found next URL (fallback): {current_url}")
                                            break
                        
                        if not current_url:
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
