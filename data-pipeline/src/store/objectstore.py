import os
import json
import logging
import dotenv
import io
from datetime import datetime, timezone
from typing import Any
from botocore.config import Config
import boto3
import pandas as pd


dotenv.load_dotenv()
TIGRIS_ACCESS_KEY_ID = os.getenv("TIGRIS_ACCESS_KEY_ID")
TIGRIS_ACCESS_KEY_SECRET = os.getenv("TIGRIS_ACCESS_KEY_SECRET")

RAW_EU_GRANTS_BUCKET_NAME = os.getenv("TIGRIS_RAW_EU_GRANTS_BUCKET_NAME")
EMBEDDED_EU_GRANT_CHUNKS_BUCKET_NAME = os.getenv(
    "TIGRIS_EMBEDDED_EU_GRANT_CHUNKS_BUCKET_NAME"
)

RAW_EU_GRANTS_KEY_SUFFIX = "_raw_grants.json"
EMBEDDED_EU_GRANT_CHUNKS_KEY_SUFFIX = "_embedded_grant_chunks.parquet"

RAW_INCOMING_PREFIX = "incoming/"
RAW_PROCESSED_PREFIX = "processed/"
EMBEDDED_INCOMING_PREFIX = "incoming/"
EMBEDDED_STORED_PREFIX = "stored/"

logger = logging.getLogger(__name__)

svc = boto3.client(
    "s3",
    aws_access_key_id=TIGRIS_ACCESS_KEY_ID,
    aws_secret_access_key=TIGRIS_ACCESS_KEY_SECRET,
    endpoint_url="https://t3.storage.dev",
    config=Config(s3={"addressing_style": "virtual"}),
)


def _store_data(bucket_name: str, object_key: str, data: bytes):
    svc.put_object(Bucket=bucket_name, Key=object_key, Body=data)


def _load_data(bucket_name: str, object_key: str) -> bytes:
    response = svc.get_object(Bucket=bucket_name, Key=object_key)
    return response["Body"].read()


def store_json(bucket_name: str, object_key: str, obj: Any) -> None:
    data = json.dumps(obj).encode("utf-8")
    _store_data(bucket_name, object_key, data)


def load_json(bucket_name: str, object_key: str) -> Any:
    data = _load_data(bucket_name, object_key)
    return json.loads(data.decode("utf-8"))


def _get_latest_dated_key(bucket_name: str, suffix: str, prefix: str = ""):
    paginator = svc.get_paginator("list_objects_v2")
    latest_key = None

    paginate_kwargs = {"Bucket": bucket_name}
    if prefix:
        paginate_kwargs["Prefix"] = prefix

    for page in paginator.paginate(**paginate_kwargs):
        for item in page.get("Contents", []):
            key = item["Key"]
            if key.endswith(suffix) and (latest_key is None or key > latest_key):
                latest_key = key
    return latest_key


def generate_raw_grants_object_key() -> str:
    """Generate object key for raw grants based on current date."""
    return (
        RAW_INCOMING_PREFIX
        + datetime.now(timezone.utc).strftime("%Y%m%d")
        + RAW_EU_GRANTS_KEY_SUFFIX
    )


def generate_embedded_chunks_object_key(raw_grants_object_key: str) -> str:
    """Generate object key for embedded chunks based on chunks object key."""
    return raw_grants_object_key.replace(
        RAW_EU_GRANTS_KEY_SUFFIX, EMBEDDED_EU_GRANT_CHUNKS_KEY_SUFFIX
    )


# TODO(LS): Update with batches?
# TODO(LS): Save to new/ folder.
def store_raw_grants(object_key: str, grant_batch: Any) -> None:
    bucket_name = RAW_EU_GRANTS_BUCKET_NAME
    logger.info(
        "Storing raw grants with %d grants to %s/%s",
        len(grant_batch),
        bucket_name,
        object_key,
    )
    store_json(bucket_name, object_key, grant_batch)


def store_embedded_chunks(object_key: str, embedded_chunks_batch: Any) -> None:
    bucket_name = EMBEDDED_EU_GRANT_CHUNKS_BUCKET_NAME
    logger.info(
        "Storing embedded grant chunks with %d chunks to %s/%s",
        len(embedded_chunks_batch),
        bucket_name,
        object_key,
    )
    records = [c.model_dump() for c in embedded_chunks_batch]
    df = pd.DataFrame(records)
    parquet_bytes = df.to_parquet(index=False)

    _store_data(bucket_name, object_key, parquet_bytes)


def load_raw_grants(object_key: str = "") -> tuple[Any, str]:
    """Load latest grant data if object_key not specified."""
    bucket_name = RAW_EU_GRANTS_BUCKET_NAME

    if object_key:
        return load_json(bucket_name, object_key)

    latest_grants_object_key = _get_latest_dated_key(
        bucket_name,
        RAW_EU_GRANTS_KEY_SUFFIX,
        prefix=RAW_INCOMING_PREFIX,
    )
    return (load_json(bucket_name, latest_grants_object_key), latest_grants_object_key)


def _load_parquet(bucket_name: str, object_key: str) -> Any:
    data = _load_data(bucket_name, object_key)
    return pd.read_parquet(io.BytesIO(data))


def load_embedded_chunks(object_key: str = "") -> tuple[Any, str]:
    """Load latest embedded chunked grant data if object_key not specified."""
    bucket_name = EMBEDDED_EU_GRANT_CHUNKS_BUCKET_NAME

    if object_key:
        return _load_parquet(bucket_name, object_key)

    latest_embedded_chunks_object_key = _get_latest_dated_key(
        bucket_name,
        EMBEDDED_EU_GRANT_CHUNKS_KEY_SUFFIX,
        prefix=EMBEDDED_INCOMING_PREFIX,
    )
    return (
        _load_parquet(bucket_name, latest_embedded_chunks_object_key),
        latest_embedded_chunks_object_key,
    )


def mark_raw_grants_as_processed(object_key: str) -> None:
    """Mark raw grants as processed by moving to the processed folder within the bucket."""
    bucket_name = RAW_EU_GRANTS_BUCKET_NAME
    base_key = object_key.removeprefix(RAW_INCOMING_PREFIX)
    processed_key = RAW_PROCESSED_PREFIX + base_key

    logger.info(
        "Marking raw grants as processed: moving %s/%s to %s/%s",
        bucket_name,
        object_key,
        bucket_name,
        processed_key,
    )

    svc.copy_object(
        Bucket=bucket_name,
        CopySource={"Bucket": bucket_name, "Key": object_key},
        Key=processed_key,
    )
    svc.delete_object(Bucket=bucket_name, Key=object_key)


def mark_embedded_chunks_as_stored(object_key: str) -> None:
    """Mark embedded chunks as stored to the vector db by moving to the stored folder within the bucket."""
    bucket_name = EMBEDDED_EU_GRANT_CHUNKS_BUCKET_NAME
    base_key = object_key.removeprefix(EMBEDDED_INCOMING_PREFIX)
    processed_key = EMBEDDED_STORED_PREFIX + base_key

    logger.info(
        "Marking embedded chunks as stored: moving %s/%s to %s/%s",
        bucket_name,
        object_key,
        bucket_name,
        processed_key,
    )

    svc.copy_object(
        Bucket=bucket_name,
        CopySource={"Bucket": bucket_name, "Key": object_key},
        Key=processed_key,
    )
    svc.delete_object(Bucket=bucket_name, Key=object_key)
