from bs4 import BeautifulSoup
import html
import json
import logging

from src.models import Grant
from src.transformers.augment import extract_total_budget

logger = logging.getLogger(__name__)


# TODO(LS): Improve error handling and logging.
def _clean_description_byte(value) -> str:
    """Normalize and clean HTML from descriptionByte field."""
    if value is None:
        return ""
    try:
        if isinstance(value, (list, dict)):
            value = json.dumps(value, ensure_ascii=False)
        elif isinstance(value, bytes):
            value = value.decode("utf-8", errors="ignore")

        # Decode HTML entities
        value = html.unescape(str(value))

        # Remove HTML tags using BeautifulSoup
        soup = BeautifulSoup(value, "html.parser")
        text = soup.get_text(separator="\n", strip=True)

        # Normalize whitespace
        text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        return text
    except Exception as e:
        logger.error("Error cleaning descriptionByte: %s", e)
        return ""


def _get_meta(grant, key, default=None):
    meta = grant.get("metadata", {})
    values = meta.get(key)
    if isinstance(values, list) and values:
        return values[0]
    return default


def _clean_grant(raw_grant) -> Grant:
    """Clean and normalize a single raw grant into a Grant object."""
    return Grant(
        id=raw_grant.get("reference", ""),
        title=_get_meta(raw_grant, "title", "") or "",
        summary=raw_grant.get("summary", "") or "",
        description=_clean_description_byte(_get_meta(raw_grant, "descriptionByte")),
        url=raw_grant.get("url", ""),
        start_date=_get_meta(raw_grant, "startDate", ""),
        deadline_date=_get_meta(raw_grant, "deadlineDate", ""),
        status=_get_meta(raw_grant, "status", ""),
        total_funding_opportunity=extract_total_budget(
            _get_meta(raw_grant, "budgetOverview")
        ),
    )


def clean_grants(raw_grants: list[dict]) -> list[Grant]:
    """Clean a batch of raw grants and return their Grant models."""
    return [_clean_grant(grant) for grant in raw_grants]
