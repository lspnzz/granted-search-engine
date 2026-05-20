import os
import json
import re
from pathlib import Path
from typing import List

from pinecone import Pinecone
from src.models import Grant
from src.embed import get_last_mock_pitch


WORD_RE = re.compile(r"[a-z0-9]+")
STOP_WORDS = {
    "a",
    "and",
    "are",
    "for",
    "in",
    "of",
    "or",
    "the",
    "to",
    "we",
    "with",
}


def _is_mock_mode() -> bool:
    return os.getenv("GRANTED_HARNESS_MODE") == "mock"


def _fixture_path() -> Path:
    return Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "grants.json"


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in WORD_RE.findall(text.lower())
        if token not in STOP_WORDS and len(token) > 2
    }


def _query_mock_grants(query_text: str, top_k: int) -> List[Grant]:
    pitch_tokens = _tokens(query_text)
    grants = json.loads(_fixture_path().read_text(encoding="utf-8"))
    ranked = []
    for grant in grants:
        grant_text = " ".join(
            str(grant.get(field, ""))
            for field in ("id", "title", "summary", "description")
        )
        overlap = len(pitch_tokens & _tokens(grant_text))
        if overlap:
            ranked.append((overlap, grant))

    ranked.sort(key=lambda item: (-item[0], item[1]["id"]))
    max_score = ranked[0][0] if ranked else 1
    return [
        Grant(
            id=grant["id"],
            title=grant["title"],
            match_score=round(score / max_score, 4),
            amount=str(grant["total_funding_opportunity"]),
            deadline=grant["deadline_date"],
            status=grant["status"],
            url=grant["url"],
            opening_date=grant["start_date"],
        )
        for score, grant in ranked[:top_k]
    ]


def query_grants(
    query_embedding: List[float],
    index_name: str,
    namespace: str,
    top_k: int = 10,
    query_text: str | None = None,
) -> List[Grant]:
    if _is_mock_mode():
        return _query_mock_grants(query_text or get_last_mock_pitch() or "", top_k)

    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
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
                amount=str(amount_val) if amount_val is not None else None,
                deadline=metadata.get("deadline_date"),
                status=metadata.get("status"),
                url=metadata.get("url"),
                opening_date=metadata.get("start_date"),
            )
        )

    return parsed_grants
