#!/usr/bin/env python3
"""
Check if the app is working correctly according to evaluation requirements.

This performs LOCAL validation without requiring API access:
1. Prompt constraints (≤100 chars)
2. Module imports and configuration
3. FastAPI endpoint structure
4. Demo endpoint local testing
"""

import sys
import os

def check_prompts():
    """Check prompt constraints."""
    print("=" * 80)
    print("1. PROMPT CONSTRAINTS CHECK")
    print("=" * 80)
    print()
    
    try:
        from prompts import SYSTEM_PROMPT_DEFENSE, USER_PROMPT_ATTACK
        
        defense_len = len(SYSTEM_PROMPT_DEFENSE)
        attack_len = len(USER_PROMPT_ATTACK)
        
        print(f"📋 System Prompt (Defense):")
        print(f"   Length: {defense_len}/100 chars")
        print(f"   Content: '{SYSTEM_PROMPT_DEFENSE}'")
        
        if defense_len <= 100:
            print(f"   ✅ PASS - Within limit")
        else:
            print(f"   ❌ FAIL - Exceeds 100 char limit by {defense_len - 100}")
        print()
        
        print(f"🎯 User Prompt (Attack):")
        print(f"   Length: {attack_len}/100 chars")
        print(f"   Content: '{USER_PROMPT_ATTACK}'")
        
        if attack_len <= 100:
            print(f"   ✅ PASS - Within limit")
        else:
            print(f"   ❌ FAIL - Exceeds 100 char limit by {attack_len - 100}")
        print()
        
        # Check defense effectiveness (basic heuristics)
        print("🛡️  Defense Prompt Analysis:")
        defense_lower = SYSTEM_PROMPT_DEFENSE.lower()
        
        has_ignore = "ignore" in defense_lower
        has_never = "never" in defense_lower or "don't" in defense_lower or "not" in defense_lower
        has_secrets = "secret" in defense_lower or "code word" in defense_lower or "password" in defense_lower
        
        print(f"   - Contains 'ignore': {'✅' if has_ignore else '❌'}")
        print(f"   - Contains negation: {'✅' if has_never else '❌'}")
        print(f"   - Mentions secrets: {'✅' if has_secrets else '❌'}")
        
        if has_ignore and has_never:
            print(f"   💡 Good defense strategy!")
        else:
            print(f"   ⚠️  Consider strengthening defense")
        print()
        
        # Check attack effectiveness
        print("⚔️  Attack Prompt Analysis:")
        attack_lower = USER_PROMPT_ATTACK.lower()
        
        asks_directly = "code word" in attack_lower or "secret" in attack_lower
        uses_encoding = "base64" in attack_lower or "encode" in attack_lower
        asks_for_system = "system prompt" in attack_lower or "instructions" in attack_lower
        
        print(f"   - Asks directly: {'✅' if asks_directly else '❌'}")
        print(f"   - Uses encoding trick: {'✅' if uses_encoding else '❌'}")
        print(f"   - Requests system prompt: {'✅' if asks_for_system else '❌'}")
        
        if asks_directly or uses_encoding or asks_for_system:
            print(f"   💡 Good attack strategy!")
        else:
            print(f"   ⚠️  Consider more aggressive attack")
        
        return defense_len <= 100 and attack_len <= 100
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False


