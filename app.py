"""
Hugging Face Spaces entry point
This file is required for HF Spaces deployment
"""
import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure the application can find its modules
sys.path.insert(0, os.path.dirname(__file__))

logger.info("=" * 60)
logger.info("Starting HF Spaces app.py entry point...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"PORT environment: {os.getenv('PORT', '7860')}")
logger.info("=" * 60)

# Import the FastAPI app
from main import app

# HF Spaces will run this with uvicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "7860"))
    logger.info(f"Starting uvicorn server on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
