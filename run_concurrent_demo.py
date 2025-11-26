#!/usr/bin/env python3
import asyncio
import httpx
import time
import argparse

HF_ENDPOINT = "https://mathcsai-llm-quiz-solver.hf.space"
EMAIL = "23f2003858@ds.study.iitm.ac.in"
SECRET = "123456789"
DEFAULT_URL = "https://tds-llm-analysis.s-anand.net/demo"
TIMEOUT = 12.0

async def fire_one(client, idx, quiz_url):
    payload = {"email": EMAIL, "secret": SECRET, "url": quiz_url}
    t0 = time.time()
    try:
        resp = await client.post(f"{HF_ENDPOINT}/receive_request", json=payload)
        dt = time.time() - t0
        body = None
        try:
            body = resp.json()
        except Exception:
            body = resp.text[:200]
        return {"id": idx, "status": resp.status_code, "latency": dt, "body": body}
    except Exception as e:
        dt = time.time() - t0
        return {"id": idx, "status": "ERR", "latency": dt, "error": str(e)}

async def main():
    parser = argparse.ArgumentParser(description="Run concurrent demo submissions")
    parser.add_argument("--concurrency", type=int, default=5, help="Number of concurrent requests")
    parser.add_argument("--url", type=str, default=DEFAULT_URL, help="Quiz URL to submit")
    args = parser.parse_args()

    print(f"Submitting {args.concurrency} concurrent runs to {HF_ENDPOINT} ...")
    print(f"Quiz URL: {args.url}")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        tasks = [fire_one(client, i+1, args.url) for i in range(args.concurrency)]
        results = await asyncio.gather(*tasks)
    # Summary
    ok = sum(1 for r in results if r.get("status") == 200)
    errs = [r for r in results if r.get("status") != 200]
    latencies = [r["latency"] for r in results if isinstance(r.get("latency"), (int, float))]
    avg = sum(latencies)/len(latencies) if latencies else 0
    sorted_lats = sorted(latencies)
    def pct(p):
        if not sorted_lats:
            return 0
        idx = max(0, min(len(sorted_lats)-1, int(p*len(sorted_lats)) - 1))
        return sorted_lats[idx]
    p95 = pct(0.95)
    p99 = pct(0.99)
    print("\nResults:")
    for r in results:
        print(f" - #{r['id']}: status={r.get('status')} latency={r['latency']:.2f}s")
    print(f"\nAccepted: {ok}/{len(results)}")
    print(f"Avg latency: {avg:.2f}s | P95 latency: {p95:.2f}s | P99 latency: {p99:.2f}s")
    if errs:
        print("\nFailures:")
        for r in errs:
            print(f" - #{r['id']}: status={r.get('status')} error={r.get('error','')} body={r.get('body','')}")

if __name__ == "__main__":
    asyncio.run(main())
