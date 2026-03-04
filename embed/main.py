import logging

from firebase_functions import https_fn
from firebase_functions.params import SecretParam
from src.openai_embeddings import OpenAIEmbeddings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Secrets (managed via firebase functions:secrets:set)
OPENAI_API_KEY = SecretParam("OPENAI_API_KEY")


@https_fn.on_request(
    region="europe-west4",
    secrets=[OPENAI_API_KEY],
)
def embed(request: https_fn.Request) -> https_fn.Response:
    request_json = request.get_json(silent=True)

    if not request_json or "texts" not in request_json:
        return {"error": "Missing 'texts' field in request"}, 400

    texts = request_json.get("texts")
    model = request_json.get("model")

    if not texts or not isinstance(texts, list):
        return {"error": "'texts' field must be non-empty list"}, 400

    try:
        embeddings_client = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY.value)

        # Call OpenAI embeddings API
        result = embeddings_client.client.embeddings.create(model=model, input=texts)

        # Extract embeddings from response
        embeddings = [item.embedding for item in result.data]

        return {"embeddings": embeddings}, 200
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        return {"error": str(e)}, 500
