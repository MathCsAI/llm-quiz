"""
FastAPI application for LLM Quiz Solver
Receives quiz tasks via POST endpoint and solves them using LLM-generated scripts
"""
import os
import asyncio
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, HttpUrl
import logging

from quiz_solver import solve_quiz_task, QuizSolver, DEFAULT_MODEL, GEMINI_API_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Request model
class QuizRequest(BaseModel):
    email: EmailStr
    secret: str
    url: HttpUrl

# Self-check configuration
SELF_TEST_DEMO_URL = os.getenv(
    "SELF_TEST_DEMO_URL",
    "https://tds-llm-analysis.s-anand.net/demo"
)
ENABLE_STARTUP_SELF_CHECK = os.getenv("ENABLE_STARTUP_SELF_CHECK", "true").lower() == "true"
ENABLE_PERIODIC_SELF_CHECKS = os.getenv("ENABLE_PERIODIC_SELF_CHECKS", "false").lower() == "true"
SELF_CHECK_INTERVAL_SECONDS = int(os.getenv("SELF_CHECK_INTERVAL_SECONDS", "900"))

async def _probe_gemini_models() -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    results = {"attempts": []}
    if not api_key:
        logger.warning("GEMINI_API_KEY not set; skipping models probe")
        results["skipped"] = True
        return results
    
    model_url = f"{GEMINI_API_URL}?key={api_key}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(model_url)
            results["attempts"].append({
                "url": model_url.split('?')[0],
                "status": resp.status_code,
                "ok": resp.status_code == 200
            })
        except Exception as e:
            results["attempts"].append({
                "url": GEMINI_API_URL,
                "error": str(e)
            })
    return results

async def run_self_check() -> dict:
    summary = {
        "health": "ok",
        "model": DEFAULT_MODEL,
        "gemini_api_url": GEMINI_API_URL,
    }
    # Probe models endpoint(s)
    models_probe = await _probe_gemini_models()
    logger.info(f"Gemini models probe: {models_probe}")
    summary["models_probe"] = models_probe
    # Try a minimal LLM call
    try:
        solver = QuizSolver(
            email=os.getenv("EMAIL", "test@example.com"),
            secret=os.getenv("SECRET_KEY", "secret")
        )
        content = await solver.call_llm("ping", model=DEFAULT_MODEL, max_tokens=10)
        if content:
            logger.info(f"Self-check LLM call succeeded: {len(content)} chars")
            summary["llm_call"] = {"ok": True, "len": len(content)}
        else:
            logger.warning("Self-check LLM call returned no content")
            summary["llm_call"] = {"ok": False}
    except Exception as e:
        logger.error(f"Self-check LLM call failed: {e}")
        summary["llm_call"] = {"ok": False, "error": str(e)}
    return summary

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    if ENABLE_STARTUP_SELF_CHECK:
        logger.info("Startup self-check enabled; running...")
        try:
            result = await run_self_check()
            logger.info(f"Startup self-check result: {result}")
        except Exception as e:
            logger.error(f"Startup self-check error: {e}")
    if ENABLE_PERIODIC_SELF_CHECKS:
        async def _loop():
            while True:
                try:
                    logger.info("Periodic self-check running...")
                    result = await run_self_check()
                    logger.info(f"Periodic self-check result: {result}")
                except Exception as e:
                    logger.error(f"Periodic self-check error: {e}")
                await asyncio.sleep(SELF_CHECK_INTERVAL_SECONDS)
        asyncio.create_task(_loop())
    
    yield
    
    # Shutdown (if needed in future)

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="LLM Quiz Solver API",
    description="Automated quiz solving using LLM-generated scripts",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root(run_self_check: bool = False, enqueue_demo: bool = False, background_tasks: BackgroundTasks = None):
    """Health check endpoint with optional self-check trigger"""
    if run_self_check:
        result = await self_check(background_tasks or BackgroundTasks(), enqueue_demo=enqueue_demo)
        return result.body if isinstance(result, JSONResponse) else result
    return {
        "status": "running",
        "message": "LLM Quiz Solver API is operational",
        "endpoints": {
            "POST /receive_request": "Submit a quiz task"
        }
    }

@app.get("/self_check")
async def self_check(background_tasks: BackgroundTasks, enqueue_demo: bool = True):
    result = await run_self_check()
    if enqueue_demo:
        email = os.getenv("EMAIL")
        secret = os.getenv("SECRET_KEY")
        if email and secret and SELF_TEST_DEMO_URL:
            logger.info(f"Enqueuing demo quiz as part of self_check: {SELF_TEST_DEMO_URL}")
            background_tasks.add_task(
                solve_quiz_task,
                email=email,
                secret=secret,
                url=SELF_TEST_DEMO_URL
            )
            result["demo_enqueued"] = True
        else:
            result["demo_enqueued"] = False
    return JSONResponse(result)

@app.post("/receive_request")
async def receive_quiz_request(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Receive and process quiz tasks
    
    Returns:
        - 200: Request accepted and processing in background
        - 400: Invalid JSON payload
        - 403: Invalid secret key
    """
    try:
        # Parse JSON payload
        try:
            payload = await request.json()
        except Exception as e:
            logger.error(f"Invalid JSON payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Validate required fields
        if not all(key in payload for key in ["email", "secret", "url"]):
            logger.error("Missing required fields in payload")
            raise HTTPException(status_code=422, detail="Missing required fields: email, secret, url")
        
        # Verify secret
        expected_secret = os.getenv("SECRET_KEY")
        if not expected_secret:
            logger.error("SECRET_KEY not configured in environment")
            raise HTTPException(status_code=500, detail="Server configuration error")
        
        if payload["secret"] != expected_secret:
            logger.warning(f"Invalid secret attempt for email: {payload['email']}")
            raise HTTPException(status_code=403, detail="Invalid secret key")
        
        # Validate email matches expected
        expected_email = os.getenv("EMAIL")
        if expected_email and payload["email"] != expected_email:
            logger.warning(f"Email mismatch: {payload['email']} != {expected_email}")
            raise HTTPException(status_code=403, detail="Invalid email")
        
        # Start background task to solve quiz
        logger.info(f"Accepted quiz request for {payload['email']}: {payload['url']}")
        background_tasks.add_task(
            solve_quiz_task,
            email=payload["email"],
            secret=payload["secret"],
            url=str(payload["url"])
        )
        
        # Return immediate success response
        return JSONResponse(
            status_code=200,
            content={
                "status": "accepted",
                "message": "Quiz task received and processing in background",
                "email": payload["email"],
                "url": str(payload["url"])
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in receive_quiz_request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
