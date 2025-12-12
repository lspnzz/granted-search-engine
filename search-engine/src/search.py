from typing import List
from src.models import Grant
from src.vectorstore import repo
from src.embeddings import embedding_service


def search(pitch: str) -> List[Grant]:
    """Search for the given pitch and return a list of relevant grants."""
    embedded_pitch = embedding_service.get_embedding(pitch)
    grants = repo.query_grants(embedded_pitch)
    return grants