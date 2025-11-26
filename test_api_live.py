#!/usr/bin/env python3
"""
Live API testing with actual HTTP calls to the running server.
Run this while the server is running: uvicorn app:app --host 0.0.0.0 --port 7860
"""

import requests
import json
import time

BASE_URL = "http://localhost:7860"
EMAIL = "23f2003858@ds.study.iitm.ac.in"
SECRET = "12356789"

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_result(test_name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"   {details}")

def test_health_check():
    """Test 1: Health check endpoint"""
    print_header("TEST 1: Health Check Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        passed = response.status_code == 200
        print_result("Health Check", passed, f"Endpoint responding")
        return passed
    except Exception as e:
        print_result("Health Check", False, f"Error: {str(e)}")
        return False

def test_invalid_secret():
    """Test 2: Invalid secret rejection"""
    print_header("TEST 2: Invalid Secret Rejection")
    
    payload = {
        "email": EMAIL,
        "secret": "wrong_secret",
        "url": "https://example.com/quiz"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/receive_request",
            json=payload,
            timeout=5
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        passed = response.status_code == 403
        print_result("Invalid Secret", passed, f"Expected 403, got {response.status_code}")
        return passed
    except Exception as e:
        print_result("Invalid Secret", False, f"Error: {str(e)}")
        return False

def test_missing_fields():
    """Test 3: Missing required fields"""
    print_header("TEST 3: Missing Required Fields")
    
    payload = {
        "email": EMAIL,
        "secret": SECRET
        # Missing "url"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/receive_request",
            json=payload,
            timeout=5
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        passed = response.status_code in [400, 422]
        print_result("Missing Fields", passed, f"Expected 400/422, got {response.status_code}")
        return passed
    except Exception as e:
        print_result("Missing Fields", False, f"Error: {str(e)}")
        return False

def test_valid_request():
    """Test 4: Valid request acceptance"""
    print_header("TEST 4: Valid Request Acceptance")
    
    payload = {
        "email": EMAIL,
        "secret": SECRET,
        "url": "https://example.com/test-quiz"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/receive_request",
            json=payload,
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        passed = response.status_code == 200
        print_result("Valid Request", passed, f"Request accepted, background task started")
        
        if passed:
            print("\n⏳ Note: Quiz solving is happening in background.")
            print("   Check server logs to see the progress.")
        
        return passed
    except Exception as e:
        print_result("Valid Request", False, f"Error: {str(e)}")
        return False

def test_concurrent_requests():
    """Test 5: Multiple concurrent requests"""
    print_header("TEST 5: Concurrent Requests Handling")
    
    payload = {
        "email": EMAIL,
        "secret": SECRET,
        "url": "https://example.com/quiz-{}"
    }
    
    try:
        results = []
        for i in range(3):
            test_payload = payload.copy()
            test_payload["url"] = payload["url"].format(i)
            
            response = requests.post(
                f"{BASE_URL}/receive_request",
                json=test_payload,
                timeout=5
            )
            results.append(response.status_code)
            print(f"Request {i+1}: {response.status_code}")
        
        passed = all(code == 200 for code in results)
        print_result("Concurrent Requests", passed, f"All {len(results)} requests accepted")
        return passed
    except Exception as e:
        print_result("Concurrent Requests", False, f"Error: {str(e)}")
        return False

def test_malformed_json():
    """Test 6: Malformed JSON handling"""
    print_header("TEST 6: Malformed JSON Handling")
    
    try:
        response = requests.post(
            f"{BASE_URL}/receive_request",
            data="not valid json",
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        passed = response.status_code == 422
        print_result("Malformed JSON", passed, f"Expected 422, got {response.status_code}")
        return passed
    except Exception as e:
        print_result("Malformed JSON", False, f"Error: {str(e)}")
        return False

def test_empty_fields():
    """Test 7: Empty field values"""
    print_header("TEST 7: Empty Field Values")
    
    payload = {
        "email": "",
        "secret": SECRET,
        "url": "https://example.com/quiz"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/receive_request",
            json=payload,
            timeout=5
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        passed = response.status_code in [400, 422]
        print_result("Empty Fields", passed, f"Expected 400/422, got {response.status_code}")
        return passed
    except Exception as e:
        print_result("Empty Fields", False, f"Error: {str(e)}")
        return False

def test_special_characters():
    """Test 8: Special characters in URL"""
    print_header("TEST 8: Special Characters in URL")
    
    payload = {
        "email": EMAIL,
        "secret": SECRET,
        "url": "https://example.com/quiz?id=123&type=test&data=hello%20world"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/receive_request",
            json=payload,
            timeout=5
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        passed = response.status_code == 200
        print_result("Special Characters", passed, f"URL with query params accepted")
        return passed
    except Exception as e:
        print_result("Special Characters", False, f"Error: {str(e)}")
        return False

def main():
    """Run all API tests"""
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "LIVE API TESTING - HTTP CALLS" + " " * 29 + "║")
    print("╚" + "=" * 78 + "╝")
    
    print("\n📋 Configuration:")
    print(f"   Base URL: {BASE_URL}")
    print(f"   Email: {EMAIL}")
    print(f"   Secret: {SECRET}")
    
    print("\n⚠️  Make sure server is running:")
    print("   uvicorn app:app --host 0.0.0.0 --port 7860")
    print("\n⏳ Starting tests in 2 seconds...")
    time.sleep(2)
    
    # Run all tests
    results = []
    
    results.append(("Health Check", test_health_check()))
    time.sleep(0.5)
    
    results.append(("Invalid Secret", test_invalid_secret()))
    time.sleep(0.5)
    
    results.append(("Missing Fields", test_missing_fields()))
    time.sleep(0.5)
    
    results.append(("Valid Request", test_valid_request()))
    time.sleep(0.5)
    
    results.append(("Concurrent Requests", test_concurrent_requests()))
    time.sleep(0.5)
    
    results.append(("Malformed JSON", test_malformed_json()))
    time.sleep(0.5)
    
    results.append(("Empty Fields", test_empty_fields()))
    time.sleep(0.5)
    
    results.append(("Special Characters", test_special_characters()))
    
    # Summary
    print("\n" + "=" * 80)
    print("  SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print()
    
    if passed == total:
        print("🎉 ALL API TESTS PASSED!")
        print("\n✅ Your API endpoint is working correctly!")
        print("\nNext steps:")
        print("  1. Deploy to Hugging Face Spaces")
        print("  2. Test with HF endpoint URL")
        print("  3. Submit to evaluation form")
    elif passed >= total * 0.8:
        print("👍 MOSTLY PASSING!")
        print("\nFix the failing tests above.")
    else:
        print("⚠️  MULTIPLE FAILURES!")
        print("\nPlease fix the issues before deployment.")
    
    print()
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
