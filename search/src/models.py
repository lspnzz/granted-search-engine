from pydantic import BaseModel, Field, field_validator
from typing import List


class Grant(BaseModel):
    id: str
    title: str
    match_score: float
    amount: str | None = None
    deadline: str | None = None
    status: str | None = None
    url: str | None = None
    opening_date: str | None = None


class SearchRequest(BaseModel):
    pitch: str = Field(min_length=1, max_length=8000)
    top_k: int | None = Field(default=10, ge=1, le=50)
    pinecone_index_name: str | None = Field(default=None, max_length=120)
    pinecone_namespace: str | None = Field(default=None, max_length=120)

    @field_validator("pitch")
    @classmethod
    def pitch_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("pitch must not be blank")
        return value


class SearchResponse(BaseModel):
    pitch: str
    grants: List[Grant]
