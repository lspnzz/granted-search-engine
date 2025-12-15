import logging
import functions_framework
from pydantic import ValidationError
from src.extractors.eu_grants_fetcher import fetch_grants
from src.loaders.objectstore import store_raw_grants
from src.transformers.clean import clean_grants
from src.transformers.chunk import chunk_grants
from src.transformers.embed import embed_chunks
from src.models import Grant, PipelineRequest
from src.loaders.vectorstore import upsert_chunks_to_pinecone


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@functions_framework.http
def run_pipeline(request):

    # TODO(LS): Expect a payload to determine if we should fetch new grants or just reprocess existing.
    # TODO(LS): Expect parameters to chose embedding models, chuniking strategy, etc.

    request_json = request.get_json(silent=True)
    if not request_json:
        return (
            {"error": "Invalid JSON or empty body provided"},
            400,
        )  # (LS): Bad Request

    try:
        pipeline_req = PipelineRequest(**request_json)  # (LS): Validate with Pydantic
        if not pipeline_req.pinecone_index_host or not pipeline_req.pinecone_namespace:
            return ({"error": "Missing pinecone index or namespace"}, 400)

        INDEX_HOST = pipeline_req.pinecone_index_host
        NAMESPACE = pipeline_req.pinecone_namespace

        raw_grants = fetch_grants()
        store_raw_grants(raw_grants)
        cleaned_grants = clean_grants(raw_grants)
        chunks = chunk_grants(cleaned_grants)
        embedded_chunks = embed_chunks(chunks)
        # TODO(LS): Store embedded chunks to object store.
        # TODO(LS): Move raw grants to processed bucket.
        upsert_chunks_to_pinecone(embedded_chunks, host=INDEX_HOST, namespace=NAMESPACE)
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
