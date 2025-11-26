#!/usr/bin/env python3
import os
import httpx

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not set in environment")
        return 1
    
    url = f"{GEMINI_API_URL}?key={api_key}"
    try:
        print(f"Querying: {GEMINI_API_URL}")
        with httpx.Client(timeout=10.0) as client:
            r = client.get(url)
            print(f"Status: {r.status_code}")
            print(r.text[:2000])
    except Exception as e:
        print(f"Error contacting Gemini API: {e}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
