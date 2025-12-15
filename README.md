# Granted: Search Engine

A serverless application that helps users find relevant EU grants based on their project pitches.

## How it works

The application exposes an HTTP endpoint via Google Cloud Run Functions. It takes a project pitch as input, generates vector embeddings using OpenAI, and performs a semantic search against a Pinecone vector database to return the most relevant grants.


## Environment setup (it's a shared environment for all services)

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r ./data-pipeline/requirements.txt
pip install -r ./search-engine/requirements.txt
```


## Deploy to Google Cloud Run Functions (from the root directory)

```bash
gcloud run deploy granted-search-engine \
    --source=./search-engine \
    --function=search_grants \
    --region=REGION \
    --base-image=python313 \
    --allow-unauthenticated \
    --set-env-vars="EU_GRANT_CHUNKS_INDEX_HOST=your_eu_grants_index_host_here,EU_GRANT_CHUNKS_NAMESPACE=your_eu_grants_namespace_here," \
    --set-secrets="PINECONE_API_KEY=projects/PROJECT_ID/secrets/PINECONE_API_KEY/versions/latest,OPENAI_API_KEY=projects/PROJECT_ID/secrets/OPENAI_API_KEY/versions/latest"

```

```bash
gcloud run deploy data-pipeline \
    --source=./data-pipeline \
    --function=run_pipeline \
    --region=REGION \
    --base-image=python313 \
    --allow-unauthenticated \
    --set-secrets="PINECONE_API_KEY=projects/PROJECT_ID/secrets/PINECONE_API_KEY/versions/latest,OPENAI_API_KEY=projects/PROJECT_ID/secrets/OPENAI_API_KEY/versions/latest"
```


```bash
gcloud run deploy granted-fetch-eu-grants \
    --source=./data-fetcher \
    --function=fetch_eu_grants \
    --region=europe-west1 \
    --base-image=python313 \
    --allow-unauthenticated \
    --set-env-vars="GCS_BUCKET_NAME=bucket-name"
```


```bash
gcloud run deploy granted-process-grants \
    --source=./data-processor \
    --function=process_raw_grants \
    --region=europe-west1 \
    --base-image=python313 \
    --allow-unauthenticated \
    --set-env-vars="GCS_OUTPUT_BUCKET_NAME=bucket-name" \
    --set-secrets="OPENAI_API_KEY=projects/PROJECT_ID/secrets/OPENAI_API_KEY/versions/latest"
```
