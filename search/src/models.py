from pydantic import BaseModel
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
    pitch: str
    top_k: int | None = 10
    model_name: str | None = None
    dimensions: int | None = None
    pinecone_index_name: str | None = None
    pinecone_namespace: str | None = None


class SearchResponse(BaseModel):
    pitch: str
    grants: List[Grant]
