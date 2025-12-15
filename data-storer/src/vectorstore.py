import logging
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from pydantic import BaseModel
from typing import Any
from src.models import GrantChunk


load_dotenv()
logger = logging.getLogger(__name__)


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_HOST = os.getenv("EU_GRANT_CHUNKS_INDEX_HOST")
NAMESPACE = os.getenv("EU_GRANT_CHUNKS_NAMESPACE")

if not PINECONE_API_KEY or not INDEX_HOST or not NAMESPACE:
    raise RuntimeError(
        "Set environment variables before using Pinecone.\n"
        f" Missing: {'PINECONE_API_KEY' if not PINECONE_API_KEY else ''}"
        f" {'EU_GRANT_CHUNKS_INDEX_HOST' if not INDEX_HOST else ''}"
        f" {'EU_GRANT_CHUNKS_NAMESPACE' if not NAMESPACE else ''}"
    )

pc = Pinecone(api_key=PINECONE_API_KEY)


class PineconeChunkRecord(BaseModel):
    """Data model for a chunk record to be stored in Pinecone."""

    id: str
    values: list[float]
    metadata: dict[str, Any]


def create_pinecone_chunk_record(chunk: GrantChunk) -> PineconeChunkRecord:
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


def upsert_chunks(chunks: list[GrantChunk]) -> None:
    index = pc.Index(host=INDEX_HOST)
    BATCH_SIZE = 100

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        pinecone_chunk_records = [
            create_pinecone_chunk_record(chunk) for chunk in batch
        ]
        index.upsert(
            namespace=NAMESPACE,
            vectors=[record.model_dump() for record in pinecone_chunk_records],
        )
