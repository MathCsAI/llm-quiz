#!/usr/bin/env python3
"""
Test the demo quiz endpoint to ensure our system works correctly
"""
import httpx
import json
import asyncio
import sys


EMAIL = "23f2003858@ds.study.iitm.ac.in"
SECRET = "12356789"
DEMO_URL = "https://tds-llm-analysis.s-anand.net/demo"


async def test_local_endpoint():
    """Test our local /receive_request endpoint"""
    print("=" * 80)
    print("TEST 1: Local Endpoint Validation")
    print("=" * 80)
    print()
    
    # Test 1: Valid request (should return 200)
    print("1.1 Testing valid request...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:7860/receive_request",
                json={
                    "email": EMAIL,
                    "secret": SECRET,
                    "url": DEMO_URL
                },
                timeout=10.0
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            assert response.status_code == 200, "Should return 200 for valid request"
            print("   ✅ PASS")
    except httpx.ConnectError:
        print("   ⚠️  SKIP - Server not running locally")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
    print()
    
    # Test 2: Invalid secret (should return 403)
    print("1.2 Testing invalid secret...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:7860/receive_request",
                json={
                    "email": EMAIL,
                    "secret": "wrong_secret",
                    "url": DEMO_URL
                },
                timeout=10.0
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            assert response.status_code == 403, "Should return 403 for invalid secret"
            print("   ✅ PASS")
    except httpx.ConnectError:
        print("   ⚠️  SKIP - Server not running locally")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
    print()
    
    # Test 3: Invalid JSON (should return 400)
    print("1.3 Testing missing fields...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:7860/receive_request",
                json={
                    "email": EMAIL
                    # Missing secret and url
                },
                timeout=10.0
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            assert response.status_code == 422, "Should return 422 for missing fields"
            print("   ✅ PASS")
    except httpx.ConnectError:
        print("   ⚠️  SKIP - Server not running locally")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
    print()


async def test_demo_quiz():
    """Test the actual demo quiz endpoint"""
    print("=" * 80)
    print("TEST 2: Demo Quiz Endpoint")
    print("=" * 80)
    print()
    
    print("Sending POST request to demo endpoint...")
    print(f"URL: {DEMO_URL}")
    print(f"Payload: {json.dumps({'email': EMAIL, 'secret': SECRET, 'url': DEMO_URL}, indent=2)}")
    print()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                DEMO_URL,
                json={
                    "email": EMAIL,
                    "secret": SECRET,
                    "url": DEMO_URL
                },
                timeout=30.0
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print()
            print("Response Body:")
            print(json.dumps(response.json(), indent=2))
            print()
            
            if response.status_code == 200:
                result = response.json()
                if result.get("correct") is not None:
                    print(f"✅ Demo endpoint responded correctly")
                    print(f"   Correct: {result.get('correct')}")
                    print(f"   Reason: {result.get('reason')}")
                    if result.get("url"):
                        print(f"   Next URL: {result.get('url')}")
                else:
                    print("⚠️  Unexpected response format")
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_our_endpoint_with_demo():
    """Test sending demo URL to our endpoint"""
    print("=" * 80)
    print("TEST 3: Our Endpoint Processing Demo Quiz")
    print("=" * 80)
    print()
    
    # First, check if our endpoint is available
    endpoint_url = None
    
    # Try HF Space
    if len(sys.argv) > 1:
        endpoint_url = f"{sys.argv[1]}/receive_request"
    else:
        # Try local
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:7860/", timeout=5.0)
                if response.status_code == 200:
                    endpoint_url = "http://localhost:7860/receive_request"
        except:
            pass
    
    if not endpoint_url:
        print("⚠️  No endpoint URL provided. Skipping this test.")
        print("   Usage: python3 test_demo.py [HF_SPACE_URL]")
        return
    
    print(f"Testing endpoint: {endpoint_url}")
    print(f"Sending demo quiz to our solver...")
    print()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint_url,
                json={
                    "email": EMAIL,
                    "secret": SECRET,
                    "url": DEMO_URL
                },
                timeout=10.0
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            print()
            
            if response.status_code == 200:
                print("✅ Our endpoint accepted the demo quiz!")
                print()
                print("Now wait 2-3 minutes for background processing...")
                print("The solver will:")
                print("  1. Visit the demo URL with Playwright")
                print("  2. Extract the quiz question")
                print("  3. Generate a Python script using LLM")
                print("  4. Execute the script")
                print("  5. Submit the answer")
                print()
                print("Check server logs to see the processing status.")
            else:
                print(f"❌ Unexpected response: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all demo tests"""
    print("\n")
    print("=" * 80)
    print("          DEMO QUIZ TESTING")
    print("=" * 80)
    print()
    
    # Test local endpoint validation
    await test_local_endpoint()
    
    # Test demo quiz endpoint directly
    await test_demo_quiz()
    
    # Test our endpoint with demo quiz
    await test_our_endpoint_with_demo()
    
    print("=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)
    print()


if __name__ == "__main__":
    asyncio.run(main())
