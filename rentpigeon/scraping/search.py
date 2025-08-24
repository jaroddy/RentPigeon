"""Search-page scraping utilities (summary rows only)."""

from typing import List, Dict, Optional

import app.scraping.zillow as zillow
import asyncio
from urllib.parse import urljoin


def build_search_url(params: Dict) -> Optional[str]:
    """Compose a Zillow search URL from the LLM params."""
    home = params.get("homeType", "homes").strip("/")
    zp, city, st_ = params.get("zipcode", ""), params.get("city", ""), params.get("state", "")

    if zp:
        base = f"https://www.zillow.com/{zp}/"
    elif city and st_:
        base = f"https://www.zillow.com/{city}-{st_}/"
    elif city:
        base = f"https://www.zillow.com/{city}/"
    else:
        return None

    if home and home not in ("homes", ""):
        base += f"{home}/"

    return base


async def _async_scrape(url: str, max_pages: int | None = None) -> List[Dict]:
    return await zillow.scrape_search(url=url, max_scrape_pages=max_pages)


def scrape_search(url: str, max_pages: int | None = None) -> List[Dict]:
    """Blocking wrapper around the async scrapfly call so callers don’t need asyncio."""
    return asyncio.run(_async_scrape(url, max_pages=max_pages))
