#!/usr/bin/env python3
"""
Check Hugging Face Spaces deployment status and run tests
"""
import asyncio
import sys
import httpx


async def check_hf_space(username: str, space_name: str):
    """Check if HF Space is accessible"""
    url = f"https://{username}-{space_name}.hf.space"
    
    print(f"Checking Hugging Face Space: {url}")
    print("="*60)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("\n🔍 Testing health endpoint...")
            response = await client.get(url)
            
            if response.status_code == 200:
                print(f"✅ Space is ONLINE (Status: {response.status_code})")
                print(f"   Response length: {len(response.text)} bytes")
                return url
            elif response.status_code == 503:
                print(f"⏳ Space is BUILDING (Status: 503)")
                print("   Wait a few minutes and try again")
                return None
            else:
                print(f"⚠️  Unexpected status: {response.status_code}")
                return None
                
    except httpx.TimeoutException:
        print("⏳ Request timed out - Space may still be building")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


async def test_endpoint(url: str):
    """Quick test of the /receive_request endpoint"""
    endpoint = f"{url}/receive_request"
    
    print(f"\n🧪 Testing API endpoint: {endpoint}")
    print("="*60)
    
    # Test 1: Valid request
    print("\nTest 1: Valid request (dummy URL)")
    payload = {
        "email": "23f2003858@ds.study.iitm.ac.in",
        "secret": "12356789",
        "url": "https://example.com/test"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(endpoint, json=payload)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Endpoint accepts valid requests")
                data = response.json()
                print(f"   Response: {data}")
            else:
                print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Invalid secret
    print("\nTest 2: Invalid secret (should reject)")
    payload["secret"] = "wrong"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(endpoint, json=payload)
            print(f"   Status: {response.status_code}")
            if response.status_code == 403:
                print(f"   ✅ Correctly rejects invalid secret")
            else:
                print(f"   ⚠️  Expected 403, got {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check HF Space deployment")
    parser.add_argument(
        "--username",
        default="",
        help="Hugging Face username"
    )
    parser.add_argument(
        "--space",
        default="llm-quiz-solver",
        help="Space name (default: llm-quiz-solver)"
    )
    parser.add_argument(
        "--url",
        help="Direct HF Space URL (overrides username/space)"
    )
    
    args = parser.parse_args()
    
    if args.url:
        url = args.url.rstrip('/')
        print(f"Using provided URL: {url}\n")
        await test_endpoint(url)
    elif args.username:
        url = await check_hf_space(args.username, args.space)
        if url:
            await test_endpoint(url)
            print(f"\n✅ Space is ready!")
            print(f"\n🚀 Run full test suite with:")
            print(f"   python3 test_cases.py --hf-endpoint {url}")
        else:
            print(f"\n⏳ Space not ready yet. Check status at:")
            print(f"   https://huggingface.co/spaces/{args.username}/{args.space}")
    else:
        print("Please provide either --username or --url")
        print("\nExamples:")
        print("  python3 check_hf_deployment.py --username YOUR_HF_USERNAME")
        print("  python3 check_hf_deployment.py --url https://username-space.hf.space")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
