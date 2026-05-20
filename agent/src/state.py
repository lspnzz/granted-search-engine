from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
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
    request_id: str


class AgentRequest(BaseModel):
    """Incoming API request to the agent."""

    messages: list[dict] = Field(min_length=1, max_length=40)
    thread_id: str = Field(min_length=1, max_length=120)

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, value: list[dict]) -> list[dict]:
        for message in value:
            if message.get("role") != "user":
                raise ValueError("messages may only contain user messages")
            content = message.get("content")
            if not isinstance(content, str) or not content.strip():
                raise ValueError("message content must be a non-empty string")
            if len(content) > 8000:
                raise ValueError("message content must be at most 8000 characters")
        return value


class AgentResponse(BaseModel):
    """Outgoing API response from the agent."""

    messages: list[dict]
    thread_id: str
    phase: Phase
    composed_pitch: Optional[str] = None
    search_results: Optional[list] = None
