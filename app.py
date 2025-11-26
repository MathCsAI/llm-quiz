"""
Hugging Face Spaces entry point
This file is required for HF Spaces deployment
"""
import sys
import os

# Ensure the application can find its modules
sys.path.insert(0, os.path.dirname(__file__))

# Import the FastAPI app
from main import app

# HF Spaces will run this with uvicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "7860"))  # HF Spaces uses port 7860
    uvicorn.run(app, host="0.0.0.0", port=port)
