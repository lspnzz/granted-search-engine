import functions_framework
from src.openai_embeddings import OpenAIEmbeddings

embeddings_client = OpenAIEmbeddings()


@functions_framework.http
def embed(request):
    request_json = request.get_json(silent=True)
    
    if not request_json or "texts" not in request_json:
        return {"error": "Missing 'texts' field in request"}, 400
    
    texts = request_json.get("texts")
    model = request_json.get("model")
    
    if not texts or not isinstance(texts, list):
        return {"error": "'texts' field must be non-empty list"}, 400
    
    try:
        # Call OpenAI embeddings API
        result = embeddings_client.client.embeddings.create(
            model=model,
            input=texts
        )
        
        # Extract embeddings from response
        embeddings = [item.embedding for item in result.data]
        
        return {"embeddings": embeddings}, 200
    except Exception as e:
        return {"error": str(e)}, 500