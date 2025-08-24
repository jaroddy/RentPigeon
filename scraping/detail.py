"""Detail-page helpers – URL validation + full property scrape."""

import asyncio
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin

import app.scraping.zillow as zillow


def canonical_detail_url(url: str, zpid: str) -> str:
    """Ensure URL is absolute and contains zpid."""
    if zpid and zpid not in url:
        return f"https://www.zillow.com/homedetails/{zpid}_zpid/"
    if url.startswith("/"):
        return urljoin("https://www.zillow.com", url)
    return url


def build_valid_detail_urls(search_rows: List[Dict]) -> List[str]:
    """From raw search rows → list of validated detail URLs."""
    out: List[str] = []
    for row in search_rows:
        zpid = str(row.get("zpid") or "")
        url = canonical_detail_url(row.get("detailUrl", ""), zpid)
        if zpid and url and zpid in url:
            out.append(url)
    return out


async def _async_scrape(urls: List[str]) -> List[Dict]:
    return await zillow.scrape_properties(urls)


def scrape_details(urls: List[str]) -> List[Dict]:
    """Blocking wrapper; fetch detail JSONs for a batch of URLs."""
    return asyncio.run(_async_scrape(urls))
