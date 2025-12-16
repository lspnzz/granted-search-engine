import os
from typing import List

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"

client = OpenAI(api_key=OPENAI_API_KEY)


def embed_pitch(pitch: str) -> List[float]:
    res = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[pitch],
    )
    return res.data[0].embedding
