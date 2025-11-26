"""
FastAPI application for LLM Quiz Solver
Receives quiz tasks via POST endpoint and solves them using LLM-generated scripts
"""
import os
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, HttpUrl
import logging

from quiz_solver import solve_quiz_task

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LLM Quiz Solver API",
    description="Automated quiz solving using LLM-generated scripts",
    version="1.0.0"
)

# Request model
class QuizRequest(BaseModel):
    email: EmailStr
    secret: str
    url: HttpUrl

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "message": "LLM Quiz Solver API is operational",
        "endpoints": {
            "POST /receive_request": "Submit a quiz task"
        }
    }

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
            raise HTTPException(status_code=400, detail="Missing required fields: email, secret, url")
        
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
