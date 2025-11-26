#!/usr/bin/env python3
"""
Stress test: submit a burst of quiz requests (demo quiz) with random jitter
and optional waves to simulate a 'big quiz' load scenario.

This reuses the existing demo quiz URL because we rely on deterministic
fallback behavior if LLM quota/rate limits hit.
"""
import asyncio
import random
import time
import httpx
import argparse
import csv
from pathlib import Path

HF_ENDPOINT = "https://mathcsai-llm-quiz-solver.hf.space"
EMAIL = "23f2003858@ds.study.iitm.ac.in"
SECRET = "123456789"
DEMO_URL = "https://tds-llm-analysis.s-anand.net/demo"

async def submit_one(client, idx, url, delay):
    await asyncio.sleep(delay)
    payload = {"email": EMAIL, "secret": SECRET, "url": url}
    t0 = time.time()
    try:
        resp = await client.post(f"{HF_ENDPOINT}/receive_request", json=payload)
        dt = time.time() - t0
        return {
            "id": idx,
            "status": resp.status_code,
            "latency": dt,
            "delay": delay,
        }
    except Exception as e:  # noqa: BLE001
        dt = time.time() - t0
        return {"id": idx, "status": "ERR", "latency": dt, "delay": delay, "error": str(e)}

async def main():
    parser = argparse.ArgumentParser(description="Big quiz stress test")
    parser.add_argument("--requests", type=int, default=12, help="Total number of requests")
    parser.add_argument("--max-jitter", type=float, default=4.0, help="Max random start delay in seconds")
    parser.add_argument("--waves", type=int, default=1, help="Number of waves (batches)")
    parser.add_argument("--csv", type=str, default="", help="Optional CSV output path")
    args = parser.parse_args()

    per_wave = args.requests // args.waves
    remainder = args.requests % args.waves
    all_results = []
    print(f"Starting stress test: {args.requests} total requests across {args.waves} waves")

    async with httpx.AsyncClient(timeout=20.0) as client:
        current_id = 1
        for w in range(args.waves):
            count = per_wave + (1 if w < remainder else 0)
            print(f"\nWave {w+1}/{args.waves}: dispatching {count} requests")
            tasks = []
            for _ in range(count):
                delay = random.uniform(0, args.max_jitter)
                tasks.append(submit_one(client, current_id, DEMO_URL, delay))
                current_id += 1
            wave_results = await asyncio.gather(*tasks)
            all_results.extend(wave_results)

    # Aggregation
    successes = sum(1 for r in all_results if r.get("status") == 200)
    errors = [r for r in all_results if r.get("status") != 200]
    latencies = [r["latency"] for r in all_results if isinstance(r.get("latency"), (int, float))]
    avg = sum(latencies)/len(latencies) if latencies else 0.0
    p95 = sorted(latencies)[int(0.95*len(latencies))-1] if latencies else 0.0
    p99 = sorted(latencies)[int(0.99*len(latencies))-1] if latencies else 0.0

    print("\nSummary:")
    print(f"  Successful submissions: {successes}/{len(all_results)}")
    print(f"  Average latency: {avg:.2f}s | P95: {p95:.2f}s | P99: {p99:.2f}s")
    if errors:
        print("  Errors:")
        for r in errors:
            print(f"    - #{r['id']} status={r.get('status')} delay={r['delay']:.2f}s error={r.get('error','')}")

    # Optional CSV output
    if args.csv:
        out_path = Path(args.csv)
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["id", "status", "latency", "delay", "error"])
                writer.writeheader()
                for r in all_results:
                    writer.writerow({
                        "id": r.get("id"),
                        "status": r.get("status"),
                        "latency": r.get("latency"),
                        "delay": r.get("delay"),
                        "error": r.get("error", "")
                    })
            print(f"\nCSV written to: {out_path}")
        except Exception as e:  # noqa: BLE001
            print(f"\nFailed to write CSV: {e}")

if __name__ == "__main__":
    asyncio.run(main())