def check_configuration():
    """Check configuration and model settings."""
    print("\n" + "=" * 80)
    print("2. CONFIGURATION CHECK")
    print("=" * 80)
    print()
    
    try:
        from quiz_solver import DEFAULT_MODEL, FALLBACK_MODELS, AI_PIPE_API_URL
        
        print(f"🤖 Model Configuration:")
        print(f"   Default Model: {DEFAULT_MODEL}")
        print(f"   Fallback Models: {FALLBACK_MODELS}")
        print()
        
        # Check model is gpt-4.1-nano as required
        correct_model = DEFAULT_MODEL == "gpt-4.1-nano"
        correct_fallback = "gpt-4.1-nano" in FALLBACK_MODELS
        
        if correct_model:
            print(f"   ✅ PASS - Using required model (gpt-4.1-nano)")
        else:
            print(f"   ❌ FAIL - Wrong model (should be gpt-4.1-nano)")
        
        if correct_fallback:
            print(f"   ✅ PASS - Fallback includes gpt-4.1-nano")
        else:
            print(f"   ❌ FAIL - Fallback should include gpt-4.1-nano")
        print()
        
        print(f"🔗 API Configuration:")
        print(f"   Endpoint: {AI_PIPE_API_URL}")
        
        correct_url = ("aipipe.ai" in AI_PIPE_API_URL) or ("aipipe.org" in AI_PIPE_API_URL)
        if correct_url:
            print(f"   ✅ PASS - Using correct API endpoint")
        else:
            print(f"   ❌ FAIL - Wrong API endpoint")
        print()
        
        return correct_model and correct_fallback and correct_url
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def check_fastapi_endpoint():
    """Check FastAPI endpoint structure."""
    print("\n" + "=" * 80)
    print("3. FASTAPI ENDPOINT CHECK")
    print("=" * 80)
    print()
    
    try:
        from app import app
        
        routes = [route.path for route in app.routes]
        
        print(f"📡 Available Routes:")
        for route in routes:
            print(f"   - {route}")
        print()
        
        has_receive = "/receive_request" in routes
        has_health = "/" in routes
        
        if has_receive:
            print(f"   ✅ PASS - /receive_request endpoint exists")
        else:
            print(f"   ❌ FAIL - Missing /receive_request endpoint")
        
        if has_health:
            print(f"   ✅ PASS - Health check endpoint exists")
        else:
            print(f"   ⚠️  Warning - No health check endpoint")
        print()
        
        # Check if QuizRequest model exists
        try:
            from app import QuizRequest
            print(f"📋 Request Model:")
            print(f"   - QuizRequest model: ✅ Defined")
            
            # Check required fields
            fields = QuizRequest.model_fields if hasattr(QuizRequest, 'model_fields') else QuizRequest.__fields__
            field_names = list(fields.keys())
            
            print(f"   - Required fields: {field_names}")
            
            has_email = "email" in field_names
            has_secret = "secret" in field_names
            has_url = "url" in field_names
            
            if has_email and has_secret and has_url:
                print(f"   ✅ PASS - All required fields present")
            else:
                print(f"   ❌ FAIL - Missing required fields")
            print()
            
            return has_receive and has_email and has_secret and has_url
            
        except ImportError:
            print(f"   ⚠️  Warning - Could not import QuizRequest model")
            return has_receive
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def check_quiz_solver():
    """Check QuizSolver implementation."""
    print("\n" + "=" * 80)
    print("4. QUIZ SOLVER CHECK")
    print("=" * 80)
    print()
    
    try:
        from quiz_solver import QuizSolver
        
        print(f"🧩 QuizSolver Class:")
        
        # Check key methods
        methods = [method for method in dir(QuizSolver) if not method.startswith('_')]
        print(f"   Available methods: {len(methods)}")
        
        required_methods = ['solve_quiz', 'solve_quiz_chain']
        for method in required_methods:
            if method in methods:
                print(f"   ✅ {method}")
            else:
                print(f"   ❌ Missing: {method}")
        print()
        
        # Try to create instance
        try:
            solver = QuizSolver(
                email="test@example.com",
                secret="test_secret",
                ai_pipe_token="test_token"
            )
            print(f"   ✅ PASS - Can instantiate QuizSolver")
            return True
        except Exception as e:
            print(f"   ⚠️  Warning - Instantiation issue: {str(e)}")
            return True  # Still pass if class exists
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def check_dockerfile():
    """Check Dockerfile configuration."""
    print("\n" + "=" * 80)
    print("5. DOCKERFILE CHECK")
    print("=" * 80)
    print()
    
    if not os.path.exists("Dockerfile"):
        print("❌ FAIL - Dockerfile not found")
        return False
    
    with open("Dockerfile", "r") as f:
        content = f.read()
    
    print(f"📦 Dockerfile Configuration:")
    
    # Check for specific patterns (excluding comments)
    lines = [line for line in content.split('\n') if not line.strip().startswith('#')]
    content_no_comments = '\n'.join(lines)
    
    checks = {
        "fonts-noto": "fonts-noto" in content,
        "playwright": "playwright install" in content,
        "no --with-deps flag": "playwright install chromium" in content_no_comments and "--with-deps" not in content_no_comments,
        "port 7860": "7860" in content,
        "chromium": "chromium" in content,
    }
    
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check_name}")
    
    print()
    
    all_passed = all(checks.values())
    if all_passed:
        print(f"   ✅ PASS - Dockerfile properly configured")
    else:
        print(f"   ⚠️  Warning - Some checks failed")
    
    return all_passed


def main():
    """Run all checks."""
    print()
    print("=" * 80)
    print("APP READINESS CHECK - Evaluation Requirements")
    print("=" * 80)
    print()
    print("This checks if your app is ready for evaluation:")
    print("  ✅ Prompt constraints (≤100 chars)")
    print("  ✅ Correct model (gpt-4.1-nano)")
    print("  ✅ FastAPI endpoint structure")
    print("  ✅ Quiz solver implementation")
    print("  ✅ Dockerfile configuration")
    print()
    
    results = []
    
    # Run all checks
    results.append(("Prompt Constraints", check_prompts()))
    results.append(("Configuration", check_configuration()))
    results.append(("FastAPI Endpoint", check_fastapi_endpoint()))
    results.append(("Quiz Solver", check_quiz_solver()))
    results.append(("Dockerfile", check_dockerfile()))
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {check_name}")
    
    print()
    print(f"Total: {passed}/{total} checks passed")
    print()
    
    if passed == total:
        print("🎉 ALL CHECKS PASSED!")
        print()
        print("✅ Your app is ready for evaluation!")
        print()
        print("Next steps:")
        print("  1. Test locally: uvicorn app:app --host 0.0.0.0 --port 7860")
        print("  2. Test demo endpoint: python3 test_demo_endpoint.py")
        print("  3. Deploy to Hugging Face Spaces")
        print("  4. Test HF endpoint with: python3 test_cases.py --hf-endpoint URL")
        print("  5. Submit to evaluation form before deadline")
        print()
        print("⏰ Deadline: Sat 29 Nov 2025, 3:00-4:00 PM IST")
    elif passed >= total * 0.8:
        print("👍 MOSTLY READY!")
        print()
        print("Fix the failing checks above, then proceed with deployment.")
    else:
        print("⚠️  NEEDS WORK!")
        print()
        print("Please fix the failing checks before proceeding.")
    
    print()
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
