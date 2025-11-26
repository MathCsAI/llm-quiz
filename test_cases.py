#!/usr/bin/env python3
"""
Comprehensive Test Cases for LLM Quiz Solver
Tests both local functionality and deployed Hugging Face endpoint
"""
import asyncio
import json
import sys
from typing import Dict, Any
import httpx


class TestCases:
    """Test suite for quiz solver application"""
    
    def __init__(self, hf_endpoint: str = None):
        """
        Initialize test cases
        
        Args:
            hf_endpoint: Hugging Face Spaces endpoint URL (optional)
        """
        self.hf_endpoint = hf_endpoint
        self.email = "23f2003858@ds.study.iitm.ac.in"
        self.secret = "123456789"
        self.results = []
    
    def log_result(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "passed": passed,
            "message": message
        })
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
    
    async def test_local_imports(self):
        """Test 1: Verify all modules can be imported"""
        try:
            from quiz_solver import QuizSolver, DEFAULT_MODEL, FALLBACK_MODELS
            from scraper import QuizScraper
            from prompts import get_script_generation_prompt, SYSTEM_PROMPT_DEFENSE, USER_PROMPT_ATTACK
            from app import app
            
            self.log_result(
                "Local Module Imports",
                True,
                f"Model: {DEFAULT_MODEL}, Fallback: {FALLBACK_MODELS}"
            )
        except Exception as e:
            self.log_result("Local Module Imports", False, str(e))
    
    async def test_local_config(self):
        """Test 2: Verify configuration is correct"""
        try:
            from quiz_solver import DEFAULT_MODEL, FALLBACK_MODELS, AI_PIPE_API_URL
            
            # Accept either gpt-4.1-nano or gpt-4o-mini
            valid_models = ["gpt-4.1-nano", "gpt-4o-mini"]
            assert DEFAULT_MODEL in valid_models, f"Invalid model: {DEFAULT_MODEL}"
            assert "aipipe.ai" in AI_PIPE_API_URL, f"Wrong API URL: {AI_PIPE_API_URL}"
            
            self.log_result("Configuration Validation", True, f"API: {AI_PIPE_API_URL}")
        except Exception as e:
            self.log_result("Configuration Validation", False, str(e))
    
    async def test_local_prompts(self):
        """Test 3: Verify prompt constraints"""
        try:
            from prompts import SYSTEM_PROMPT_DEFENSE, USER_PROMPT_ATTACK
            
            defense_len = len(SYSTEM_PROMPT_DEFENSE)
            attack_len = len(USER_PROMPT_ATTACK)
            
            assert defense_len <= 100, f"Defense prompt too long: {defense_len} chars"
            assert attack_len <= 100, f"Attack prompt too long: {attack_len} chars"
            
            self.log_result(
                "Prompt Length Constraints",
                True,
                f"Defense: {defense_len}/100, Attack: {attack_len}/100"
            )
        except Exception as e:
            self.log_result("Prompt Length Constraints", False, str(e))
    
    async def test_local_quiz_solver_init(self):
        """Test 4: Verify QuizSolver initialization"""
        try:
            import os
            from dotenv import load_dotenv
            from quiz_solver import QuizSolver
            
            load_dotenv()
            solver = QuizSolver(
                email=self.email,
                secret=self.secret
            )
            
            assert solver.email == self.email
            assert solver.secret == self.secret
            assert solver.ai_pipe_token is not None
            
            self.log_result("QuizSolver Initialization", True)
        except Exception as e:
            self.log_result("QuizSolver Initialization", False, str(e))
    
    async def test_hf_health_check(self):
        """Test 5: Check if HF endpoint is accessible"""
        if not self.hf_endpoint:
            self.log_result("HF Health Check", False, "No HF endpoint provided")
            return
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.hf_endpoint)
                
                if response.status_code == 200:
                    self.log_result("HF Health Check", True, f"Status: {response.status_code}")
                else:
                    self.log_result("HF Health Check", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("HF Health Check", False, str(e))
    
    async def test_hf_endpoint_validation(self):
        """Test 6: Validate HF endpoint accepts correct requests"""
        if not self.hf_endpoint:
            self.log_result("HF Endpoint Validation", False, "No HF endpoint provided")
            return
        
        try:
            url = f"{self.hf_endpoint}/receive_request"
            payload = {
                "email": self.email,
                "secret": self.secret,
                "url": "https://example.com/test"  # Dummy URL for validation
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                
                # We expect 200 even if quiz fails (background task)
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(
                        "HF Endpoint Validation",
                        True,
                        f"Response: {data.get('message', 'OK')}"
                    )
                else:
                    self.log_result(
                        "HF Endpoint Validation",
                        False,
                        f"Status: {response.status_code}, Body: {response.text[:200]}"
                    )
        except Exception as e:
            self.log_result("HF Endpoint Validation", False, str(e))
    
    async def test_hf_invalid_secret(self):
        """Test 7: Verify HF endpoint rejects invalid secret"""
        if not self.hf_endpoint:
            self.log_result("HF Invalid Secret Rejection", False, "No HF endpoint provided")
            return
        
        try:
            url = f"{self.hf_endpoint}/receive_request"
            payload = {
                "email": self.email,
                "secret": "wrong_secret",
                "url": "https://example.com/test"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                
                # Should return 403 for invalid secret
                if response.status_code == 403:
                    self.log_result("HF Invalid Secret Rejection", True, "Correctly rejected")
                else:
                    self.log_result(
                        "HF Invalid Secret Rejection",
                        False,
                        f"Expected 403, got {response.status_code}"
                    )
        except Exception as e:
            self.log_result("HF Invalid Secret Rejection", False, str(e))
    
    async def test_hf_missing_fields(self):
        """Test 8: Verify HF endpoint validates required fields"""
        if not self.hf_endpoint:
            self.log_result("HF Missing Fields Validation", False, "No HF endpoint provided")
            return
        
        try:
            url = f"{self.hf_endpoint}/receive_request"
            payload = {
                "email": self.email,
                # Missing 'secret' and 'url'
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                
                # Should return 422 for validation error
                if response.status_code == 422:
                    self.log_result("HF Missing Fields Validation", True, "Correctly validated")
                else:
                    self.log_result(
                        "HF Missing Fields Validation",
                        False,
                        f"Expected 422, got {response.status_code}"
                    )
        except Exception as e:
            self.log_result("HF Missing Fields Validation", False, str(e))
    
    async def test_hf_demo_quiz(self):
        """Test 9: Test with demo quiz URL (if available)"""
        if not self.hf_endpoint:
            self.log_result("HF Demo Quiz Test", False, "No HF endpoint provided")
            return
        
        try:
            url = f"{self.hf_endpoint}/receive_request"
            # Using a demo quiz URL from the problem statement
            payload = {
                "email": self.email,
                "secret": self.secret,
                "url": "https://tds-llm-analysis.s-anand.net/demo"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(
                        "HF Demo Quiz Test",
                        True,
                        f"Quiz processing started: {data.get('message')}"
                    )
                else:
                    self.log_result(
                        "HF Demo Quiz Test",
                        False,
                        f"Status: {response.status_code}"
                    )
        except Exception as e:
            self.log_result("HF Demo Quiz Test", False, str(e))
    
    async def run_all_tests(self, include_hf: bool = True):
        """Run all test cases"""
        print("\n" + "="*70)
        print(" "*20 + "RUNNING TEST SUITE")
        print("="*70 + "\n")
        
        # Local tests (always run)
        print("📋 LOCAL TESTS:")
        await self.test_local_imports()
        await self.test_local_config()
        await self.test_local_prompts()
        await self.test_local_quiz_solver_init()
        
        # HF tests (only if endpoint provided)
        if include_hf and self.hf_endpoint:
            print("\n🚀 HUGGING FACE DEPLOYMENT TESTS:")
            await self.test_hf_health_check()
            await self.test_hf_endpoint_validation()
            await self.test_hf_invalid_secret()
            await self.test_hf_missing_fields()
            await self.test_hf_demo_quiz()
        elif include_hf and not self.hf_endpoint:
            print("\n⚠️  HUGGING FACE TESTS SKIPPED: No endpoint provided")
        
        # Summary
        print("\n" + "="*70)
        print(" "*20 + "TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for r in self.results if r["passed"])
        failed = sum(1 for r in self.results if not r["passed"])
        total = len(self.results)
        
        print(f"\n✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {failed}/{total}")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if not result["passed"]:
                    print(f"   - {result['test']}: {result['message']}")
        
        print("\n" + "="*70)
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED!")
        else:
            print("⚠️  SOME TESTS FAILED - REVIEW ABOVE")
        
        print("="*70 + "\n")
        
        return failed == 0


async def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test LLM Quiz Solver")
    parser.add_argument(
        "--hf-endpoint",
        help="Hugging Face Spaces endpoint URL",
        default=None
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Run only local tests, skip HF tests"
    )
    
    args = parser.parse_args()
    
    tests = TestCases(hf_endpoint=args.hf_endpoint)
    success = await tests.run_all_tests(include_hf=not args.local_only)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
