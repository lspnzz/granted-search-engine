import os
from typing import List

from openai import OpenAI


def embed_pitch(
    pitch: str,
    model: str,
    dimensions: int,
) -> List[float]:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    res = client.embeddings.create(
        model=model,
        input=[pitch],
        dimensions=dimensions,
    )
    return res.data[0].embedding
