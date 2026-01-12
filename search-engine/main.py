import functions_framework
import logging
from pydantic import ValidationError
from src.models import SearchRequest
from src.embed import embed_pitch
from src.vectorstore import query_grants

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@functions_framework.http
def search_grants(request):
    request_json = request.get_json(silent=True)
    if not request_json:
        return (
            {"error": "Invalid JSON or empty body provided"},
            400,
        )  # (LS): Bad Request

    try:
        search_req = SearchRequest(**request_json)  # (LS): Validate with Pydantic
        pitch = search_req.pitch
        top_k = search_req.top_k
        model_name = search_req.model_name
        dimensions = search_req.dimensions
        index_name = search_req.pinecone_index_name
        namespace = search_req.pinecone_namespace

        embedded_pitch = embed_pitch(pitch, model=model_name, dimensions=dimensions)
        grants = query_grants(
            embedded_pitch,
            top_k=top_k,
            index_name=index_name,
            namespace=namespace,
        )

        response_data = {
            "pitch": pitch,
            "grants": [g.model_dump() for g in grants],
        }

        return response_data

    except ValidationError as e:
        logger.error(f"Validation Error: {e}")
        return ({"error": "Validation Error", "details": e.errors()}, 400)

    except Exception as e:
        logger.error(f"Error executing search: {e}")
        return ({"error": "Internal Server Error"}, 500)
