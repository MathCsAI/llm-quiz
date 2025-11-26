import asyncio
import sys
from typing import Optional

from fetch_utils import fetch_data

URL = "https://tds-llm-analysis.s-anand.net/demo-scrape-data?email=23f2003858%40ds.study.iitm.ac.in&id=11726"

async def main(url: Optional[str] = None):
    u = url or URL
    data, text, ct = await fetch_data(u)
    print(f"content-type: {ct}")
    if data is not None:
        print("JSON:")
        print(data)
    else:
        print("TEXT (first 300 chars):")
        print(text[:300])

if __name__ == "__main__":
    url_arg = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(main(url_arg))
