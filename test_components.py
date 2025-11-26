"""
Comprehensive testing script for local development
Tests all components of the quiz solver
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("="*60)
print("LLM QUIZ SOLVER - COMPONENT TEST SUITE")
print("="*60)
print()


def test_environment():
    """Test environment variables"""
    print("1. Testing Environment Configuration...")
    
    required = ["EMAIL", "SECRET_KEY", "AI_PIPE_TOKEN"]
    missing = []
    
    for var in required:
        value = os.getenv(var)
        if not value:
            missing.append(var)
            print(f"  ✗ {var}: NOT SET")
        else:
            masked = value[:4] + "*" * (len(value) - 4) if len(value) > 4 else "****"
            print(f"  ✓ {var}: {masked}")
    
    if missing:
        print(f"\n  ERROR: Missing variables: {', '.join(missing)}")
        print("  Please configure .env file")
        return False
    
    print("  ✓ All environment variables configured\n")
    return True


def test_imports():
    """Test that all required modules can be imported"""
    print("2. Testing Python Dependencies...")
    
    modules = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("httpx", "HTTPX"),
        ("playwright", "Playwright"),
        ("bs4", "BeautifulSoup"),
        ("pandas", "Pandas"),
        ("dotenv", "Python-dotenv")
    ]
    
    failed = []
    
    for module, name in modules:
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - NOT INSTALLED")
            failed.append(module)
    
    if failed:
        print(f"\n  ERROR: Missing modules: {', '.join(failed)}")
        print("  Run: pip install -r requirements.txt")
        return False
    
    print("  ✓ All dependencies installed\n")
    return True


def test_playwright():
    """Test Playwright browser installation"""
    print("3. Testing Playwright Browser...")
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto("https://www.google.com")
                title = page.title()
                browser.close()
                
                print(f"  ✓ Chromium browser working")
                print(f"  ✓ Test navigation successful: {title}")
                print()
                return True
                
            except Exception as e:
                print(f"  ✗ Browser error: {e}")
                print("  Run: playwright install chromium")
                print()
                return False
                
    except Exception as e:
        print(f"  ✗ Playwright error: {e}")
        print()
        return False


async def test_scraper():
    """Test web scraping functionality"""
    print("4. Testing Web Scraper...")
    
    try:
        from scraper import fetch_quiz_content_simple
        
        test_url = "https://example.com"
        result = await fetch_quiz_content_simple(test_url)
        
        if result and 'text' in result:
            print(f"  ✓ Scraper working")
            print(f"  ✓ Fetched {len(result['text'])} characters")
            print()
            return True
        else:
            print(f"  ✗ Scraper returned unexpected result")
            print()
            return False
            
    except Exception as e:
        print(f"  ✗ Scraper error: {e}")
        print()
        return False


async def test_aipipe():
    """Test AI Pipe API connection"""
    print("5. Testing AI Pipe API...")
    
    try:
        import httpx
        
        token = os.getenv("AI_PIPE_TOKEN")
        url = "https://aipipe.ai/api/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Say 'API test successful' and nothing else"}],
            "max_tokens": 50
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"  ✓ AI Pipe API connected")
                print(f"  ✓ Response: {content}")
                print()
                return True
            else:
                print(f"  ✗ API returned status {response.status_code}")
                print(f"  Response: {response.text}")
                print()
                return False
                
    except Exception as e:
        print(f"  ✗ AI Pipe API error: {e}")
        print()
        return False


def test_project_structure():
    """Test that all required files exist"""
    print("6. Testing Project Structure...")
    
    required_files = [
        "main.py",
        "quiz_solver.py",
        "scraper.py",
        "prompts.py",
        "requirements.txt",
        ".env",
        "LICENSE",
        "README.md"
    ]
    
    missing = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - NOT FOUND")
            missing.append(file)
    
    if missing:
        print(f"\n  ERROR: Missing files: {', '.join(missing)}")
        return False
    
    print("  ✓ All required files present\n")
    return True


async def run_all_tests():
    """Run all tests"""
    results = []
    
    # Synchronous tests
    results.append(("Environment", test_environment()))
    results.append(("Dependencies", test_imports()))
    results.append(("Playwright", test_playwright()))
    results.append(("Project Structure", test_project_structure()))
    
    # Asynchronous tests
    results.append(("Web Scraper", await test_scraper()))
    results.append(("AI Pipe API", await test_aipipe()))
    
    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Start server: ./start_server.sh")
        print("2. Test endpoint: python test_endpoint.py")
        print("3. Deploy and submit Google Form")
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
