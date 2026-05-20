import hashlib
import json
import os
import logging
import requests
from typing import List

logger = logging.getLogger(__name__)

# URL of the embeddings service (set at runtime or default to local)
EMBEDDINGS_SERVICE_URL = os.getenv("EMBEDDINGS_SERVICE_URL")
MOCK_DIMENSIONS = 32
_LAST_MOCK_PITCH: str | None = None


def _is_mock_mode() -> bool:
    return os.getenv("GRANTED_HARNESS_MODE") == "mock"


def _mock_embedding(text: str, dimensions: int = MOCK_DIMENSIONS) -> List[float]:
    values = [0.0] * dimensions
    for word in text.lower().split():
        digest = hashlib.sha256(word.encode("utf-8")).digest()
        values[int.from_bytes(digest[:2], "big") % dimensions] += 1.0
    return values


def get_last_mock_pitch() -> str | None:
    return _LAST_MOCK_PITCH


def _log_event(event: str, **fields) -> None:
    logger.info(json.dumps({"service": "search", "event": event, **fields}))


def embed_pitch(
    pitch: str,
    request_id: str | None = None,
) -> List[float]:
    """Call the embeddings service to embed a single pitch."""
    global _LAST_MOCK_PITCH
    if _is_mock_mode():
        _LAST_MOCK_PITCH = pitch
        _log_event("embedding.mock", request_id=request_id, text_length=len(pitch))
        return _mock_embedding(pitch)

    if not EMBEDDINGS_SERVICE_URL:
        raise RuntimeError("EMBEDDINGS_SERVICE_URL is not set")

    try:
        response = requests.post(
            f"{EMBEDDINGS_SERVICE_URL}/embed",
            json={"texts": [pitch]},
            headers={"X-Request-ID": request_id} if request_id else None,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        embeddings = data.get("embeddings", [])
        return embeddings[0] if embeddings else []
    except Exception as e:
        logger.error(f"Failed to embed pitch: {type(e).__name__}: {str(e)}")
        raise RuntimeError(f"Failed to embed pitch: {str(e)}") from e
