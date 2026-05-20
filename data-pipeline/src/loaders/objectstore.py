import json
import logging
import os
from pathlib import Path
from datetime import datetime, timezone
from google.cloud import storage
from src.models import Grant


INCOMING_PREFIX = "incoming/"
PROCESSED_PREFIX = "processed/"

RAW_EU_GRANTS_BUCKET_NAME = "raw-grants"
RAW_GRANTS_KEY_SUFFIX = "_raw_grants.json"

CLEAN_EU_GRANTS_BUCKET_NAME = "clean-grants"
CLEAN_GRANTS_KEY_SUFFIX = "_clean_grants.json"

EMBEDDED_EU_GRANT_CHUNKS_BUCKET_NAME = "embedded-grant-chunks"
EMBEDDED_GRANT_CHUNKS_KEY_SUFFIX = "_embedded_grant_chunks.parquet"


logger = logging.getLogger(__name__)


def _is_mock_mode() -> bool:
    return os.getenv("GRANTED_HARNESS_MODE") == "mock"


def _raw_fixture_path() -> Path:
    return Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "raw_grants.json"


def _get_bucket(bucket_name: str) -> storage.Bucket:
    client = storage.Client()
    return client.bucket(bucket_name)


def _store_to_gcs(bucket_name: str, blob_name: str, data: list):
    """Uploads the data to Google Cloud Storage."""
    if _is_mock_mode():
        logger.info(
            "Mock GCS upload skipped for %d items to gs://%s/%s",
            len(data),
            bucket_name,
            blob_name,
        )
        return

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


def _get_clean_grants_object_key() -> str:
    """Generate object key for clean grants based on current date."""
    return (
        INCOMING_PREFIX
        + datetime.now(timezone.utc).strftime("%Y%m%d")
        + CLEAN_GRANTS_KEY_SUFFIX
    )


def store_clean_grants(grants: list[Grant]) -> None:
    bucket_name = CLEAN_EU_GRANTS_BUCKET_NAME
    object_key = _get_clean_grants_object_key()
    grants_data = [g.model_dump(mode="json") for g in grants]
    _store_to_gcs(bucket_name, object_key, grants_data)


def load_raw_grants(file_name: str) -> list[dict]:
    if _is_mock_mode():
        logger.info("Loading mock raw grants for %s", file_name)
        return json.loads(_raw_fixture_path().read_text(encoding="utf-8"))

    bucket_name = RAW_EU_GRANTS_BUCKET_NAME
    bucket = _get_bucket(bucket_name)
    object_key = INCOMING_PREFIX + file_name
    blob = bucket.blob(object_key)
    raw_grants = blob.download_as_text()
    return json.loads(raw_grants)
