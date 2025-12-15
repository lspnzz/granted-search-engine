import os
from dotenv import load_dotenv
from openai import OpenAI
from src.models import GrantChunk

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 100

client = OpenAI(api_key=OPENAI_API_KEY)


def embed_chunks(chunks: list[GrantChunk]) -> list[GrantChunk]:
    """Return a list of GrantChunk with an 'embedding' field added."""

    texts = [chunk.text for chunk in chunks]

    for batch_start in range(0, len(texts), BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        batch = texts[batch_start:batch_end]

        try:
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=batch,
            )
        except Exception as e:
            raise RuntimeError(
                f"Embedding batch {batch_start}:{batch_end} failed"
            ) from e

        # Assign embeddings directly back to the matching chunks
        for offset, item in enumerate(response.data):
            chunks[batch_start + offset].embedding = item.embedding

    return chunks
