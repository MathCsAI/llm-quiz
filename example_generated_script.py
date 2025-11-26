"""
Example of a generated script that the LLM might create to solve a quiz

This is what the AI Pipe LLM generates after analyzing the quiz content.
The script is then executed with environment variables to solve the quiz.
"""

import os
import httpx
import pandas as pd
import json
from io import BytesIO

# Get credentials from environment
EMAIL = os.getenv("EMAIL")
SECRET = os.getenv("SECRET")
AI_PIPE_TOKEN = os.getenv("AI_PIPE_TOKEN")

# Quiz information
QUIZ_URL = "https://example.com/quiz-834"
SUBMIT_URL = "https://example.com/submit"

print(f"Solving quiz: {QUIZ_URL}")

# Step 1: Download the data file mentioned in quiz
print("Step 1: Downloading data file...")
data_url = "https://example.com/data-q834.pdf"

response = httpx.get(data_url, timeout=30.0)
response.raise_for_status()

# Step 2: Parse the PDF to extract table from page 2
print("Step 2: Extracting data from PDF page 2...")

# Using PyPDF2 or similar to extract text
# For this example, let's assume we extracted the data and it's in CSV format
# In real scenario, this would involve PDF parsing

# Simulated data extraction
data = """
item,value
A,100
B,200
C,300
D,400
E,500
"""

# Step 3: Load data into pandas
print("Step 3: Analyzing data...")
df = pd.read_csv(BytesIO(data.encode()))

# Step 4: Calculate the sum of the "value" column
answer = df['value'].sum()
print(f"Calculated answer: {answer}")

# Step 5: Submit the answer
print("Step 5: Submitting answer...")

payload = {
    "email": EMAIL,
    "secret": SECRET,
    "url": QUIZ_URL,
    "answer": int(answer)  # Ensure it's the right type
}

submit_response = httpx.post(
    SUBMIT_URL,
    json=payload,
    headers={"Content-Type": "application/json"},
    timeout=30.0
)

submit_response.raise_for_status()
result = submit_response.json()

print(f"Submission result: {json.dumps(result, indent=2)}")

# Step 6: Check for next quiz
if result.get("correct"):
    print("✓ Answer was correct!")
    
    if "url" in result:
        next_url = result["url"]
        print(f"Next quiz URL: {next_url}")
        print("Note: The main solver will handle the next quiz")
    else:
        print("Quiz chain completed!")
else:
    print("✗ Answer was incorrect")
    if "reason" in result:
        print(f"Reason: {result['reason']}")
