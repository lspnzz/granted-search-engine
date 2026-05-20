from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError


ROOT = Path(__file__).resolve().parents[1]


def _clear_src_modules() -> None:
    for name in list(sys.modules):
        if name == "src" or name.startswith("src."):
            del sys.modules[name]


def _import_search(module: str):
    _clear_src_modules()
    sys.path.insert(0, str(ROOT / "search"))
    try:
        return importlib.import_module(module)
    finally:
        sys.path.pop(0)


def test_search_request_rejects_blank_pitch():
    models = _import_search("src.models")

    with pytest.raises(ValidationError):
        models.SearchRequest(pitch="   ")


def test_validation_errors_are_json_serializable_without_context():
    models = _import_search("src.models")

    with pytest.raises(ValidationError) as exc:
        models.SearchRequest(pitch="   ")

    json.dumps(exc.value.errors(include_context=False))


def test_mock_search_returns_fixture_results(monkeypatch):
    monkeypatch.setenv("GRANTED_HARNESS_MODE", "mock")
    embed = _import_search("src.embed")
    vectorstore = importlib.import_module("src.vectorstore")

    embedding = embed.embed_pitch("AI medical imaging for hospitals")
    grants = vectorstore.query_grants(
        embedding,
        index_name="mock",
        namespace="mock",
        query_text="AI medical imaging for hospitals",
    )

    assert grants
    assert grants[0].id == "GRANT-AI-HEALTH"


def test_live_embed_requires_service_url(monkeypatch):
    monkeypatch.delenv("GRANTED_HARNESS_MODE", raising=False)
    monkeypatch.delenv("EMBEDDINGS_SERVICE_URL", raising=False)
    embed = _import_search("src.embed")

    with pytest.raises(RuntimeError, match="EMBEDDINGS_SERVICE_URL"):
        embed.embed_pitch("test")
