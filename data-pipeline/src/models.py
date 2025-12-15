from enum import StrEnum
from pydantic import BaseModel


class Grant(BaseModel):
    """Data model for a processed EU grant."""

    id: str
    title: str
    summary: str
    description: str
    url: str
    start_date: str
    deadline_date: str
    status: str
    total_funding_opportunity: float | None  # (LS): Assuming currency is EUR


class GrantMetadata(BaseModel):
    title: str
    url: str
    start_date: str
    deadline_date: str
    status: str
    total_funding_opportunity: float | None  # (LS): Assuming currency is EUR


class GrantChunk(BaseModel):
    """Data model representing an individual chunk derived from a grant."""

    grant_id: str
    chunk_id: int
    text: str
    embedding: list[float] | None = None
    metadata: GrantMetadata


class PipelineStep(StrEnum):
    PROCESS = "process"
    STORE = "store"


class PipelineRequest(BaseModel):
    start_from: PipelineStep | None = None
    pinecone_index_host: str | None = None
    pinecone_namespace: str | None = None

    # TODO(LS): Add chunk parameters
    # TODO(LS): Add embedding parameters
