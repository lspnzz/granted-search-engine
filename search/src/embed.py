import os
from typing import List

from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


def embed_pitch(
    pitch: str,
    model: str,
    dimensions: int,
) -> List[float]:
    res = client.embeddings.create(
        model=model,
        input=[pitch],
        dimensions=dimensions,
    )
    return res.data[0].embedding
