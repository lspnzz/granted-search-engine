from pydantic import BaseModel, Field, model_validator


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


class PipelineRequest(BaseModel):
    load_grants_from_file: str | None = Field(default=None, max_length=240)
    pinecone_index_name: str | None = Field(default=None, max_length=120)
    pinecone_namespace: str | None = Field(default=None, max_length=120)

    # Configuration Parameters
    model_name: str | None = Field(default=None, max_length=120)
    dimensions: int | None = Field(default=None, ge=1, le=4096)
    chunk_size: int | None = Field(default=None, ge=100, le=8000)
    chunk_overlap: int | None = Field(default=None, ge=0, le=10000)

    @model_validator(mode="after")
    def chunk_overlap_must_be_smaller_than_size(self):
        if (
            self.chunk_size is not None
            and self.chunk_overlap is not None
            and self.chunk_overlap >= self.chunk_size
        ):
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        return self
