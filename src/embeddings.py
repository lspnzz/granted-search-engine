import os, logging
from abc import ABC, abstractmethod
from typing import List

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class EmbeddingService(ABC):
    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """Get the embedding for the given text."""
        raise NotImplementedError


class OpenAIEmbeddingService(EmbeddingService):
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.EMBEDDING_MODEL = "text-embedding-3-small"

    def get_embedding(self, text: str) -> List[float]:
        res = self.client.embeddings.create(
            model=self.EMBEDDING_MODEL,
            input=[text],
        )
        return res.data[0].embedding


embedding_service = OpenAIEmbeddingService()
