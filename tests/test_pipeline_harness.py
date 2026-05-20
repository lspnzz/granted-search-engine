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


def _import_pipeline(module: str):
    _clear_src_modules()
    sys.path.insert(0, str(ROOT / "data-pipeline"))
    try:
        return importlib.import_module(module)
    finally:
        sys.path.pop(0)


def test_pipeline_request_bounds():
    models = _import_pipeline("src.models")

    with pytest.raises(ValidationError):
        models.PipelineRequest(chunk_size=99)
    with pytest.raises(ValidationError):
        models.PipelineRequest(chunk_size=8001)
    with pytest.raises(ValidationError):
        models.PipelineRequest(chunk_size=200, chunk_overlap=200)


def test_clean_and_chunk_fixture_grants():
    clean = _import_pipeline("src.transformers.clean")
    chunk = importlib.import_module("src.transformers.chunk")

    raw = json.loads((ROOT / "tests" / "fixtures" / "raw_grants.json").read_text())
    cleaned = clean.clean_grants(raw)
    chunks = chunk.chunk_grants(cleaned, chunk_size=200, chunk_overlap=20)

    assert cleaned[0].id == "GRANT-AI-HEALTH"
    assert "<p>" not in cleaned[0].description
    assert chunks
    assert chunks[0].metadata.title == "AI tools for clinical imaging"


def test_mock_embedding_adds_vectors(monkeypatch):
    monkeypatch.setenv("GRANTED_HARNESS_MODE", "mock")
    clean = _import_pipeline("src.transformers.clean")
    chunk = importlib.import_module("src.transformers.chunk")
    embed = importlib.import_module("src.transformers.embed")

    raw = json.loads((ROOT / "tests" / "fixtures" / "raw_grants.json").read_text())
    chunks = chunk.chunk_grants(clean.clean_grants(raw), chunk_size=200, chunk_overlap=20)
    embedded = embed.embed_chunks(chunks, model_name="mock", dimensions=8)

    assert embedded[0].embedding
    assert len(embedded[0].embedding) == 8
