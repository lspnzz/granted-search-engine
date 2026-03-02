import logging
import os

from firebase_functions import https_fn, options
from firebase_functions.params import SecretParam, StringParam, IntParam
from pydantic import ValidationError
from src.models import SearchRequest
from src.embed import embed_pitch
from src.vectorstore import query_grants

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Secrets (managed via firebase functions:secrets:set)
OPENAI_API_KEY = SecretParam("OPENAI_API_KEY")
PINECONE_API_KEY = SecretParam("PINECONE_API_KEY")

# Environment params (set via firebase functions:config or .env)
PINECONE_INDEX_NAME_PARAM = StringParam("PINECONE_INDEX_NAME")
PINECONE_NAMESPACE_PARAM = StringParam("PINECONE_NAMESPACE")
MODEL_NAME_PARAM = StringParam("MODEL_NAME")
DIMENSIONS_PARAM = IntParam("DIMENSIONS")
TOP_K_PARAM = IntParam("TOP_K", default=10)

cors_env = os.environ.get("CORS_ORIGINS")
CORS_ORIGINS = cors_env.split(",") if cors_env else []


@https_fn.on_request(
    region="europe-west4",
    secrets=[OPENAI_API_KEY, PINECONE_API_KEY],
    cors=options.CorsOptions(
        cors_origins=CORS_ORIGINS, cors_methods=["GET", "POST", "OPTIONS"]
    ),
)
def search_grants(request: https_fn.Request) -> https_fn.Response:
    request_json = request.get_json(silent=True)
    if not request_json:
        return (
            {"error": "Invalid JSON or empty body provided"},
            400,
        )  # (LS): Bad Request

    try:
        search_req = SearchRequest(**request_json)  # (LS): Validate with Pydantic

        # Configuration Resolution (Request > Env > Error)
        pitch = search_req.pitch

        _top_k = search_req.top_k or os.getenv("TOP_K")
        TOP_K = int(_top_k) if _top_k else None

        MODEL_NAME = search_req.model_name or os.getenv("MODEL_NAME")

        _dimensions = search_req.dimensions or os.getenv("DIMENSIONS")
        DIMENSIONS = int(_dimensions) if _dimensions else None

        PINECONE_INDEX_NAME = search_req.pinecone_index_name or os.getenv(
            "PINECONE_INDEX_NAME"
        )

        PINECONE_NAMESPACE = search_req.pinecone_namespace or os.getenv(
            "PINECONE_NAMESPACE"
        )

        if (
            not PINECONE_INDEX_NAME
            or not PINECONE_NAMESPACE
            or not MODEL_NAME
            or not DIMENSIONS
            or not TOP_K
        ):
            missing_params = [
                k
                for k, v in {
                    "INDEX_NAME": PINECONE_INDEX_NAME,
                    "NAMESPACE": PINECONE_NAMESPACE,
                    "MODEL_NAME": MODEL_NAME,
                    "DIMENSIONS": DIMENSIONS,
                    "TOP_K": TOP_K,
                }.items()
                if not v
            ]
            return (
                {"error": f"Missing required parameters: {', '.join(missing_params)}"},
                400,
            )

        embedded_pitch = embed_pitch(
            pitch, model=MODEL_NAME, dimensions=int(DIMENSIONS)
        )
        grants = query_grants(
            embedded_pitch,
            top_k=TOP_K,
            index_name=PINECONE_INDEX_NAME,
            namespace=PINECONE_NAMESPACE,
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
