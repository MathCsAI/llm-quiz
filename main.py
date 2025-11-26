"""
FastAPI server for LLM Quiz Application
Receives quiz tasks, validates requests, and solves them in the background
"""
import os
import logging
from typing import Dict, Any
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv

from quiz_solver import solve_quiz_task

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LLM Quiz Solver API",
    description="API endpoint that receives and solves quiz tasks using LLMs",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("=" * 60)
    logger.info("LLM Quiz Solver API Starting...")
    logger.info(f"Port: {os.getenv('PORT', '8000')}")
    logger.info(f"Email configured: {bool(EMAIL)}")
    logger.info(f"Secret configured: {bool(SECRET_KEY)}")
    logger.info("=" * 60)

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
EMAIL = os.getenv("EMAIL")

if not SECRET_KEY:
    logger.warning("SECRET_KEY not set in environment variables")
if not EMAIL:
    logger.warning("EMAIL not set in environment variables")


class QuizRequest(BaseModel):
    """Request model for quiz tasks"""
    email: str
    secret: str
    url: str


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "LLM Quiz Solver API is running",
        "email_configured": bool(EMAIL),
        "secret_configured": bool(SECRET_KEY)
    }


@app.post("/receive_request")
async def receive_quiz_request(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Main endpoint to receive quiz tasks
    
    Validates:
    - JSON format (400 if invalid)
    - Secret key (403 if invalid)
    
    Returns 200 immediately and processes quiz in background
    """
    try:
        # Parse JSON body
        try:
            body = await request.json()
        except Exception as e:
            logger.error(f"Invalid JSON received: {e}")
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON payload"
            )
        
        # Validate request structure
        try:
            quiz_request = QuizRequest(**body)
        except ValidationError as e:
            logger.error(f"Invalid request structure: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid request structure: {str(e)}"
            )
        
        # Verify secret
        if quiz_request.secret != SECRET_KEY:
            logger.warning(f"Invalid secret provided for {quiz_request.email}")
            raise HTTPException(
                status_code=403,
                detail="Invalid secret key"
            )
        
        # Verify email matches
        if quiz_request.email != EMAIL:
            logger.warning(f"Email mismatch: {quiz_request.email} != {EMAIL}")
            raise HTTPException(
                status_code=403,
                detail="Email does not match configured email"
            )
        
        logger.info(f"Valid request received for URL: {quiz_request.url}")
        
        # Add quiz solving to background tasks
        background_tasks.add_task(
            solve_quiz_task,
            email=quiz_request.email,
            secret=quiz_request.secret,
            url=quiz_request.url
        )
        
        # Return immediate 200 response
        return JSONResponse(
            status_code=200,
            content={
                "status": "accepted",
                "message": "Quiz task accepted and processing in background",
                "url": quiz_request.url
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    """Alternative endpoint name for quiz requests"""
    return await receive_quiz_request(request, background_tasks)


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
