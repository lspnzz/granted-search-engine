import json
import requests
import logging
from enum import StrEnum
from requests_toolbelt.multipart.encoder import MultipartEncoder


class GrantType(StrEnum):
    DIRECT_EU_GRANTS = "1"
    EXTERNAL_ACTIONS = "2"


class StatusCode(StrEnum):
    FORTHCOMING = "31094501"
    OPEN_FOR_SUBMISSION = "31094502"


class Languages(StrEnum):
    EN = "en"


API_KEY = "SEDIA"
BASE_API_URL = "https://api.tech.ec.europa.eu/search-api/prod/rest/search"
PAGE_SIZE = 50  # (LS): EU Portal default page size


logger = logging.getLogger(__name__)


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
                                GrantType.DIRECT_EU_GRANTS.value,
                                GrantType.EXTERNAL_ACTIONS.value,
                            ]
                        }
                    },
                    {
                        "terms": {
                            "status": [
                                StatusCode.FORTHCOMING.value,
                                StatusCode.OPEN_FOR_SUBMISSION.value,
                            ]
                        }
                    },
                ]
            }
        }

        languages = [Languages.EN.value]  # (LS): Only fetching EN grants for now

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
                timeout=15,
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


def _iter_grants():
    """Yield lists of grants, one batch per API page."""
    for page in _iter_grant_pages():
        yield [raw_grant for raw_grant in page]


def fetch_grants() -> list[dict]:
    """Fetch grants from the EU API."""
    # TODO(LS): Optimise with proper batching
    raw_grants = []  # (LS): Using a flat list to collect all grants

    for grant_batch in _iter_grants():
        raw_grants.extend(grant_batch)
        logger.info("Fetched %d grants for current batch", len(grant_batch))

    return raw_grants
