import asyncio
from typing import Any, Optional, Tuple

import httpx

DEFAULT_TIMEOUT = 15.0
MAX_RETRIES = 3
BACKOFF_BASE = 0.6

class FetchError(Exception):
    pass

async def fetch_data(url: str, *, headers: Optional[dict] = None, timeout: float = DEFAULT_TIMEOUT) -> Tuple[Optional[Any], str, str]:
    """
    Fetch data from URL. If content-type is JSON, parse and return (json, raw_text, content_type).
    Otherwise, return (None, raw_text, content_type).
    Retries on network/timeouts and JSON decode errors, with backoff.
    """
    attempt = 0
    last_text = ""
    last_ct = ""
    async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
        while attempt < MAX_RETRIES:
            try:
                resp = await client.get(url, headers=headers)
                ct = resp.headers.get("content-type", "").lower()
                text = resp.text
                last_text = text
                last_ct = ct

                if "application/json" in ct:
                    try:
                        data = resp.json()
                        return data, text, ct
                    except Exception:
                        # JSON stated but not decodable, try again with backoff
                        attempt += 1
                        await asyncio.sleep(BACKOFF_BASE * (2 ** (attempt - 1)))
                        continue
                else:
                    # Non-JSON: return raw text for caller to handle
                    return None, text, ct
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                attempt += 1
                await asyncio.sleep(BACKOFF_BASE * (2 ** (attempt - 1)))
                if attempt >= MAX_RETRIES:
                    raise FetchError(f"Network error after {MAX_RETRIES} attempts: {e}")
        # If we exhausted retries due to JSON decode issues
        raise FetchError(f"Failed to decode JSON from content-type '{last_ct}'. Body starts: {last_text[:120]!r}")
