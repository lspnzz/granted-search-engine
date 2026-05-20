import json
import logging
import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.state import AgentState, PitchInfo
from src.prompts import (
    SYSTEM_PROMPT,
    COMPOSE_PITCH_PROMPT,
    REVIEW_PROMPT,
)
from src.tools import search_grants

logger = logging.getLogger(__name__)


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("AGENT_MODEL", "gpt-4o-mini"),
        temperature=float(os.getenv("AGENT_TEMPERATURE", "0.7")),
    )


# ---------------------------------------------------------------------------
# Node: gather_info
# ---------------------------------------------------------------------------
def gather_info(state: AgentState) -> dict:
    """Single-turn node: respond to the user and ask the next question.

    Uses a single LLM call with a detailed system prompt that handles
    extraction, sufficiency checking, and question-asking all at once.
    """
    llm = _get_llm()
    messages = state["messages"]
    pitch_info = state.get("pitch_info", {})

    system = (
        SYSTEM_PROMPT
        + f"""

Current extracted info: {json.dumps(pitch_info) if pitch_info else "Nothing yet."}

IMPORTANT RULES FOR THIS RESPONSE:
- If you have enough info (at minimum: domain, problem, and innovation are all
  clearly defined), respond with EXACTLY the marker [READY_TO_COMPOSE] at the
  very end of your message, after telling the user you'll compose their pitch.
- If you still need more info, ask ONE follow-up question. Do NOT include
  [READY_TO_COMPOSE].
- As you learn things from the user, include a JSON block at the very end of
  your message wrapped in <pitch_info>...</pitch_info> tags with the updated
  fields. Only include fields you've learned. Example:
  <pitch_info>{{"domain": "agriculture", "problem": "crop disease detection"}}</pitch_info>
"""
    )

    response = llm.invoke([SystemMessage(content=system)] + list(messages))

    content = response.content

    # Extract pitch_info if present
    if "<pitch_info>" in content and "</pitch_info>" in content:
        try:
            json_str = (
                content.split("<pitch_info>")[1].split("</pitch_info>")[0].strip()
            )
            extracted = json.loads(json_str)
            for key, value in extracted.items():
                if value is not None:
                    pitch_info[key] = value
            # Remove the tags from the visible message
            content = content.split("<pitch_info>")[0].strip()
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to parse pitch_info: {e}")

    # Check for readiness marker
    next_phase = "gathering"
    if "[READY_TO_COMPOSE]" in content:
        content = content.replace("[READY_TO_COMPOSE]", "").strip()
        next_phase = "composing"

    return {
        "messages": [AIMessage(content=content)],
        "pitch_info": pitch_info,
        "phase": next_phase,
    }


# ---------------------------------------------------------------------------
# Node: compose_pitch
# ---------------------------------------------------------------------------
def compose_pitch(state: AgentState) -> dict:
    """Compose an optimised pitch from the gathered information."""
    llm = _get_llm()
    pitch_info = state.get("pitch_info", {})

    info = PitchInfo(**pitch_info)

    composed = llm.invoke(
        [
            SystemMessage(
                content="You are an expert at writing EU grant search pitches."
            ),
            HumanMessage(
                content=COMPOSE_PITCH_PROMPT.format(
                    domain=info.domain or "Not specified",
                    problem=info.problem or "Not specified",
                    innovation=info.innovation or "Not specified",
                    target_audience=info.target_audience or "Not specified",
                    budget_range=info.budget_range or "Not specified",
                    additional_context=info.additional_context or "Not specified",
                )
            ),
        ]
    )

    composed_pitch = composed.content.strip()
    review_msg = REVIEW_PROMPT.format(pitch=composed_pitch)

    return {
        "messages": [AIMessage(content=review_msg)],
        "composed_pitch": composed_pitch,
        "phase": "reviewing",
    }


