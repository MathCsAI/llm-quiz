#!/usr/bin/env python3
"""
Comprehensive Robust Testing Suite
Tests all possible scenarios and validates complete workflow
"""
import asyncio
import httpx
import time
import json
from datetime import datetime

# Configuration
HF_ENDPOINT = "https://mathcsai-llm-quiz-solver.hf.space"
EMAIL = "23f2003858@ds.study.iitm.ac.in"
SECRET = "123456789"
DEMO_QUIZ_URL = "https://tds-llm-analysis.s-anand.net/demo"

class ComprehensiveTest:
    def __init__(self):
        self.results = []
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0
        
    def log_test(self, name: str, passed: bool, message: str = ""):
        """Log a test result"""
        self.test_count += 1
        if passed:
            self.pass_count += 1
            status = "✅ PASS"
        else:
            self.fail_count += 1
            status = "❌ FAIL"
        
        result = {
            "test": name,
            "status": status,
            "passed": passed,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        print(f"\n{status}: {name}")
        if message:
            print(f"   {message}")
    
    async def test_1_health_check(self):
        """Test 1: Basic health check"""
        print("\n" + "="*80)
        print("TEST 1: HEALTH CHECK")
        print("="*80)
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(HF_ENDPOINT)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        "Health Check",
                        True,
                        f"Status: {data.get('status')}, Message: {data.get('message')}"
                    )
                    return True
                else:
                    self.log_test("Health Check", False, f"Status: {response.status_code}")
                    return False
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False
    
    async def test_2_invalid_secret(self):
        """Test 2: Invalid secret rejection"""
        print("\n" + "="*80)
        print("TEST 2: INVALID SECRET REJECTION")
        print("="*80)
        
        try:
            payload = {
                "email": EMAIL,
                "secret": "wrong_secret_12345",
                "url": DEMO_QUIZ_URL
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{HF_ENDPOINT}/receive_request",
                    json=payload
                )
                
                if response.status_code == 403:
                    self.log_test(
                        "Invalid Secret Rejection",
                        True,
                        f"Correctly rejected with 403: {response.json().get('detail')}"
                    )
                    return True
                else:
                    self.log_test(
                        "Invalid Secret Rejection",
                        False,
                        f"Expected 403, got {response.status_code}"
                    )
                    return False
        except Exception as e:
            self.log_test("Invalid Secret Rejection", False, str(e))
            return False
    
    async def test_3_missing_email(self):
        """Test 3: Missing email field"""
        print("\n" + "="*80)
        print("TEST 3: MISSING EMAIL VALIDATION")
        print("="*80)
        
        try:
            payload = {
                "secret": SECRET,
                "url": DEMO_QUIZ_URL
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{HF_ENDPOINT}/receive_request",
                    json=payload
                )
                
                if response.status_code == 422:
                    self.log_test(
                        "Missing Email Validation",
                        True,
                        f"Correctly rejected: {response.json().get('detail')}"
                    )
                    return True
                else:
                    self.log_test(
                        "Missing Email Validation",
                        False,
                        f"Expected 422, got {response.status_code}"
                    )
                    return False
        except Exception as e:
            self.log_test("Missing Email Validation", False, str(e))
            return False
    
    async def test_4_missing_secret(self):
        """Test 4: Missing secret field"""
        print("\n" + "="*80)
        print("TEST 4: MISSING SECRET VALIDATION")
        print("="*80)
        
        try:
            payload = {
                "email": EMAIL,
                "url": DEMO_QUIZ_URL
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{HF_ENDPOINT}/receive_request",
                    json=payload
                )
                
                if response.status_code == 422:
                    self.log_test(
                        "Missing Secret Validation",
                        True,
                        f"Correctly rejected: {response.json().get('detail')}"
                    )
                    return True
                else:
                    self.log_test(
                        "Missing Secret Validation",
                        False,
                        f"Expected 422, got {response.status_code}"
                    )
                    return False
        except Exception as e:
            self.log_test("Missing Secret Validation", False, str(e))
            return False
    
    async def test_5_missing_url(self):
        """Test 5: Missing URL field"""
        print("\n" + "="*80)
        print("TEST 5: MISSING URL VALIDATION")
        print("="*80)
        
        try:
            payload = {
                "email": EMAIL,
                "secret": SECRET
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{HF_ENDPOINT}/receive_request",
                    json=payload
                )
                
                if response.status_code == 422:
                    self.log_test(
                        "Missing URL Validation",
                        True,
                        f"Correctly rejected: {response.json().get('detail')}"
                    )
                    return True
                else:
                    self.log_test(
                        "Missing URL Validation",
                        False,
                        f"Expected 422, got {response.status_code}"
                    )
                    return False
        except Exception as e:
            self.log_test("Missing URL Validation", False, str(e))
            return False
    
    async def test_6_invalid_json(self):
        """Test 6: Invalid JSON payload"""
        print("\n" + "="*80)
        print("TEST 6: INVALID JSON HANDLING")
        print("="*80)
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{HF_ENDPOINT}/receive_request",
                    content="not valid json",
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 400:
                    self.log_test(
                        "Invalid JSON Handling",
                        True,
                        f"Correctly rejected: {response.json().get('detail')}"
                    )
                    return True
                else:
                    self.log_test(
                        "Invalid JSON Handling",
                        False,
                        f"Expected 400, got {response.status_code}"
                    )
                    return False
        except Exception as e:
            self.log_test("Invalid JSON Handling", False, str(e))
            return False
    
    async def test_7_valid_request(self):
        """Test 7: Valid request acceptance"""
        print("\n" + "="*80)
        print("TEST 7: VALID REQUEST ACCEPTANCE")
        print("="*80)
        
        try:
            payload = {
                "email": EMAIL,
                "secret": SECRET,
                "url": DEMO_QUIZ_URL
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{HF_ENDPOINT}/receive_request",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        "Valid Request Acceptance",
                        True,
                        f"Accepted: {data.get('message')}, URL: {data.get('url')}"
                    )
                    return True
                else:
                    self.log_test(
                        "Valid Request Acceptance",
                        False,
                        f"Expected 200, got {response.status_code}: {response.text}"
                    )
                    return False
        except Exception as e:
            self.log_test("Valid Request Acceptance", False, str(e))
            return False
    
    async def test_8_method_not_allowed(self):
        """Test 8: Wrong HTTP method"""
        print("\n" + "="*80)
        print("TEST 8: METHOD NOT ALLOWED")
        print("="*80)
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{HF_ENDPOINT}/receive_request")
                
                if response.status_code == 405:
                    self.log_test(
                        "Method Not Allowed",
                        True,
                        "Correctly rejected GET request on POST endpoint"
                    )
                    return True
                else:
                    self.log_test(
                        "Method Not Allowed",
                        False,
                        f"Expected 405, got {response.status_code}"
                    )
                    return False
        except Exception as e:
            self.log_test("Method Not Allowed", False, str(e))
            return False
    
    async def test_9_concurrent_requests(self):
        """Test 9: Handle concurrent requests"""
        print("\n" + "="*80)
        print("TEST 9: CONCURRENT REQUEST HANDLING")
        print("="*80)
        
        try:
            payload = {
                "email": EMAIL,
                "secret": SECRET,
                "url": DEMO_QUIZ_URL
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Send 3 requests concurrently
                tasks = [
                    client.post(f"{HF_ENDPOINT}/receive_request", json=payload)
                    for _ in range(3)
                ]
                responses = await asyncio.gather(*tasks)
                
                all_success = all(r.status_code == 200 for r in responses)
                
                if all_success:
                    self.log_test(
                        "Concurrent Request Handling",
                        True,
                        f"All 3 concurrent requests accepted (200 OK)"
                    )
                    return True
                else:
                    statuses = [r.status_code for r in responses]
                    self.log_test(
                        "Concurrent Request Handling",
                        False,
                        f"Status codes: {statuses}"
                    )
                    return False
        except Exception as e:
            self.log_test("Concurrent Request Handling", False, str(e))
            return False
    
    async def test_10_response_time(self):
        """Test 10: Response time for acceptance"""
        print("\n" + "="*80)
        print("TEST 10: RESPONSE TIME")
        print("="*80)
        
        try:
            payload = {
                "email": EMAIL,
                "secret": SECRET,
                "url": DEMO_QUIZ_URL
            }
            
            start = time.time()
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{HF_ENDPOINT}/receive_request",
                    json=payload
                )
            elapsed = time.time() - start
            
            if response.status_code == 200 and elapsed < 5.0:
                self.log_test(
                    "Response Time",
                    True,
                    f"Request accepted in {elapsed:.2f}s (< 5s threshold)"
                )
                return True
            elif response.status_code == 200:
                self.log_test(
                    "Response Time",
                    False,
                    f"Request accepted but took {elapsed:.2f}s (> 5s threshold)"
                )
                return False
            else:
                self.log_test(
                    "Response Time",
                    False,
                    f"Status: {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_test("Response Time", False, str(e))
            return False
    
    def print_summary(self):
        """Print final test summary"""
        print("\n" + "="*80)
        print("COMPREHENSIVE TEST SUMMARY")
        print("="*80)
        print()
        print(f"Total Tests: {self.test_count}")
        print(f"Passed: {self.pass_count} ✅")
        print(f"Failed: {self.fail_count} ❌")
        print(f"Success Rate: {(self.pass_count/self.test_count*100):.1f}%")
        print()
        
        if self.fail_count > 0:
            print("FAILED TESTS:")
            for result in self.results:
                if not result['passed']:
                    print(f"   ❌ {result['test']}: {result['message']}")
            print()
        
        print("="*80)
        if self.fail_count == 0:
            print("🎉 ALL TESTS PASSED! YOUR HF SPACE IS FULLY FUNCTIONAL!")
        else:
            print("⚠️  SOME TESTS FAILED - REVIEW ABOVE")
        print("="*80)
        print()
        
        # Save results to JSON
        with open('/tmp/test_results.json', 'w') as f:
            json.dump({
                'total': self.test_count,
                'passed': self.pass_count,
                'failed': self.fail_count,
                'success_rate': self.pass_count/self.test_count*100,
                'results': self.results
            }, f, indent=2)
        
        print("📊 Detailed results saved to: /tmp/test_results.json")
        print()

async def main():
    """Run all comprehensive tests"""
    print()
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║              COMPREHENSIVE ROBUST TESTING SUITE                              ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print()
    print(f"Testing HF Space: {HF_ENDPOINT}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tester = ComprehensiveTest()
    
    # Run all tests sequentially
    await tester.test_1_health_check()
    await tester.test_2_invalid_secret()
    await tester.test_3_missing_email()
    await tester.test_4_missing_secret()
    await tester.test_5_missing_url()
    await tester.test_6_invalid_json()
    await tester.test_7_valid_request()
    await tester.test_8_method_not_allowed()
    await tester.test_9_concurrent_requests()
    await tester.test_10_response_time()
    
    # Print summary
    tester.print_summary()
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print()
    print("1. Check HF Space logs for background processing:")
    print(f"   https://huggingface.co/spaces/MathCsAi/llm-quiz-solver/logs")
    print()
    print("2. Look for these indicators in logs:")
    print("   ✅ 'Successfully extracted quiz content'")
    print("   ✅ 'API Response Status: 200'")
    print("   ✅ 'LLM response received'")
    print("   ✅ 'Script execution result'")
    print()
    print("3. If you see 'Timeout' or 'Error' messages:")
    print("   - Check AI_PIPE_TOKEN is valid")
    print("   - Verify generativelanguage.googleapis.com API is responding")
    print("   - Check model 'gpt-4o-mini' is available")
    print()
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
