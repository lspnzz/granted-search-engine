import logging
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


@functions_framework.http
def run_pipeline(request):
    # TODO(LS): Expect parameters to chose embedding models, chuniking strategy, etc.

    request_json = request.get_json(silent=True)
    if not request_json:
        return (
            {"error": "Invalid JSON or empty body provided"},
            400,
        )  # (LS): Bad Request

    try:
        pipeline_req = PipelineRequest(**request_json)  # (LS): Validate with Pydantic
        if (
            not pipeline_req.pinecone_index_name
            and not pipeline_req.pinecone_index_host
        ):
            return ({"error": "Missing pinecone index name (or host)"}, 400)

        if not pipeline_req.pinecone_namespace:
            return ({"error": "Missing pinecone namespace"}, 400)

        # Config extraction
        INDEX_NAME = pipeline_req.pinecone_index_name
        # Fallback to host if name not provided (backward compatibility)
        INDEX_HOST = pipeline_req.pinecone_index_host
        NAMESPACE = pipeline_req.pinecone_namespace

        CHUNK_SIZE = pipeline_req.chunk_size
        CHUNK_OVERLAP = pipeline_req.chunk_overlap
        MODEL_NAME = pipeline_req.model_name
        DIMENSIONS = pipeline_req.dimensions

        grants_filename = pipeline_req.load_grants_from_file

        if grants_filename:
            raw_grants = load_raw_grants(grants_filename)
            logger.info(f"Loaded {len(raw_grants)} grants from file: {grants_filename}")
        else:
            raw_grants = fetch_grants()
            store_raw_grants(raw_grants)
            logger.info(f"Fetched {len(raw_grants)} grants")

        logger.info(f"Starting grants cleaning...")
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
            host=INDEX_HOST,  # Pass host for backward compatibility if name is missing
        )
        logger.info(f"Chunks upserted to Pinecone")
        # TODO(LS): Move embedded chunks to processed bucket.
        return "Pipeline completed successfully"

    except ValidationError as e:
        logger.error(f"Validation Error: {e}")
        return ({"error": "Validation Error", "details": e.errors()}, 400)

    except Exception as e:
        logger.error(f"Error executing pipeline: {e}")
        return ({"error": "Internal Server Error"}, 500)


if __name__ == "__main__":
    run_pipeline()
