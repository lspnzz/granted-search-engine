from pydantic import BaseModel
from typing import List


class Grant(BaseModel):
    id: str
    title: str
    match_score: float


class SearchRequest(BaseModel):
    pitch: str
    top_k: int | None = 10
    model_name: str
    dimensions: int
    pinecone_index_name: str
    pinecone_namespace: str


class SearchResponse(BaseModel):
    pitch: str
    grants: List[Grant]
