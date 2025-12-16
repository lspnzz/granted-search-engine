from pydantic import BaseModel
from typing import List


class Grant(BaseModel):
    id: str
    title: str
    match_score: float


class SearchRequest(BaseModel):
    pitch: str
    top_k: int | None = 10
    pinecone_index_host: str | None = None
    pinecone_namespace: str | None = None


class SearchResponse(BaseModel):
    pitch: str
    grants: List[Grant]
