import os
import logging
import requests
from typing import List
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2 import id_token

load_dotenv()
logger = logging.getLogger(__name__)


def search_grants(pitch: str) -> List[dict]:
    """Execute the grant search by calling the search Cloud Function API.

    Delegates to the existing search service, keeping search logic
    in a single place.
    """
    search_api_url = os.getenv("SEARCH_API_URL")
    if not search_api_url:
        raise ValueError("SEARCH_API_URL environment variable is not set")

    headers = {"Content-Type": "application/json"}

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
