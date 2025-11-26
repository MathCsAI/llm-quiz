"""
Test script for the quiz endpoint
"""
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
EMAIL = os.getenv("EMAIL", "your_email@example.com")
SECRET = os.getenv("SECRET_KEY", "your_secret")
ENDPOINT_URL = "http://localhost:8000/receive_request"  # Change to your deployed URL

# Test URLs
DEMO_URL = "https://tds-llm-analysis.s-anand.net/demo"


def test_valid_request():
    """Test with valid credentials"""
    print("Testing valid request...")
    
    payload = {
        "email": EMAIL,
        "secret": SECRET,
        "url": DEMO_URL
    }
    
    try:
        response = httpx.post(ENDPOINT_URL, json=payload, timeout=10.0)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Valid request test passed!\n")
        
    except Exception as e:
        print(f"✗ Valid request test failed: {e}\n")


def test_invalid_json():
    """Test with invalid JSON"""
    print("Testing invalid JSON...")
    
    try:
        response = httpx.post(
            ENDPOINT_URL, 
            data="not a json",
            headers={"Content-Type": "application/json"},
            timeout=10.0
        )
        print(f"Status Code: {response.status_code}")
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Invalid JSON test passed!\n")
        
    except Exception as e:
        print(f"✗ Invalid JSON test failed: {e}\n")


def test_invalid_secret():
    """Test with invalid secret"""
    print("Testing invalid secret...")
    
    payload = {
        "email": EMAIL,
        "secret": "wrong_secret",
        "url": DEMO_URL
    }
    
    try:
        response = httpx.post(ENDPOINT_URL, json=payload, timeout=10.0)
        print(f"Status Code: {response.status_code}")
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Invalid secret test passed!\n")
        
    except Exception as e:
        print(f"✗ Invalid secret test failed: {e}\n")


def test_missing_fields():
    """Test with missing required fields"""
    print("Testing missing fields...")
    
    payload = {
        "email": EMAIL
        # Missing secret and url
    }
    
    try:
        response = httpx.post(ENDPOINT_URL, json=payload, timeout=10.0)
        print(f"Status Code: {response.status_code}")
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Missing fields test passed!\n")
        
    except Exception as e:
        print(f"✗ Missing fields test failed: {e}\n")


def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    
    try:
        response = httpx.get("http://localhost:8000/", timeout=10.0)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Health check test passed!\n")
        
    except Exception as e:
        print(f"✗ Health check test failed: {e}\n")


if __name__ == "__main__":
    print("="*60)
    print("QUIZ ENDPOINT TEST SUITE")
    print("="*60)
    print()
    
    print(f"Testing endpoint: {ENDPOINT_URL}")
    print(f"Email: {EMAIL}")
    print(f"Secret: {'*' * len(SECRET) if SECRET else 'NOT SET'}")
    print()
    
    # Run tests
    test_health_check()
    test_invalid_json()
    test_missing_fields()
    test_invalid_secret()
    test_valid_request()
    
    print("="*60)
    print("TEST SUITE COMPLETED")
    print("="*60)
