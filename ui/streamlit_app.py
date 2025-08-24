"""Streamlit front-end that re-uses pure modules.

Run with:   streamlit run app/ui/streamlit_app.py
"""

import sys, pathlib

# ensure project root is on the import path
ROOT = pathlib.Path(__file__).resolve().parents[2]   # …/rentpigeon
if ROOT.as_posix() not in sys.path:
    sys.path.insert(0, ROOT.as_posix())

import re
from datetime import datetime
from typing import List, Dict, Optional

import streamlit as st

# local imports
from app.llm.extract import extract_params
from app.scraping.search import build_search_url, scrape_search
from app.scraping.detail import build_valid_detail_urls, scrape_details, canonical_detail_url

# ------------------------------------------------------------------ #
# Streamlit boilerplate

st.set_page_config(page_title="Zillow Finder", page_icon="🏡", layout="wide")

# live log
if "log_lines" not in st.session_state:
    st.session_state.log_lines: List[str] = []
def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    st.session_state.log_lines.append(line)
    st.session_state.log_placeholder.markdown("\n".join(st.session_state.log_lines))
with st.expander("🪵 Log – under the hood", expanded=False):
    st.session_state.log_placeholder = st.empty()

# ------------------------------------------------------------------ #
# Helpers that belong only to the UI layer

def clean_price(v) -> Optional[int]:
    n = re.sub(r"[^\d]", "", str(v))
    return int(n) if n.isdigit() else None

def create_card(sum_: Dict, det: Dict) -> Dict:
    card = {
        "price": sum_.get("price", "N/A"),
        "address": sum_.get("address", ""),
        "beds": sum_.get("beds", "?"),
        "baths": sum_.get("baths", "?"),
        "img": sum_.get("imgSrc"),
        "url": sum_.get("detailUrl", "#"),
    }
    for k in ("listingProviderName", "brokerName", "brokerageName", "realEstateAgentName"):
        if k in det:
            card["broker"] = det[k]; break
    for k in ("listingProviderPhoneNumber", "brokerPhone", "phone", "contactPhone"):
        if k in det:
            card["phone"] = det[k]; break
    for k in ("description", "homeDescription", "hdpText"):
        if k in det and det[k]:
            card["description"] = det[k]; break
    return card

# ------------------------------------------------------------------ #
# UI flow

query = st.text_input(
    "Find properties (e.g. 'rent apartments in Seattle under $2000')",
    placeholder="Type your search here…",
)

if st.button("Search") and query.strip():
    log(f"User query ▶️ {query}")

    # price cap extraction
    m = re.search(r"under\s*\$?([\d,]+)", query, re.I)
    max_price = int(m.group(1).replace(",", "")) if m else None
    if max_price:
        log(f"Price cap: ${max_price:,}")

    # LLM params
    params = extract_params(query)
    if not params:
        st.error("Could not interpret your search; please clarify.")
        st.stop()

    # build search URL
    search_url = build_search_url(params)
    if not search_url:
        st.error("Cannot build Zillow URL; check query.")
        st.stop()
    log(f"Search URL: {search_url}")

    # scrape search
    with st.spinner("🔍 Scraping search results…"):
        try:
            listings = scrape_search(search_url)
            log(f"Listings fetched: {len(listings)}")
        except Exception as e:
            st.error(f"Search scrape error: {e}")
            log(f"Search scrape ❌ {e}")
            st.stop()

    # build & scrape detail URLs
    det_urls = build_valid_detail_urls(listings)
    log(f"Detail scrape batch: {len(det_urls)} URLs")

    with st.spinner("📄 Fetching detailed data…"):
        try:
            det_objs = scrape_details(det_urls)
            log("Detail scrape ✅ done")
        except Exception as e:
            st.error(f"Detail scrape error: {e}")
            log(f"Detail scrape ❌ {e}")
            st.stop()

    det_lookup = {d.get("hdpUrl") or d.get("url"): d for d in det_objs}

    # Merge, filter, sort
    cards: List[Dict] = []
    for l in listings:
        zpid = str(l.get("zpid") or "")
        detail_url = canonical_detail_url(l.get("detailUrl", ""), zpid)
        if zpid and zpid not in detail_url:
            continue
        if max_price and (p := clean_price(l.get("price"))) is not None and p > max_price:
            continue
        cards.append(create_card(l, det_lookup.get(detail_url, {})))

    log(f"Listings after price filter: {len(cards)}")
    cards.sort(key=lambda c: clean_price(c["price"]) or 0)

    # Render
    if cards:
        st.subheader(f"Found {len(cards)} listing(s)")
        for idx, c in enumerate(cards, 1):
            with st.container():
                cols = st.columns([1, 3])
                if c["img"]:
                    cols[0].image(c["img"], use_container_width=True)
                info = (
                    f"### {idx}. [{c['price']}]({c['url']})\n"
                    f"{c['address']}\n{c['beds']} bd / {c['baths']} ba\n"
                    f"**Broker:** {c.get('broker','N/A')}\n"
                    f"**Phone:** {c.get('phone','N/A')}\n\n"
                    f"{c.get('description','')[:400]}{'…' if len(c.get('description',''))>400 else ''}"
                )
                cols[1].markdown(info)
    else:
        st.warning("No listings matched your criteria.")
        log("Zero listings after validation/price filter")

# reset log
if st.sidebar.button("🔄 Clear"):
    st.session_state.log_lines = []
    st.rerun()
