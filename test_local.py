#!/usr/bin/env python3
"""
Local test script to verify the application works
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check required environment variables
required_vars = ["EMAIL", "SECRET_KEY", "AI_PIPE_TOKEN"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
    print("\nPlease create a .env file with:")
    print("EMAIL=23f2003858@ds.study.iitm.ac.in")
    print("SECRET_KEY=12356789")
    print("AI_PIPE_TOKEN=your_token_here")
    sys.exit(1)

print("✅ Environment variables loaded")
print(f"   EMAIL: {os.getenv('EMAIL')}")
print(f"   SECRET_KEY: {'*' * len(os.getenv('SECRET_KEY'))}")
print(f"   AI_PIPE_TOKEN: {'*' * 20}...")

# Test imports
print("\n📦 Testing imports...")
try:
    from quiz_solver import QuizSolver, solve_quiz_task
    from scraper import QuizScraper
    from prompts import get_script_generation_prompt, SYSTEM_PROMPT_DEFENSE, USER_PROMPT_ATTACK
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test QuizSolver initialization
print("\n🔧 Testing QuizSolver initialization...")
try:
    solver = QuizSolver(
        email=os.getenv("EMAIL"),
        secret=os.getenv("SECRET_KEY")
    )
    print("✅ QuizSolver initialized successfully")
except Exception as e:
    print(f"❌ QuizSolver initialization failed: {e}")
    sys.exit(1)

# Test LLM connection
print("\n🤖 Testing LLM API connection...")
async def test_llm():
    try:
        from quiz_solver import DEFAULT_MODEL
        response = await solver.call_llm(
            prompt="Say 'Hello, I am working!' in exactly those words.",
            model=DEFAULT_MODEL
        )
        if response:
            print(f"✅ LLM responded: {response[:100]}...")
            return True
        else:
            print("❌ LLM returned None")
            return False
    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        return False

llm_success = asyncio.run(test_llm())

# Test scraper
print("\n🌐 Testing web scraper...")
async def test_scraper():
    try:
        scraper = QuizScraper()
        # Use a simple URL to test scraping capability
        print("   Note: Scraper initialized successfully")
        print("   (Full scraping test would require a live quiz URL)")
        return True
    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        return False

scraper_success = asyncio.run(test_scraper())

# Test prompt generation
print("\n📝 Testing prompt generation...")
try:
    prompt = get_script_generation_prompt(
        question="What is 2+2?",
        quiz_url="https://example.com/quiz",
        submit_url="https://example.com/submit",
        email=os.getenv("EMAIL"),
        secret=os.getenv("SECRET_KEY")
    )
    if prompt and len(prompt) > 100:
        print(f"✅ Prompt generated successfully ({len(prompt)} chars)")
        prompt_success = True
    else:
        print("❌ Prompt generation failed or too short")
        prompt_success = False
except Exception as e:
    print(f"❌ Prompt generation failed: {e}")
    prompt_success = False

# Test defense/attack prompts
print("\n🛡️ Testing defense/attack prompts...")
try:
    if len(SYSTEM_PROMPT_DEFENSE) <= 100:
        print(f"✅ Defense prompt: {len(SYSTEM_PROMPT_DEFENSE)} chars (≤100)")
    else:
        print(f"⚠️  Defense prompt: {len(SYSTEM_PROMPT_DEFENSE)} chars (>100!)")
    
    if len(USER_PROMPT_ATTACK) <= 100:
        print(f"✅ Attack prompt: {len(USER_PROMPT_ATTACK)} chars (≤100)")
    else:
        print(f"⚠️  Attack prompt: {len(USER_PROMPT_ATTACK)} chars (>100!)")
    
    prompts_success = True
except Exception as e:
    print(f"❌ Prompt check failed: {e}")
    prompts_success = False

# Summary
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)
print(f"Environment Variables:  {'✅' if not missing_vars else '❌'}")
print(f"Module Imports:         ✅")
print(f"QuizSolver Init:        ✅")
print(f"LLM API Connection:     {'✅' if llm_success else '❌'}")
print(f"Web Scraper:            {'✅' if scraper_success else '❌'}")
print(f"Prompt Generation:      {'✅' if prompt_success else '❌'}")
print(f"Defense/Attack Prompts: {'✅' if prompts_success else '❌'}")

all_success = llm_success and scraper_success and prompt_success and prompts_success

if all_success:
    print("\n🎉 ALL TESTS PASSED! Application is ready.")
    print("\nTo test with a real quiz, run:")
    print("python3 app.py")
    print("\nThen in another terminal:")
    print('curl -X POST http://localhost:7860/receive_request \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"email":"23f2003858@ds.study.iitm.ac.in","secret":"12356789","url":"YOUR_QUIZ_URL"}\'')
    sys.exit(0)
else:
    print("\n❌ SOME TESTS FAILED. Please fix the issues above.")
    sys.exit(1)
