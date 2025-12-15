import json
import logging
import os
import functions_framework
import pandas as pd
from dotenv import load_dotenv
from google.cloud import storage
from src.process import process_grant
from src.chunk import chunk_grant
from src.embed import embed_chunks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

EMBEDDED_CHUNKS_SUFFIX = "_embedded_grant_chunks.parquet"
RAW_GRANTS_SUFFIX = "_raw_grants.json"
INCOMING_PREFIX = "incoming/"
PROCESSED_PREFIX = "processed/"
OUTPUT_BUCKET_NAME = os.getenv("GCS_OUTPUT_BUCKET_NAME")

storage_client = storage.Client()


def _load_data(bucket, blob_name):
    """Downloads and parses a JSON blob from GCS."""
    blob = bucket.blob(blob_name)
    content = blob.download_as_text()
    return json.loads(content)


def _store_embedded_chunks(source_object_name, embedded_chunks):
    """Derives output path and uploads embedded chunks to GCS as parquet."""
    output_blob_name = source_object_name.replace(RAW_GRANTS_SUFFIX, EMBEDDED_CHUNKS_SUFFIX)
    logger.info(f"Uploading {len(embedded_chunks)} embedded chunks to gs://{OUTPUT_BUCKET_NAME}/{output_blob_name}")
    
    records = [chunk.model_dump() for chunk in embedded_chunks]
    df = pd.DataFrame(records)
    parquet_bytes = df.to_parquet(index=False)
    
    bucket = storage_client.bucket(OUTPUT_BUCKET_NAME)
    blob = bucket.blob(output_blob_name)
    blob.upload_from_string(parquet_bytes, content_type="application/octet-stream")


def _mark_as_processed(bucket, object_name):
    """Moves the original raw grants blob to the processed folder."""
    destination_blob_name = object_name.replace(INCOMING_PREFIX, PROCESSED_PREFIX)
    source_blob = bucket.blob(object_name)
    bucket.copy_blob(source_blob, bucket, destination_blob_name)
    bucket.delete_blob(object_name)
    logger.info(f"Moved {object_name} to {destination_blob_name}")


@functions_framework.cloud_event
def process_raw_grants(cloud_event):
    """
    Cloud Function triggered by a Cloud Storage event.
    Processes a raw grants JSON file, chunks and embeds the data,
    stores the result vs parquet, and moves the original file to processed/.
    """
    data = cloud_event.data
    bucket_name = data["bucket"]
    object_name = data["name"]

    logger.info(f"Processing gs://{bucket_name}/{object_name}")

    if not object_name.startswith(INCOMING_PREFIX):
        logger.info(f"Ignoring file {object_name} which is not in {INCOMING_PREFIX}")
        return

    if not OUTPUT_BUCKET_NAME:
        raise ValueError("GCS_OUTPUT_BUCKET_NAME environment variable is not set.")

    try:
        source_bucket = storage_client.bucket(bucket_name)

        raw_grants_data = _load_data(source_bucket, object_name)
        logger.info(f"Loaded {len(raw_grants_data)} raw grants.")

        processed_grants = [process_grant(raw_grant) for raw_grant in raw_grants_data]
        chunks = [chunk for grant in processed_grants for chunk in chunk_grant(grant)]
        
        embedded_chunks = embed_chunks(chunks)
        logger.info(f"Embedded {len(embedded_chunks)} chunks.")

        _store_embedded_chunks(object_name, embedded_chunks)
        _mark_as_processed(source_bucket, object_name)
        logger.info(f"Successfully processed {object_name}")

    except Exception as e:
        logger.error(f"Error processing {object_name}: {e}")
        raise
