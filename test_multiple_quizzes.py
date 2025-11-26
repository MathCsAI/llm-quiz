#!/usr/bin/env python3
"""
Test multiple quiz submissions to HuggingFace Space
Submits 25 quiz requests and tracks results
"""
import asyncio
import httpx
import time
from typing import List, Dict, Any

HF_ENDPOINT = "https://mathcsai-llm-quiz-solver.hf.space"
EMAIL = "23f2003858@ds.study.iitm.ac.in"
SECRET = "123456789"
DEMO_URL = "https://tds-llm-analysis.s-anand.net/demo"

async def submit_quiz(client: httpx.AsyncClient, quiz_id: int, url: str) -> Dict[str, Any]:
    """Submit a single quiz and return result"""
    payload = {
        "email": EMAIL,
        "secret": SECRET,
        "url": url
    }
    
    start_time = time.time()
    try:
        response = await client.post(
            f"{HF_ENDPOINT}/receive_request",
            json=payload,
            timeout=30.0
        )
        elapsed = time.time() - start_time
        
        return {
            "id": quiz_id,
            "status": response.status_code,
            "elapsed": elapsed,
            "success": response.status_code == 200,
            "response": response.json() if response.status_code == 200 else response.text[:100]
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "id": quiz_id,
            "status": "ERROR",
            "elapsed": elapsed,
            "success": False,
            "error": str(e)[:100]
        }

async def test_batch(batch_num: int, batch_size: int, delay_between: float = 0.5) -> List[Dict[str, Any]]:
    """Test a batch of quizzes with delays"""
    print(f"\n{'='*70}")
    print(f"BATCH {batch_num}: Submitting {batch_size} quizzes")
    print(f"{'='*70}")
    
    results = []
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i in range(batch_size):
            quiz_id = (batch_num - 1) * batch_size + i + 1
            print(f"Submitting quiz #{quiz_id}...", end=" ", flush=True)
            
            result = await submit_quiz(client, quiz_id, DEMO_URL)
            results.append(result)
            
            status_icon = "✅" if result["success"] else "❌"
            print(f"{status_icon} {result['status']} ({result['elapsed']:.2f}s)")
            
            # Small delay between requests to avoid overwhelming the server
            if i < batch_size - 1:
                await asyncio.sleep(delay_between)
    
    return results

def print_summary(all_results: List[Dict[str, Any]]):
    """Print summary statistics"""
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    total = len(all_results)
    successful = sum(1 for r in all_results if r["success"])
    failed = total - successful
    
    elapsed_times = [r["elapsed"] for r in all_results]
    avg_time = sum(elapsed_times) / len(elapsed_times) if elapsed_times else 0
    min_time = min(elapsed_times) if elapsed_times else 0
    max_time = max(elapsed_times) if elapsed_times else 0
    
    print(f"\nTotal quizzes: {total}")
    print(f"✅ Successful: {successful} ({successful/total*100:.1f}%)")
    print(f"❌ Failed: {failed} ({failed/total*100:.1f}%)")
    print(f"\nTiming:")
    print(f"  Average: {avg_time:.2f}s")
    print(f"  Min: {min_time:.2f}s")
    print(f"  Max: {max_time:.2f}s")
    
    if failed > 0:
        print(f"\nFailed submissions:")
        for r in all_results:
            if not r["success"]:
                error_msg = r.get("error", r.get("response", "Unknown"))
                print(f"  Quiz #{r['id']}: {r['status']} - {error_msg}")
    
    # Status code breakdown
    status_counts = {}
    for r in all_results:
        status = r["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"\nStatus code breakdown:")
    for status, count in sorted(status_counts.items(), key=lambda x: str(x[0])):
        print(f"  {status}: {count}")
    
    print(f"\n{'='*70}")

async def main():
    """Main test runner"""
    print(f"\n{'='*70}")
    print("MULTIPLE QUIZ TEST - HUGGINGFACE SPACE")
    print(f"{'='*70}")
    print(f"Endpoint: {HF_ENDPOINT}")
    print(f"Quiz URL: {DEMO_URL}")
    print(f"Test plan: 1 batch of 25 quizzes")
    print(f"{'='*70}")
    
    # Check health first
    print("\nChecking HF Space health...", end=" ", flush=True)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(HF_ENDPOINT)
            if response.status_code == 200:
                print("✅ Online")
            else:
                print(f"⚠️  Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Run test batch
    start_time = time.time()
    all_results = await test_batch(batch_num=1, batch_size=25, delay_between=0.5)
    total_time = time.time() - start_time
    
    # Print summary
    print_summary(all_results)
    print(f"\nTotal test duration: {total_time:.1f}s")
    print(f"Average throughput: {len(all_results)/total_time:.2f} requests/second")

if __name__ == "__main__":
    asyncio.run(main())
