from typing import Optional, Literal
from pydantic import BaseModel
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages


class PitchInfo(BaseModel):
    """Structured information extracted from the user's project description."""

    domain: Optional[str] = None
    problem: Optional[str] = None
    innovation: Optional[str] = None
    target_audience: Optional[str] = None
    budget_range: Optional[str] = None
    additional_context: Optional[str] = None


Phase = Literal["gathering", "composing", "reviewing", "searching", "complete"]


class AgentState(TypedDict):
    """Full state for the pitch refinement agent graph."""

    messages: Annotated[list, add_messages]
    pitch_info: dict  # Serialised PitchInfo fields
    composed_pitch: str
    phase: Phase
    search_results: list  # Grant results from the search


class AgentRequest(BaseModel):
    """Incoming API request to the agent."""

    messages: list[dict]  # [{"role": "user", "content": "..."}]
    thread_id: str


class AgentResponse(BaseModel):
    """Outgoing API response from the agent."""

    messages: list[dict]
    thread_id: str
    phase: Phase
    composed_pitch: Optional[str] = None
    search_results: Optional[list] = None
