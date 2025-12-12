from pydantic import BaseModel
from typing import List


class Grant(BaseModel):
    id: str
    title: str
    match_score: float


class SearchRequest(BaseModel):
    pitch: str


class SearchResponse(BaseModel):
    pitch: str
    grants: List[Grant]
