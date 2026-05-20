import os
import logging
import json
import time
from uuid import uuid4
import functions_framework
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from pydantic import ValidationError
from src.graph import build_graph
from src.state import AgentRequest

load_dotenv()

# ---------------------------------------------------------------------------
# LangSmith Tracing Configuration
# ---------------------------------------------------------------------------
# These env vars enable automatic tracing — set in .env:
#   LANGCHAIN_TRACING_V2=true
#   LANGCHAIN_API_KEY=<your key>
#   LANGCHAIN_PROJECT=granted-pitch-agent
# No code needed — langchain auto-detects them.

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Build the graph once at module level (reused across requests)
app = build_graph()


def _request_id(request) -> str:
    return request.headers.get("X-Request-ID") or str(uuid4())


def _log_event(event: str, **fields) -> None:
    logger.info(json.dumps({"service": "agent", "event": event, **fields}))


@functions_framework.http
def refine_pitch(request):
    """Cloud Function entry point for the pitch refinement agent.

    Accepts POST with JSON body:
    {
        "messages": [{"role": "user", "content": "..."}],
        "thread_id": "unique-conversation-id"
    }

    Returns JSON:
    {
        "messages": [{"role": "assistant", "content": "..."}],
        "thread_id": "...",
        "phase": "gathering|composing|reviewing|searching|complete",
        "composed_pitch": "..." (when available),
        "search_results": [...] (when search is complete)
    }
    """
    # Handle CORS preflight
    request_id = _request_id(request)
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Request-ID",
            "Access-Control-Expose-Headers": "X-Request-ID",
            "Access-Control-Max-Age": "3600",
            "X-Request-ID": request_id,
        }
        return ("", 204, headers)

    started = time.perf_counter()
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Expose-Headers": "X-Request-ID",
        "X-Request-ID": request_id,
    }

    request_json = request.get_json(silent=True)
    if not request_json:
        return (
            {"error": "Invalid JSON or empty body provided"},
            400,
            cors_headers,
        )

    try:
        _log_event("request.start", request_id=request_id, mode=os.getenv("GRANTED_HARNESS_MODE", "live"))
        agent_req = AgentRequest(**request_json)
        thread_id = agent_req.thread_id

        # Convert incoming messages to LangChain format
        lc_messages = []
        for msg in agent_req.messages:
            if msg.get("role") == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))

        # Invoke the graph with the thread config for checkpointing
        config = {"configurable": {"thread_id": thread_id}}
        result = app.invoke(
            {"messages": lc_messages, "request_id": request_id},
            config=config,
        )

        # Extract the response
        response_messages = []
        for msg in result.get("messages", []):
            role = "assistant" if not isinstance(msg, HumanMessage) else "user"
            response_messages.append(
                {
                    "role": role,
                    "content": msg.content,
                }
            )

        response = {
            "messages": response_messages,
            "thread_id": thread_id,
            "phase": result.get("phase", "gathering"),
            "composed_pitch": result.get("composed_pitch"),
            "search_results": result.get("search_results"),
        }

        _log_event(
            "request.complete",
            request_id=request_id,
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
            phase=response["phase"],
        )
        return (response, 200, cors_headers)

    except ValidationError as e:
        logger.error(f"Validation Error: {e}")
        return (
            {"error": "Validation Error", "details": e.errors(include_context=False)},
            400,
            cors_headers,
        )

    except Exception as e:
        logger.error(f"Agent error: {e}", exc_info=True)
        _log_event("request.error", request_id=request_id, error=type(e).__name__)
        return (
            {"error": f"Agent error: {str(e)}"},
            500,
            cors_headers,
        )
