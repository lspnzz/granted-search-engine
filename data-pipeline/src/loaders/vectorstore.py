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
pc = Pinecone(api_key=PINECONE_API_KEY)


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


def upsert_chunks_to_pinecone(chunks: list[GrantChunk], host: str, namespace: str) -> None:
    index = pc.Index(host=host)
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
