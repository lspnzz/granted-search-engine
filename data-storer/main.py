import logging
import io
import os
import functions_framework
import pandas as pd
from google.cloud import storage
from src.models import GrantChunk
from src.vectorstore import upsert_chunks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INCOMING_PREFIX = "incoming/"
PROCESSED_PREFIX = "processed/"
EMBEDDED_CHUNKS_SUFFIX = "_embedded_grant_chunks.parquet"

storage_client = storage.Client()


def _load_embedded_chunks(bucket, blob_name):
    """Downloads parquet file from GCS and returns a list of GrantChunk objects."""
    blob = bucket.blob(blob_name)
    content = blob.download_as_bytes()
    df = pd.read_parquet(io.BytesIO(content))
    
    chunks = []
    for _, row in df.iterrows():
        try:
            chunks.append(GrantChunk(**row.to_dict()))
        except Exception as e:
            logger.error(f"Failed to parse row into GrantChunk: {e}")
            raise
            
    return chunks


def _mark_as_processed(bucket, object_name):
    """Moves the original blob to the processed folder."""
    destination_blob_name = object_name.replace(INCOMING_PREFIX, PROCESSED_PREFIX)
    source_blob = bucket.blob(object_name)
    bucket.copy_blob(source_blob, bucket, destination_blob_name)
    bucket.delete_blob(object_name)
    logger.info(f"Moved {object_name} to {destination_blob_name}")


@functions_framework.cloud_event
def store_embedded_chunks(cloud_event):
    """
    Cloud Function triggered by a Cloud Storage event.
    Processes an embedded grants parquet file, upserts vectors to Pinecone,
    and moves the file to processed/.
    """
    data = cloud_event.data
    bucket_name = data["bucket"]
    object_name = data["name"]

    logger.info(f"Processing gs://{bucket_name}/{object_name}")

    if not object_name.startswith(INCOMING_PREFIX):
        logger.info(f"Ignoring file {object_name} which is not in {INCOMING_PREFIX}")
        return

    try:
        bucket = storage_client.bucket(bucket_name)

        chunks = _load_embedded_chunks(bucket, object_name)
        logger.info(f"Loaded {len(chunks)} chunks from parquet.")

        upsert_chunks(chunks)
        logger.info(f"Upserted {len(chunks)} chunks to Pinecone.")

        _mark_as_processed(bucket, object_name)
        logger.info(f"Successfully processed {object_name}")

    except Exception as e:
        logger.error(f"Error processing {object_name}: {e}")
        # Re-raising the exception causes the Cloud Function to retry (if configured)
        raise
