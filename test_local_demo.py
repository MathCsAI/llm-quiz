#!/usr/bin/env python3
"""
Test the quiz solver locally to verify it can:
1. Scrape the demo quiz
2. Generate a solution script
3. Execute the script
"""
import asyncio
import os
from quiz_solver import QuizSolver
from scraper import QuizScraper

# Load environment variables
EMAIL = os.getenv("EMAIL", "23f2003858@ds.study.iitm.ac.in")
SECRET = os.getenv("SECRET_KEY", "123456789")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEMO_QUIZ_URL = "https://tds-llm-analysis.s-anand.net/demo"

async def test_scraper():
    """Test if scraper can extract the demo quiz"""
    print("=" * 80)
    print("TEST 1: SCRAPING DEMO QUIZ")
    print("=" * 80)
    print()
    
    scraper = QuizScraper()
    
    print(f"📥 Fetching quiz from: {DEMO_QUIZ_URL}")
    print()
    
    try:
        quiz_data = await scraper.fetch_quiz_content(DEMO_QUIZ_URL)
        
        if quiz_data and quiz_data.get("question"):
            print("✅ Successfully scraped quiz!")
            print()
            print(f"📋 Question (first 200 chars):")
            print(f"   {quiz_data['question'][:200]}...")
            print()
            
            if quiz_data.get("submit_url"):
                print(f"📤 Submit URL: {quiz_data['submit_url']}")
            else:
                print("⚠️  No submit URL found (expected for demo)")
            
            print()
            return True
        else:
            print("❌ Failed to extract question")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_full_solver():
    """Test the full quiz solver pipeline"""
    print("=" * 80)
    print("TEST 2: FULL QUIZ SOLVER PIPELINE")
    print("=" * 80)
    print()
    
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not set in environment")
        print("   Set it in .env file to run this test")
        return False
    
    print(f"🚀 Starting quiz solver...")
    print(f"   Email: {EMAIL}")
    print(f"   Quiz: {DEMO_QUIZ_URL}")
    print()
    
    solver = QuizSolver(
        email=EMAIL,
        secret=SECRET
    )
    
    try:
        await solver.solve_quiz_chain(DEMO_QUIZ_URL)
        
        print()
        print("=" * 80)
        print("RESULTS")
        print("=" * 80)
        print()
        print("✅ Quiz processing completed!")
        print()
        print("📊 Check the logs above for:")
        print("   - Quiz scraping success")
        print("   - LLM script generation")
        print("   - Script execution results")
        print()
        return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print()
    print("🧪 TESTING QUIZ SOLVER LOCALLY")
    print()
    
    # Test 1: Scraping
    scraper_ok = await test_scraper()
    
    print()
    input("Press Enter to continue to full solver test...")
    print()
    
    # Test 2: Full solver
    solver_ok = await test_full_solver()
    
    # Summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()
    print(f"Scraping Test: {'✅ PASS' if scraper_ok else '❌ FAIL'}")
    print(f"Full Solver Test: {'✅ PASS' if solver_ok else '❌ FAIL'}")
    print()
    
    if scraper_ok and solver_ok:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("Your quiz solver is working correctly.")
        print("The HF Space should be able to process quizzes successfully.")
    else:
        print("⚠️  SOME TESTS FAILED")
        print()
        print("Review the errors above to debug issues.")

if __name__ == "__main__":
    asyncio.run(main())
