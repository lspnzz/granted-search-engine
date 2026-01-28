import os
from typing import List
from dotenv import load_dotenv
from pinecone import Pinecone
from src.models import Grant

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=PINECONE_API_KEY)


def query_grants(
    query_embedding: List[float], index_name: str, namespace: str, top_k: int = 10
) -> List[Grant]:
    dense_eu_grants_index = pc.Index(name=index_name)
    response = dense_eu_grants_index.query(
        namespace=namespace,
        vector=query_embedding,
        top_k=top_k,
        include_values=False,
        include_metadata=True,
    )
    raw_grants = response["matches"]
    parsed_grants = []
    for grant in raw_grants:
        metadata = grant["metadata"]
        amount_val = metadata.get("total_funding_opportunity")

        parsed_grants.append(
            Grant(
                id=grant["id"],
                title=metadata.get("title"),
                match_score=grant["score"],
                summary=metadata.get("summary"),
                amount=str(amount_val) if amount_val is not None else None,
                deadline=metadata.get("deadline_date"),
                status=metadata.get("status"),
                url=metadata.get("url"),
                opening_date=metadata.get("start_date"),
            )
        )

    return parsed_grants
