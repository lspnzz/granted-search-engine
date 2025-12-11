import os, logging
from abc import ABC, abstractmethod
from typing import List

from dotenv import load_dotenv
from pinecone import Pinecone

from src.models import Grant

load_dotenv()
logger = logging.getLogger(__name__)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
EU_GRANT_CHUNKS_INDEX_HOST = os.getenv("EU_GRANT_CHUNKS_INDEX_HOST")
EU_GRANT_CHUNKS_NAMESPACE = os.getenv("EU_GRANT_CHUNKS_NAMESPACE")


class VectorRepository(ABC):
    @abstractmethod
    def query_grants(self, query_embedding: List[float]) -> List[Grant]:
        """Query the vector store for relevant grants based on the input text."""
        raise NotImplementedError


class PineconeRepository(VectorRepository):
    def __init__(self):
        logger.info("Initializing Pinecone client")

        if (
            not PINECONE_API_KEY
            or not EU_GRANT_CHUNKS_INDEX_HOST
            or not EU_GRANT_CHUNKS_NAMESPACE
        ):
            raise RuntimeError(
                f"Set environment variables before using Pinecone.\\n Missing: {'PINECONE_API_KEY' if not PINECONE_API_KEY else ''} {'EU_GRANT_CHUNKS_INDEX_HOST' if not EU_GRANT_CHUNKS_INDEX_HOST else ''} {'EU_GRANT_CHUNKS_NAMESPACE' if not EU_GRANT_CHUNKS_NAMESPACE else ''}"
            )

        logger.info("Creating Pinecone client")
        self.pc = Pinecone(api_key=PINECONE_API_KEY)

    def query_grants(self, query_embedding: List[float]) -> List[Grant]:
        dense_eu_grants_index = self.pc.Index(host=EU_GRANT_CHUNKS_INDEX_HOST)
        response = dense_eu_grants_index.query(
            namespace=EU_GRANT_CHUNKS_NAMESPACE,
            vector=query_embedding,
            top_k=10,
            include_values=False,
            include_metadata=True,
        )
        raw_grants = response["matches"]
        logger.info(f"Retrieved {len(raw_grants)} grants from Pinecone.")
        parsed_grants = [
            Grant(
                id=grant["id"],
                title=grant["metadata"]["title"],
                match_score=grant["score"],
            )
            for grant in raw_grants
        ]

        return parsed_grants


repo = PineconeRepository()