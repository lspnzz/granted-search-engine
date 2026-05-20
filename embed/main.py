import logging
import os
import hashlib
import json
import time
from uuid import uuid4

from openai import OpenAI
from firebase_functions import https_fn
from firebase_functions.params import SecretParam

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Secrets (managed via firebase functions:secrets:set)
OPENAI_API_KEY = SecretParam("OPENAI_API_KEY")


def _is_mock_mode() -> bool:
    return os.getenv("GRANTED_HARNESS_MODE") == "mock"


def _request_id(request: https_fn.Request) -> str:
    return request.headers.get("X-Request-ID") or str(uuid4())


def _log_event(event: str, **fields) -> None:
    logger.info(json.dumps({"service": "embed", "event": event, **fields}))


def _mock_embedding(text: str, dimensions: int) -> list[float]:
    values = [0.0] * dimensions
    for word in text.lower().split():
        digest = hashlib.sha256(word.encode("utf-8")).digest()
        values[int.from_bytes(digest[:2], "big") % dimensions] += 1.0
    return values


def _validate_texts(value) -> list[str]:
    if not value or not isinstance(value, list):
        raise ValueError("'texts' field must be non-empty list")
    if len(value) > 100:
        raise ValueError("'texts' field must contain at most 100 items")
    if not all(isinstance(item, str) and 0 < len(item.strip()) <= 8000 for item in value):
        raise ValueError("each text must be a non-empty string up to 8000 characters")
    return [item.strip() for item in value]


@https_fn.on_request(
    region="europe-west4",
    secrets=[OPENAI_API_KEY],
)
def embed(request: https_fn.Request) -> https_fn.Response:
    started = time.perf_counter()
    request_id = _request_id(request)
    headers = {"X-Request-ID": request_id}
    request_json = request.get_json(silent=True)

    if not request_json or "texts" not in request_json:
        return {"error": "Missing 'texts' field in request"}, 400, headers

    try:
        texts = _validate_texts(request_json.get("texts"))
    except ValueError as e:
        return {"error": str(e)}, 400, headers

    model = request_json.get("model") or os.environ.get("MODEL_NAME")
    dimensions_str = request_json.get("dimensions") or os.environ.get("DIMENSIONS")

    if not model or not dimensions_str:
        return {"error": "Missing 'model' or 'dimensions' configuration"}, 400, headers

    try:
        dimensions = int(dimensions_str)
        if dimensions < 1 or dimensions > 4096:
            return {"error": "'dimensions' must be between 1 and 4096"}, 400, headers

        _log_event(
            "request.start",
            request_id=request_id,
            mode=os.getenv("GRANTED_HARNESS_MODE", "live"),
            batch_size=len(texts),
        )

        if _is_mock_mode():
            embeddings = [_mock_embedding(text, dimensions) for text in texts]
            return {"embeddings": embeddings}, 200, headers

        client = OpenAI(api_key=OPENAI_API_KEY.value)

        # Call OpenAI embeddings API
        result = client.embeddings.create(
            model=model, input=texts, dimensions=dimensions
        )

        # Extract embeddings from response
        embeddings = [item.embedding for item in result.data]

        _log_event(
            "request.complete",
            request_id=request_id,
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
            batch_size=len(texts),
        )
        return {"embeddings": embeddings}, 200, headers
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        _log_event("request.error", request_id=request_id, error=type(e).__name__)
        return {"error": str(e)}, 500, headers
