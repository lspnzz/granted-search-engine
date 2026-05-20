import logging
import os
import time
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec, CloudProvider, AwsRegion, Metric
from pydantic import BaseModel
from typing import Any
from src.models import GrantChunk


load_dotenv()
logger = logging.getLogger(__name__)


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")


def _is_mock_mode() -> bool:
    return os.getenv("GRANTED_HARNESS_MODE") == "mock"


def _client() -> Pinecone:
    return Pinecone(api_key=PINECONE_API_KEY)


class PineconeChunkRecord(BaseModel):
    """Data model for a chunk record to be stored in Pinecone."""

    id: str
    values: list[float]
    metadata: dict[str, Any]


def _create_pinecone_chunk_record(chunk: GrantChunk) -> PineconeChunkRecord:
    record_id = f"{chunk.grant_id}-{chunk.chunk_id}"
    values = chunk.embedding or []
    metadata = chunk.metadata.model_dump(
        exclude_none=True
    )  # (LS):Dropping empty fields to comply with Pinecone metadata restrictions
    return PineconeChunkRecord(
        id=record_id,
        values=values,
        metadata=metadata,
    )


def upsert_chunks_to_pinecone(
    chunks: list[GrantChunk],
    index_name: str | None,
    namespace: str,
    dimensions: int,
    host: str | None = None,
) -> None:
    if _is_mock_mode():
        logger.info(
            "Mock Pinecone upsert skipped for %d chunks into index=%s namespace=%s",
            len(chunks),
            index_name,
            namespace,
        )
        return

    if index_name:
        pc = _client()
        existing_indexes = [i.name for i in pc.list_indexes()]

        if index_name not in existing_indexes:
            logger.info(f"Creating new Pinecone index: {index_name}")
            try:
                pc.create_index(
                    name=index_name,
                    dimension=dimensions,
                    metric=Metric.COSINE,
                    spec=ServerlessSpec(
                        cloud=CloudProvider.AWS,
                        region=AwsRegion.US_EAST_1,  # (LS): Free tier defaults
                    ),
                )
                # Wait for index to be ready
                while not pc.describe_index(index_name).status.ready:
                    time.sleep(1)

                logger.info(f"Index {index_name} is ready.")
            except Exception as e:
                logger.error(f"Failed to create index {index_name}: {e}")
                raise e

        # Get host from index description if not provided or to ensure it matches
        index_description = pc.describe_index(index_name)
        host = index_description.host

    if not host:
        raise ValueError(
            "No Pinecone host could be determined (neither provided nor found via index name)."
        )

    index = _client().Index(host=host)
    BATCH_SIZE = 100

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        pinecone_chunk_records = [
            _create_pinecone_chunk_record(chunk) for chunk in batch
        ]
        index.upsert(
            namespace=namespace,
            vectors=[record.model_dump() for record in pinecone_chunk_records],
        )
