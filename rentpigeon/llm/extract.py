"""LLM helper – turn a free-text real-estate query into structured params.

Returned dict keys:
    - homeType  (str, default 'homes')
    - zipcode   (str)
    - city      (str)
    - state     (str)
"""

import os
import json
import re
from typing import Optional, Dict

from openai import OpenAI

# ------------------------------------------------------------------ #
# initialise client once per process
_api_key = os.getenv("OPEN_AI")
if not _api_key:                       # fail fast
    raise RuntimeError("Missing OPEN_AI environment variable")
_client = OpenAI(api_key=_api_key)

# ------------------------------------------------------------------ #


def _safe_json(txt: str) -> Optional[Dict]:
    """Be lenient with code-fenced or partial JSON outputs."""
    try:
        return json.loads(txt)
    except Exception:
        i, j = txt.find("{"), txt.rfind("}")
        if 0 <= i < j:
            try:
                return json.loads(txt[i : j + 1])
            except Exception:
                return None
        return None


def extract_params(query: str) -> Optional[Dict]:
    """Return dict on success, else None."""
    system_msg = (
        "Parse any real-estate query into JSON keys "
        "homeType, zipcode, city, state; default homeType='homes'."
    )

    resp = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": query},
        ],
        temperature=0,
    )
    raw = re.sub(r"^```[\w]*|```$", "", resp.choices[0].message.content.strip(), flags=re.MULTILINE)
    return _safe_json(raw)
