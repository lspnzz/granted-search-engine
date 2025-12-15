import logging
from src.utils import configure_logging
from src.fetch.eu_grants_fetcher import iter_grants
from src.store.objectstore import (
    store_raw_grants,
    generate_raw_grants_object_key,
    load_raw_grants,
    generate_embedded_chunks_object_key,
    load_embedded_chunks,
    store_embedded_chunks,
    mark_raw_grants_as_processed,
    mark_embedded_chunks_as_stored,
)
from src.process.clean import clean_grant
from src.process.chunk import chunk_grant
from src.process.embed import embed_chunks
from src.models import GrantChunk
from src.store.vectorstore import upsert_chunks
import functions_framework


configure_logging(log_level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_grants():
    """Fetch EU grants and store raw grants to storage."""

    # TODO(LS): Optimise with proper batching
    raw_grants = []  # (LS): Using a flat list to collect all grants

    for grant_batch in iter_grants():
        raw_grants.extend(grant_batch)
        logger.info("Fetched %d grants for current batch", len(grant_batch))

    raw_grants_object_key = generate_raw_grants_object_key()
    store_raw_grants(raw_grants_object_key, raw_grants)


def process_grants():
    """Looks for new raw grants, processes them, chunks them, embeds them, and stores results."""

    # TODO(LS): Make sure we stop if no new raw grants are found.
    raw_grants, raw_grants_object_key = load_raw_grants()  # Loading latest raw grants
    cleaned_grants = [clean_grant(grant) for grant in raw_grants]

    chunks = []
    for grant in cleaned_grants:
        grant_chunks = chunk_grant(grant)
        chunks.extend(grant_chunks)

    embedded_chunks = embed_chunks(chunks)
    embedded_chunks_object_key = generate_embedded_chunks_object_key(
        raw_grants_object_key
    )

    store_embedded_chunks(embedded_chunks_object_key, embedded_chunks)  # (LS): Stores to object store.
    mark_raw_grants_as_processed(raw_grants_object_key)


# TODO(LS): rename to avoid confusion with object store.
def store_chunks():
    chunks, chunks_object_key = load_embedded_chunks()
    grant_chunks = [GrantChunk(**row) for _, row in chunks.iterrows()]
    upsert_chunks(grant_chunks)
    mark_embedded_chunks_as_stored(chunks_object_key)


@functions_framework.http
def run_pipeline(request=None):

  # TODO(LS): Expect a payload to determine if we should fetch new grants or just reprocess existing.
  # TODO(LS): Expect parameters to chose embedding models, chuniking strategy, etc.

  request_json = request.get_json(silent=True)    
    if not request_json:
        return ({"error": "Invalid JSON or empty body provided"}, 400)  # (LS): Bad Request

  try:
    pipeline_req = PipelineRequest(**request_json)  # (LS): Validate with Pydantic

    if pipeline_req.fetch:
      fetch_grants()
    if pipeline_req.process:
      process_grants()
    if pipeline_req.store:
      store_chunks()
    
    return "Pipeline completed successfully"

  except ValidationError as e:
    logger.error(f"Validation Error: {e}")
    return ({"error": "Validation Error", "details": e.errors()}, 400)
    
  except Exception as e:
    logger.error(f"Error executing pipeline: {e}") 
    return ({"error": "Internal Server Error"}, 500)


if __name__ == "__main__":
    run_pipeline()
