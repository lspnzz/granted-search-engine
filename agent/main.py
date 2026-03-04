import os
import logging
import functions_framework
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
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
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "3600",
        }
        return ("", 204, headers)

    cors_headers = {"Access-Control-Allow-Origin": "*"}

    request_json = request.get_json(silent=True)
    if not request_json:
        return (
            {"error": "Invalid JSON or empty body provided"},
            400,
            cors_headers,
        )

    try:
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
            {"messages": lc_messages},
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

        return (response, 200, cors_headers)

    except Exception as e:
        logger.error(f"Agent error: {e}", exc_info=True)
        return (
            {"error": f"Agent error: {str(e)}"},
            500,
            cors_headers,
        )
