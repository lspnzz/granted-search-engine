import os
import hashlib
import logging
import requests
from src.models import GrantChunk

logger = logging.getLogger(__name__)

BATCH_SIZE = 100
EMBEDDINGS_SERVICE_URL = os.getenv("EMBEDDINGS_SERVICE_URL")


def _is_mock_mode() -> bool:
    return os.getenv("GRANTED_HARNESS_MODE") == "mock"


def _mock_embedding(text: str, dimensions: int) -> list[float]:
    values = [0.0] * dimensions
    for word in text.lower().split():
        digest = hashlib.sha256(word.encode("utf-8")).digest()
        values[int.from_bytes(digest[:2], "big") % dimensions] += 1.0
    return values


def embed_chunks(
    chunks: list[GrantChunk], model_name: str, dimensions: int = 1536
) -> list[GrantChunk]:
    """Return a list of GrantChunk with an 'embedding' field added."""

    texts = [chunk.text for chunk in chunks]
    if _is_mock_mode():
        for chunk in chunks:
            chunk.embedding = _mock_embedding(chunk.text, dimensions)
        return chunks

    if not EMBEDDINGS_SERVICE_URL:
        raise RuntimeError("EMBEDDINGS_SERVICE_URL is not set")

    for batch_start in range(0, len(texts), BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        batch = texts[batch_start:batch_end]

        try:
            # Call embeddings API
            response = requests.post(
                f"{EMBEDDINGS_SERVICE_URL}/embed",
                # TODO(IZ): add thr auth token, folow the search Fe
                json={"texts": batch, "model": model_name, "dimensions": dimensions},
                timeout=30,
            )
            # we want to raise before we parse bad responses
            response.raise_for_status()
            
            data = response.json()
            embeddings = data.get("embeddings", [])
        except Exception as e:
            logger.error(
                f"Embedding batch {batch_start}:{batch_end} failed: {type(e).__name__}: {str(e)}"
            )
            raise RuntimeError(
                f"Embedding batch {batch_start}:{batch_end} failed"
            ) from e

        # Assign embeddings directly back to the matching chunks
        for offset, embedding in enumerate(embeddings):
            chunks[batch_start + offset].embedding = embedding

    return chunks
