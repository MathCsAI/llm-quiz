#!/bin/bash

# Start the FastAPI server

echo "Starting LLM Quiz Solver API..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