# ---------------------------------------------------------------------------
# Node: review_pitch
# ---------------------------------------------------------------------------
def review_pitch(state: AgentState) -> dict:
    """Handle the user's response to the composed pitch."""
    messages = state["messages"]

    last_user_msg = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_msg = msg.content.strip().lower()
            break

    if not last_user_msg:
        return {"phase": "reviewing"}

    approval_keywords = [
        "yes",
        "search",
        "go",
        "looks good",
        "perfect",
        "approve",
        "ok",
        "okay",
        "sure",
        "let's go",
        "do it",
        "great",
    ]

    if any(keyword in last_user_msg for keyword in approval_keywords):
        return {
            "messages": [
                AIMessage(
                    content="Excellent! Searching for matching EU grants now... 🔍"
                )
            ],
            "phase": "searching",
        }

    # User wants changes
    llm = _get_llm()
    change_response = llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            *messages,
            HumanMessage(
                content=(
                    "The user wants to change the pitch. Acknowledge their feedback "
                    "and ask clarifying questions if needed. Be helpful and concise."
                )
            ),
        ]
    )

    return {
        "messages": [change_response],
        "phase": "gathering",
    }


# ---------------------------------------------------------------------------
# Node: execute_search
# ---------------------------------------------------------------------------
def execute_search(state: AgentState) -> dict:
    """Execute the grant search with the composed pitch."""
    composed_pitch = state.get("composed_pitch", "")

    if not composed_pitch:
        return {
            "messages": [
                AIMessage(
                    content="Something went wrong — no pitch was composed. Let's start over."
                )
            ],
            "phase": "gathering",
            "search_results": [],
        }

    try:
        grants = search_grants(composed_pitch, request_id=state.get("request_id"))

        if grants:
            result_summary = f"Found **{len(grants)} matching EU grants**! Here are the top results:\n\n"
            for i, grant in enumerate(grants[:5], 1):
                score_pct = (
                    f"{grant['match_score'] * 100:.0f}%"
                    if grant.get("match_score")
                    else "N/A"
                )
                result_summary += f"**{i}. {grant.get('title', 'Untitled')}**\n"
                result_summary += f"   Match: {score_pct}"
                if grant.get("deadline"):
                    result_summary += f" · Deadline: {grant['deadline']}"
                if grant.get("amount"):
                    result_summary += f" · Funding: €{grant['amount']}"
                result_summary += "\n\n"
            if len(grants) > 5:
                result_summary += f"_...and {len(grants) - 5} more results._\n"
        else:
            result_summary = "No matching grants were found. You might want to try broadening your pitch."

        return {
            "messages": [AIMessage(content=result_summary)],
            "search_results": grants,
            "phase": "complete",
        }

    except Exception as e:
        logger.error(f"Search execution failed: {e}")
        return {
            "messages": [
                AIMessage(
                    content=f"Sorry, the search encountered an error: {str(e)}. Please try again."
                )
            ],
            "search_results": [],
            "phase": "complete",
        }


# ---------------------------------------------------------------------------
# Routing logic
# ---------------------------------------------------------------------------
def route_by_phase(state: AgentState) -> str:
    """Route to the correct node based on current phase."""
    phase = state.get("phase", "gathering")
    if phase == "gathering":
        return "gather_info"
    elif phase == "composing":
        return "compose_pitch"
    elif phase == "reviewing":
        return "review_pitch"
    elif phase == "searching":
        return "execute_search"
    return END


# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------
def build_graph():
    """Build and compile the LangGraph agent.

    Key design: each node routes to END after executing, so the graph
    returns after every turn. The phase stored in state determines which
    node runs on the next invocation. Only compose_pitch and execute_search
    chain to a follow-up node in the same invocation.
    """
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("gather_info", gather_info)
    graph.add_node("compose_pitch", compose_pitch)
    graph.add_node("review_pitch", review_pitch)
    graph.add_node("execute_search", execute_search)

    # Entry: route to the right node based on phase
    graph.add_conditional_edges(START, route_by_phase)

    # After gather_info: if phase became "composing", chain to compose_pitch,
    # otherwise END (wait for next user message)
    graph.add_conditional_edges(
        "gather_info",
        lambda s: "compose_pitch" if s.get("phase") == "composing" else END,
    )

    # After compose_pitch: always END (show pitch to user for review)
    graph.add_edge("compose_pitch", END)

    # After review_pitch: if user approved, chain to search; otherwise END
    graph.add_conditional_edges(
        "review_pitch",
        lambda s: "execute_search" if s.get("phase") == "searching" else END,
    )

    # After search: always END
    graph.add_edge("execute_search", END)

    # Compile with checkpointer for multi-turn state
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)
