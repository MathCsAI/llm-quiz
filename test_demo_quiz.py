#!/usr/bin/env python3
"""
Test the quiz solver against the actual demo quiz
Submits a real quiz and verifies it processes correctly
"""
import asyncio
import httpx
import time

# Configuration
HF_ENDPOINT = "https://mathcsai-llm-quiz-solver.hf.space"
EMAIL = "23f2003858@ds.study.iitm.ac.in"
SECRET = "123456789"
DEMO_QUIZ_URL = "https://tds-llm-analysis.s-anand.net/demo"

async def test_demo_quiz():
    """Submit the demo quiz and check if it processes correctly"""
    
    print("=" * 80)
    print("TESTING DEMO QUIZ ON HUGGING FACE SPACE")
    print("=" * 80)
    print()
    
    # Submit the quiz
    print(f"📤 Submitting quiz to HF Space...")
    print(f"   Endpoint: {HF_ENDPOINT}/receive_request")
    print(f"   Quiz URL: {DEMO_QUIZ_URL}")
    print()
    
    payload = {
        "email": EMAIL,
        "secret": SECRET,
        "url": DEMO_QUIZ_URL
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{HF_ENDPOINT}/receive_request",
                json=payload
            )
            
            print(f"✅ Response Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            print()
            
            if response.status_code == 200:
                print("✅ Quiz request accepted!")
                print("   The quiz is now being processed in the background.")
                print()
                print("🔍 Check HF Space logs to verify:")
                print("   1. Quiz page scraped successfully")
                print("   2. Question extracted from decoded content")
                print("   3. LLM generated solution script")
                print("   4. Script executed and answer submitted")
                print()
                print("📊 Expected in logs:")
                print("   - 'Successfully extracted quiz content'")
                print("   - 'Calling AI Pipe API with model: gpt-4.1-nano'")
                print("   - 'Generated script' or 'LLM response received'")
                print("   - 'Script execution result'")
                print()
                print("=" * 80)
                print("🎯 MANUAL VERIFICATION STEPS:")
                print("=" * 80)
                print()
                print("1. Go to your HF Space:")
                print(f"   https://huggingface.co/spaces/MathCsAi/llm-quiz-solver")
                print()
                print("2. Check the Logs tab")
                print()
                print("3. Look for these success indicators:")
                print("   ✅ 'Accepted quiz request for...'")
                print("   ✅ 'Successfully extracted quiz content'")
                print("   ✅ 'Calling AI Pipe API'")
                print("   ✅ 'Generated script' (the LLM's solution)")
                print("   ✅ 'Script execution result'")
                print()
                print("4. The demo quiz asks for window.location.origin")
                print("   Expected answer: The Space's origin URL")
                print()
                print("=" * 80)
                return True
            else:
                print(f"❌ Unexpected response: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def check_space_health():
    """Check if the HF Space is running"""
    print("🏥 Checking HF Space health...")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(HF_ENDPOINT)
            
            if response.status_code == 200:
                print(f"✅ Space is online: {response.json()}")
                print()
                return True
            else:
                print(f"⚠️  Space returned: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Space not reachable: {e}")
        return False

async def main():
    """Run the demo quiz test"""
    
    # First check if space is healthy
    if not await check_space_health():
        print("❌ HF Space is not accessible. Please check the deployment.")
        return
    
    # Submit the demo quiz
    success = await test_demo_quiz()
    
    if success:
        print()
        print("✅ TEST COMPLETE")
        print()
        print("Next: Check HF Space logs to see the full processing details")
        print("      and verify the answer was submitted correctly.")
    else:
        print()
        print("❌ TEST FAILED")
        print("   Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
