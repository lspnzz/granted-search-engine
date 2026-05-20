from dotenv import load_dotenv
import os
import logging
import json
import time
from uuid import uuid4
import functions_framework
from pydantic import ValidationError
from src.extractors.eu_grants_fetcher import fetch_grants
from src.loaders.objectstore import (
    store_raw_grants,
    load_raw_grants,
    store_clean_grants,
)
from src.transformers.clean import clean_grants
from src.transformers.chunk import chunk_grants
from src.transformers.embed import embed_chunks
from src.models import PipelineRequest
from src.loaders.vectorstore import upsert_chunks_to_pinecone


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


load_dotenv()


def _request_id(request) -> str:
    return request.headers.get("X-Request-ID") or str(uuid4())


def _log_event(event: str, **fields) -> None:
    logger.info(json.dumps({"service": "data-pipeline", "event": event, **fields}))


@functions_framework.http
def run_pipeline(request):
    started = time.perf_counter()
    request_id = _request_id(request)
    headers = {"X-Request-ID": request_id}
    request_json = request.get_json(silent=True)
    if not request_json:
        return (
            {"error": "Invalid JSON or empty body provided"},
            400,
            headers,
        )  # (LS): Bad Request

    try:
        _log_event("request.start", request_id=request_id, mode=os.getenv("GRANTED_HARNESS_MODE", "live"))
        # (LS): Validate with Pydantic
        pipeline_req = PipelineRequest(**request_json)

        # Config extraction (Request > Env > Default)
        INDEX_NAME = pipeline_req.pinecone_index_name or os.getenv(
            "PINECONE_INDEX_NAME"
        )

        NAMESPACE = pipeline_req.pinecone_namespace or os.getenv("PINECONE_NAMESPACE")

        _chunk_size = pipeline_req.chunk_size or os.getenv("CHUNK_SIZE")
        CHUNK_SIZE = int(_chunk_size) if _chunk_size else None

        _chunk_overlap = pipeline_req.chunk_overlap or os.getenv("CHUNK_OVERLAP")
        CHUNK_OVERLAP = int(_chunk_overlap) if _chunk_overlap else None

        MODEL_NAME = pipeline_req.model_name or os.getenv("MODEL_NAME")

        _dimensions = pipeline_req.dimensions or os.getenv("DIMENSIONS")
        DIMENSIONS = int(_dimensions) if _dimensions else None

        if CHUNK_SIZE is not None and not 100 <= CHUNK_SIZE <= 8000:
            return (
                {"error": "CHUNK_SIZE must be between 100 and 8000"},
                400,
                headers,
            )

        if CHUNK_OVERLAP is not None and not 0 <= CHUNK_OVERLAP <= 10000:
            return (
                {"error": "CHUNK_OVERLAP must be between 0 and 10000"},
                400,
                headers,
            )

        if (
            CHUNK_SIZE is not None
            and CHUNK_OVERLAP is not None
            and CHUNK_OVERLAP >= CHUNK_SIZE
        ):
            return (
                {"error": "CHUNK_OVERLAP must be smaller than CHUNK_SIZE"},
                400,
                headers,
            )

        if (
            not INDEX_NAME
            or not NAMESPACE
            or not CHUNK_SIZE
            or not CHUNK_OVERLAP
            or not MODEL_NAME
            or not DIMENSIONS
        ):
            missing_params = [
                k
                for k, v in {
                    "INDEX_NAME": INDEX_NAME,
                    "NAMESPACE": NAMESPACE,
                    "CHUNK_SIZE": CHUNK_SIZE,
                    "CHUNK_OVERLAP": CHUNK_OVERLAP,
                    "MODEL_NAME": MODEL_NAME,
                    "DIMENSIONS": DIMENSIONS,
                }.items()
                if not v
            ]
            return (
                {"error": f"Missing required parameters: {', '.join(missing_params)}"},
                400,
            )

        grants_filename = pipeline_req.load_grants_from_file

        if grants_filename:
            raw_grants = load_raw_grants(grants_filename)
            logger.info(f"Loaded {len(raw_grants)} grants from file: {grants_filename}")
        else:
            raw_grants = fetch_grants()
            store_raw_grants(raw_grants)
            logger.info(f"Fetched {len(raw_grants)} grants")

        logger.info("Starting grants cleaning...")
        cleaned_grants = clean_grants(raw_grants)
        store_clean_grants(cleaned_grants)
        logger.info(f"Grants cleaned: {len(cleaned_grants)}")
        chunks = chunk_grants(
            cleaned_grants, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        )
        logger.info(f"Chunks created: {len(chunks)}")
        embedded_chunks = embed_chunks(
            chunks, model_name=MODEL_NAME, dimensions=DIMENSIONS
        )
        logger.info(f"Chunks embedded: {len(embedded_chunks)}")
        # TODO(LS): Store embedded chunks to object store.
        # TODO(LS): Move raw grants to processed bucket.
        upsert_chunks_to_pinecone(
            embedded_chunks,
            index_name=INDEX_NAME,
            namespace=NAMESPACE,
            dimensions=DIMENSIONS,
        )
        logger.info("Chunks upserted to Pinecone")
        # TODO(LS): Move embedded chunks to processed bucket.
        _log_event(
            "request.complete",
            request_id=request_id,
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
            raw_grants=len(raw_grants),
            chunks=len(chunks),
        )
        return "Pipeline completed successfully", 200, headers

    except ValidationError as e:
        logger.error(f"Validation Error: {e}")
        return (
            {"error": "Validation Error", "details": e.errors(include_context=False)},
            400,
            headers,
        )

    except Exception as e:
        logger.error(f"Error executing pipeline: {e}")
        _log_event("request.error", request_id=request_id, error=type(e).__name__)
        return ({"error": "Internal Server Error"}, 500, headers)


if __name__ == "__main__":
    run_pipeline()
