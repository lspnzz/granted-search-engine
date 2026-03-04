import os
import logging
import requests
from typing import List

logger = logging.getLogger(__name__)

# URL of the embeddings service (set at runtime or default to local)
EMBEDDINGS_SERVICE_URL = os.getenv("EMBEDDINGS_SERVICE_URL")


def embed_pitch(
    pitch: str,
) -> List[float]:
    """Call the embeddings service to embed a single pitch."""
    try:
        response = requests.post(
            f"{EMBEDDINGS_SERVICE_URL}/embed", json={"texts": [pitch]}, timeout=30
        )
        response.raise_for_status()
        data = response.json()
        embeddings = data.get("embeddings", [])
        return embeddings[0] if embeddings else []
    except Exception as e:
        logger.error(f"Failed to embed pitch: {type(e).__name__}: {str(e)}")
        raise RuntimeError(f"Failed to embed pitch: {str(e)}") from e
