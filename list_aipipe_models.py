#!/usr/bin/env python3
import os
import httpx

ENDPOINTS = [
    os.getenv("AI_PIPE_MODELS_URL", "https://aipipe.ai/openai/v1/models"),
    "https://aipipe.ai/v1/models",
]

def main():
    token = os.getenv("AI_PIPE_TOKEN")
    if not token:
        print("AI_PIPE_TOKEN not set in environment")
        return 1
    headers = {"Authorization": f"Bearer {token}"}
    for url in ENDPOINTS:
        try:
            print(f"Querying: {url}")
            with httpx.Client(timeout=10.0) as client:
                r = client.get(url, headers=headers)
                print(f"Status: {r.status_code}")
                print(r.text[:2000])
        except Exception as e:
            print(f"Error contacting {url}: {e}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
