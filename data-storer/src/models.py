from pydantic import BaseModel


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
