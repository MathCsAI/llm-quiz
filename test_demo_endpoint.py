#!/usr/bin/env python3
"""
Test the demo endpoint to verify the quiz-solving flow works correctly.

This simulates the actual evaluation:
1. POST to our /receive_request endpoint with demo URL
2. Our solver visits the demo page, extracts the question
3. Generates a Python script to solve it
4. Executes the script and submits the answer
5. Handles sequential quizzes if provided
"""

import asyncio
import httpx
import json
import time

# Configuration
LOCAL_ENDPOINT = "http://localhost:7860/receive_request"
HF_ENDPOINT = None  # Will be set if testing HF deployment

EMAIL = "23f2003858@ds.study.iitm.ac.in"
SECRET = "12356789"
DEMO_URL = "https://tds-llm-analysis.s-anand.net/demo"


async def test_demo_endpoint(endpoint_url: str):
    """Test the demo endpoint flow."""
    
    print("=" * 80)
    print("DEMO ENDPOINT TEST - Quiz Solving Flow")
    print("=" * 80)
    print()
    
    print(f"📋 Configuration:")
    print(f"   Endpoint: {endpoint_url}")
    print(f"   Email: {EMAIL}")
    print(f"   Secret: {SECRET}")
    print(f"   Demo URL: {DEMO_URL}")
    print()
    
    payload = {
        "email": EMAIL,
        "secret": SECRET,
        "url": DEMO_URL
    }
    
    print("📤 Sending POST request to /receive_request...")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            start_time = time.time()
            
            response = await client.post(
                endpoint_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            elapsed = time.time() - start_time
            
            print(f"📥 Response received in {elapsed:.2f}s")
            print(f"   Status Code: {response.status_code}")
            print()
            
            if response.status_code == 200:
                print("✅ Request accepted! Background task started.")
                response_data = response.json()
                print(f"   Response: {json.dumps(response_data, indent=2)}")
                print()
                
                print("⏳ Quiz solving in progress...")
                print("   This may take up to 3 minutes per quiz question.")
                print()
                print("📋 What happens next:")
                print("   1. Solver visits demo page with Playwright")
                print("   2. Extracts quiz question from JavaScript-rendered HTML")
                print("   3. LLM generates Python script to solve the quiz")
                print("   4. Executes script and captures the answer")
                print("   5. Submits answer to the specified endpoint")
                print("   6. If response includes next URL, continues to next quiz")
                print()
                print("💡 Check server logs to see the solving process:")
                print("   - Local: Check terminal where app is running")
                print("   - HF: Check Space logs in HF dashboard")
                
                return True
                
            elif response.status_code == 403:
                print("🚨 FAILED - Invalid secret")
                print(f"   Response: {response.text}")
                return False
                
            elif response.status_code == 400:
                print("🚨 FAILED - Invalid request format")
                print(f"   Response: {response.text}")
                return False
                
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except httpx.TimeoutException:
        print("❌ Request timed out")
        print("   Note: The request should return immediately (200 OK)")
        print("   Quiz solving happens in background, not blocking the response")
        return False
        
    except httpx.ConnectError:
        print("❌ Connection failed")
        print(f"   Could not connect to {endpoint_url}")
        print()
        print("💡 Is the server running?")
        print("   Local: uvicorn app:app --host 0.0.0.0 --port 7860")
        print("   HF: Check Space status on Hugging Face")
        return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_invalid_secret(endpoint_url: str):
    """Test that invalid secrets are rejected."""
    
    print("\n" + "=" * 80)
    print("SECURITY TEST - Invalid Secret Rejection")
    print("=" * 80)
    print()
    
    payload = {
        "email": EMAIL,
        "secret": "wrong_secret",
        "url": DEMO_URL
    }
    
    print("📤 Testing with invalid secret...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                endpoint_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 403:
                print("✅ PASS - Invalid secret correctly rejected (403)")
                return True
            else:
                print(f"🚨 FAIL - Expected 403, got {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_invalid_json(endpoint_url: str):
    """Test that invalid JSON is rejected."""
    
    print("\n" + "=" * 80)
    print("VALIDATION TEST - Invalid JSON Rejection")
    print("=" * 80)
    print()
    
    # Missing required field
    payload = {
        "email": EMAIL,
        "secret": SECRET
        # Missing "url"
    }
    
    print("📤 Testing with missing 'url' field...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                endpoint_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 400 or response.status_code == 422:
                print(f"✅ PASS - Invalid JSON correctly rejected ({response.status_code})")
                return True
            else:
                print(f"🚨 FAIL - Expected 400/422, got {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def main():
    """Run all demo endpoint tests."""
    
    print("Starting Demo Endpoint Tests...")
    print()
    
    # Determine which endpoint to test
    endpoint = LOCAL_ENDPOINT
    
    print("🎯 Testing local endpoint")
    print("   Make sure the server is running:")
    print("   uvicorn app:app --host 0.0.0.0 --port 7860")
    print()
    input("Press Enter when server is ready...")
    print()
    
    # Run tests
    results = []
    
    # Test 1: Valid demo request
    result1 = await test_demo_endpoint(endpoint)
    results.append(("Demo Quiz Flow", result1))
    
    # Test 2: Invalid secret
    result2 = await test_invalid_secret(endpoint)
    results.append(("Invalid Secret", result2))
    
    # Test 3: Invalid JSON
    result3 = await test_invalid_json(endpoint)
    results.append(("Invalid JSON", result3))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    print()
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("✅ Your endpoint is ready for evaluation!")
        print()
        print("Next steps:")
        print("1. Deploy to Hugging Face Spaces")
        print("2. Test with HF endpoint URL")
        print("3. Submit to evaluation form")
    else:
        print("⚠️  Some tests failed. Please fix issues before submission.")
    
    print()


if __name__ == "__main__":
    asyncio.run(main())
