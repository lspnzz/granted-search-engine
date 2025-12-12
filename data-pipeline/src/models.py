from typing import Any
from pydantic import BaseModel


__all__ = ["Grant", "GrantChunk"]


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
    total_funding_opportunity: float  # (LS): Assuming currency is EUR


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
