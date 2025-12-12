import functions_framework
import logging
from src.models import SearchRequest
from src.search import search
from src.utils import configure_logging

logger = configure_logging(log_level=logging.INFO)


@functions_framework.http
def search_grants(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
    Returns:
        dict: The response data.
    """

    request_json = request.get_json(silent=True)    
    if not request_json:
        return ({"error": "Invalid JSON or empty body provided"}, 400)  # (LS): Bad Request

    try:
        search_req = SearchRequest(**request_json)  # (LS): Validate with Pydantic
        grants = search(search_req.pitch)

        response_data = {
            "pitch": search_req.pitch,
            "grants": [g.model_dump() for g in grants]
        }

        return response_data

    except ValidationError as e:
        logger.error(f"Validation Error: {e}")
        return ({"error": "Validation Error", "details": e.errors()}, 400)
        
    except Exception as e:
        logger.error(f"Error executing search: {e}") 
        return ({"error": "Internal Server Error"}, 500)
