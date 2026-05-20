import os
import logging
import requests
import json
import re
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2 import id_token

load_dotenv()
logger = logging.getLogger(__name__)
WORD_RE = re.compile(r"[a-z0-9]+")


def _is_mock_mode() -> bool:
    return os.getenv("GRANTED_HARNESS_MODE") == "mock"


def _fixture_path() -> Path:
    return Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "grants.json"


def _tokens(text: str) -> set[str]:
    return set(WORD_RE.findall(text.lower()))


def _mock_search(pitch: str) -> List[dict]:
    pitch_tokens = _tokens(pitch)
    grants = json.loads(_fixture_path().read_text(encoding="utf-8"))
    ranked = []
    for grant in grants:
        grant_text = " ".join(
            str(grant.get(field, ""))
            for field in ("id", "title", "summary", "description")
        )
        overlap = len(pitch_tokens & _tokens(grant_text))
        if overlap:
            ranked.append((overlap, grant))
    ranked.sort(key=lambda item: (-item[0], item[1]["id"]))
    max_score = ranked[0][0] if ranked else 1
    return [
        {
            "id": grant["id"],
            "title": grant["title"],
            "match_score": round(score / max_score, 4),
            "amount": str(grant["total_funding_opportunity"]),
            "deadline": grant["deadline_date"],
            "status": grant["status"],
            "url": grant["url"],
            "opening_date": grant["start_date"],
        }
        for score, grant in ranked[:5]
    ]


def search_grants(pitch: str, request_id: str | None = None) -> List[dict]:
    """Execute the grant search by calling the search Cloud Function API.

    Delegates to the existing search service, keeping search logic
    in a single place.
    """
    if _is_mock_mode():
        return _mock_search(pitch)

    search_api_url = os.getenv("SEARCH_API_URL")
    if not search_api_url:
        raise ValueError("SEARCH_API_URL environment variable is not set")

    headers = {"Content-Type": "application/json"}
    if request_id:
        headers["X-Request-ID"] = request_id

    # Authenticate with Google Cloud if running on Cloud Run
    try:
        token = id_token.fetch_id_token(Request(), search_api_url)
        headers["Authorization"] = f"Bearer {token}"
    except Exception:
        # Running locally — no auth needed
        logger.info("No Google Auth available, calling search API directly")

    payload = {"pitch": pitch}

    response = requests.post(search_api_url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()

    data = response.json()
    grants = data.get("grants", [])

    logger.info(f"Search returned {len(grants)} grants for pitch: {pitch[:80]}...")
    return grants
