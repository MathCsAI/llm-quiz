"""
Test script for the quiz solver endpoint
"""
import httpx
import asyncio
import json

# Test configuration
API_URL = "http://localhost:7860/receive_request"
DEMO_URL = "https://tds-llm-analysis.s-anand.net/demo"

async def test_valid_request():
    """Test with valid credentials"""
    print("=" * 60)
    print("Test 1: Valid Request")
    print("=" * 60)
    
    payload = {
        "email": "test@example.com",
        "secret": "test-secret",
        "url": DEMO_URL
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(API_URL, json=payload)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                print("✓ Test PASSED: Got 200 response")
            else:
                print(f"✗ Test FAILED: Expected 200, got {response.status_code}")
        except Exception as e:
            print(f"✗ Test FAILED: {e}")
    
    print()

async def test_invalid_json():
    """Test with invalid JSON"""
    print("=" * 60)
    print("Test 2: Invalid JSON")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                API_URL,
                content="invalid json{",
                headers={"Content-Type": "application/json"}
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 400:
                print("✓ Test PASSED: Got 400 for invalid JSON")
            else:
                print(f"✗ Test FAILED: Expected 400, got {response.status_code}")
        except Exception as e:
            print(f"✗ Test FAILED: {e}")
    
    print()

async def test_invalid_secret():
    """Test with invalid secret"""
    print("=" * 60)
    print("Test 3: Invalid Secret")
    print("=" * 60)
    
    payload = {
        "email": "test@example.com",
        "secret": "wrong-secret",
        "url": DEMO_URL
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(API_URL, json=payload)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 403:
                print("✓ Test PASSED: Got 403 for invalid secret")
            else:
                print(f"✗ Test FAILED: Expected 403, got {response.status_code}")
        except Exception as e:
            print(f"✗ Test FAILED: {e}")
    
    print()

async def test_missing_fields():
    """Test with missing required fields"""
    print("=" * 60)
    print("Test 4: Missing Fields")
    print("=" * 60)
    
    payload = {
        "email": "test@example.com"
        # Missing secret and url
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(API_URL, json=payload)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 400:
                print("✓ Test PASSED: Got 400 for missing fields")
            else:
                print(f"✗ Test FAILED: Expected 400, got {response.status_code}")
        except Exception as e:
            print(f"✗ Test FAILED: {e}")
    
    print()

async def test_health_check():
    """Test health check endpoint"""
    print("=" * 60)
    print("Test 5: Health Check")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get("http://localhost:7860/")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                print("✓ Test PASSED: Server is running")
            else:
                print(f"✗ Test FAILED: Expected 200, got {response.status_code}")
        except Exception as e:
            print(f"✗ Test FAILED: {e}")
    
    print()

async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("LLM Quiz Solver - Endpoint Tests")
    print("=" * 60 + "\n")
    
    print("Make sure the server is running on http://localhost:7860\n")
    print("Update the test email and secret to match your .env file\n")
    
    input("Press Enter to start tests...")
    print()
    
    await test_health_check()
    await test_valid_request()
    await test_invalid_json()
    await test_invalid_secret()
    await test_missing_fields()
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
