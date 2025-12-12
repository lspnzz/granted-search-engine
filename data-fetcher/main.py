import json
import logging
import os
from datetime import datetime, timezone
import functions_framework
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from google.cloud import storage
from dotenv import load_dotenv

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# EU API constants
API_KEY = "SEDIA"
BASE_API_URL = "https://api.tech.ec.europa.eu/search-api/prod/rest/search"
PAGE_SIZE = 50

# GCS constants
RAW_EU_GRANTS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME") 
RAW_INCOMING_PREFIX = "incoming/"
RAW_EU_GRANTS_KEY_SUFFIX = "_raw_grants.json"


class GrantType:
    DIRECT_EU_GRANTS = "1"
    EXTERNAL_ACTIONS = "2"


class StatusCode:
    FORTHCOMING = "31094501"
    OPEN_FOR_SUBMISSION = "31094502"


class Languages:
    EN = "en"


def _iter_grant_pages():
    """Yield one page of grant results at a time."""
    session = requests.Session()
    page = 1

    logger.info("Starting grant fetch from EU API")

    while True:
        query = {
            "bool": {
                "must": [
                    {
                        "terms": {
                            "type": [
                                GrantType.DIRECT_EU_GRANTS,
                                GrantType.EXTERNAL_ACTIONS,
                            ]
                        }
                    },
                    {
                        "terms": {
                            "status": [
                                StatusCode.FORTHCOMING,
                                StatusCode.OPEN_FOR_SUBMISSION,
                            ]
                        }
                    },
                ]
            }
        }

        languages = [Languages.EN]

        form_data = MultipartEncoder(
            fields={
                "query": ("query", json.dumps(query), "application/json"),
                "languages": ("languages", json.dumps(languages), "application/json"),
            }
        )

        headers = {
            "Accept": "application/json",
            "Content-Type": form_data.content_type,
        }

        params = {
            "apiKey": API_KEY,
            "text": "*",
            "pageNumber": page,
            "pageSize": PAGE_SIZE,
        }

        try:
            response = session.post(
                BASE_API_URL,
                params=params,
                headers=headers,
                data=form_data,
                timeout=30,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error("Request failed on page %d: %s", page, e)
            break

        data = response.json()
        results = data.get("results", [])

        if not results:
            logger.info("No results returned on page %d. Stopping.", page)
            break

        logger.info("Fetched %d results from page %d", len(results), page)

        yield results

        if len(results) < PAGE_SIZE:
            logger.info("Reached last page (%d).", page)
            break

        page += 1

    logger.info("Finished fetching grants.")


def generate_raw_grants_object_key() -> str:
    """Generate object key for raw grants based on current date."""
    return (
        RAW_INCOMING_PREFIX
        + datetime.now(timezone.utc).strftime("%Y%m%d")
        + RAW_EU_GRANTS_KEY_SUFFIX
    )


def upload_to_gcs(bucket_name: str, blob_name: str, data: list):
    """Uploads the data to Google Cloud Storage."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        # Determine if data should be bytes or string
        json_data = json.dumps(data)
        blob.upload_from_string(json_data, content_type="application/json")
        
        logger.info(f"Uploaded {len(data)} items to gs://{bucket_name}/{blob_name}")
    except Exception as e:
        logger.error(f"Failed to upload to GCS: {e}")
        raise


@functions_framework.http
def fetch_eu_grants(request):
    """HTTP Cloud Function to fetch grants and store them in GCS."""
    try:
        # TODO(LS): Optimise with proper batching
        raw_grants = []  # (LS): Using a flat list to collect all grants
        for grant_batch in _iter_grant_pages():
            raw_grants.extend(grant_batch)
        
        if not raw_grants:
             return "No grants fetched.", 200

        object_key = generate_raw_grants_object_key()
        upload_to_gcs(RAW_EU_GRANTS_BUCKET_NAME, object_key, raw_grants)

        return f"Successfully fetched and stored {len(raw_grants)} grants to {object_key}", 200

    except Exception as e:
        logger.exception("Error in fetch_grants_function")
        return f"Internal Server Error: {e}", 500