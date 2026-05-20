from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage
import pytest
from pydantic import ValidationError


ROOT = Path(__file__).resolve().parents[1]


def _clear_src_modules() -> None:
    for name in list(sys.modules):
        if name == "src" or name.startswith("src."):
            del sys.modules[name]


def _import_agent(module: str):
    _clear_src_modules()
    sys.path.insert(0, str(ROOT / "agent"))
    try:
        return importlib.import_module(module)
    finally:
        sys.path.pop(0)


class FakeLLM:
    def __init__(self, *contents: str):
        self.contents = list(contents)

    def invoke(self, _messages):
        return AIMessage(content=self.contents.pop(0))


def test_gather_info_extracts_and_moves_to_composing(monkeypatch):
    graph = _import_agent("src.graph")
    monkeypatch.setattr(
        graph,
        "_get_llm",
        lambda: FakeLLM(
            'I can compose that now. [READY_TO_COMPOSE]\n<pitch_info>{"domain": "health", "problem": "slow imaging", "innovation": "AI triage"}</pitch_info>'
        ),
    )

    result = graph.gather_info(
        {"messages": [HumanMessage(content="health AI imaging")], "pitch_info": {}}
    )

    assert result["phase"] == "composing"
    assert result["pitch_info"]["domain"] == "health"


def test_compose_pitch_uses_fake_llm(monkeypatch):
    graph = _import_agent("src.graph")
    monkeypatch.setattr(graph, "_get_llm", lambda: FakeLLM("Composed pitch"))

    result = graph.compose_pitch(
        {
            "messages": [],
            "pitch_info": {
                "domain": "health",
                "problem": "slow imaging",
                "innovation": "AI triage",
            },
        }
    )

    assert result["phase"] == "reviewing"
    assert result["composed_pitch"] == "Composed pitch"


def test_review_pitch_approval_routes_to_searching():
    graph = _import_agent("src.graph")

    result = graph.review_pitch({"messages": [HumanMessage(content="yes, search")]})

    assert result["phase"] == "searching"


def test_execute_search_uses_injected_tool(monkeypatch):
    graph = _import_agent("src.graph")
    monkeypatch.setattr(
        graph,
        "search_grants",
        lambda pitch, request_id=None: [
            {"id": "GRANT-AI-HEALTH", "title": pitch, "match_score": 0.9}
        ],
    )

    result = graph.execute_search(
        {"composed_pitch": "AI health pitch", "request_id": "req-test"}
    )

    assert result["phase"] == "complete"
    assert result["search_results"][0]["id"] == "GRANT-AI-HEALTH"


def test_agent_request_rejects_assistant_messages_serializably():
    state = _import_agent("src.state")

    with pytest.raises(ValidationError) as exc:
        state.AgentRequest(
            thread_id="thread-test",
            messages=[{"role": "assistant", "content": "server-side only"}],
        )

    json.dumps(exc.value.errors(include_context=False))
