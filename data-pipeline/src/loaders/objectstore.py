import json
import logging
from datetime import datetime, timezone
from google.cloud import storage
from src.models import Grant


INCOMING_PREFIX = "incoming/"
PROCESSED_PREFIX = "processed/"

RAW_EU_GRANTS_BUCKET_NAME = "raw-grants"
RAW_GRANTS_KEY_SUFFIX = "_raw_grants.json"

EMBEDDED_EU_GRANT_CHUNKS_BUCKET_NAME = "embedded-grant-chunks"
EMBEDDED_GRANT_CHUNKS_KEY_SUFFIX = "_embedded_grant_chunks.parquet"


logger = logging.getLogger(__name__)
client = storage.Client()


def _get_bucket(bucket_name: str) -> storage.Bucket:
    return client.bucket(bucket_name)


def _store_to_gcs(bucket_name: str, blob_name: str, data: list):
    """Uploads the data to Google Cloud Storage."""
    try:
        bucket = _get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        # (LS): Serialize the list of data to a JSON string
        json_data = json.dumps(data)
        blob.upload_from_string(json_data, content_type="application/json")
        
        logger.info(f"Uploaded {len(data)} items to gs://{bucket_name}/{blob_name}")
    except Exception as e:
        logger.error(f"Failed to upload to GCS: {e}")
        raise


def _get_raw_grants_object_key() -> str:
    """Generate object key for raw grants based on current date."""
    return (
        INCOMING_PREFIX
        + datetime.now(timezone.utc).strftime("%Y%m%d")
        + RAW_GRANTS_KEY_SUFFIX
    )


# TODO(LS): Update with batches?
def store_raw_grants(grants: list[Grant]) -> None:
    bucket_name = RAW_EU_GRANTS_BUCKET_NAME
    object_key = _get_raw_grants_object_key()
    _store_to_gcs(bucket_name, object_key, grants)
