from bs4 import BeautifulSoup
import html
import json
import logging
import math

from src.models import Grant

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


# TODO(LS): This code could probably be simplified.
def _extract_total_budget(entry):
    """Extract total funding amount from various budget JSON formats."""
    if entry in (None, "", "{}", "[]"):
        return math.nan
    if isinstance(entry, float) and math.isnan(entry):
        return math.nan

    try:
        # Parse JSON if it's a string
        data = json.loads(entry) if isinstance(entry, str) else entry

        # Handle case where it's a list of JSON strings or dicts
        if isinstance(data, list):
            # If list of JSON strings, parse them
            parsed = []
            for item in data:
                if isinstance(item, str):
                    try:
                        parsed.append(json.loads(item))
                    except Exception:
                        continue
                elif isinstance(item, dict):
                    parsed.append(item)
            data = parsed[0] if len(parsed) == 1 else parsed

        if isinstance(data, dict) and "budgetTopicActionMap" in data:
            return (
                sum(
                    int(str(val).replace(",", "").strip())
                    for actions in data["budgetTopicActionMap"].values()
                    for a in actions
                    for val in a.get("budgetYearMap", {}).values()
                    if str(val).strip().isdigit()
                )
                or math.nan
            )

        if isinstance(data, dict):
            return data.get("totalBudget") or data.get("budget") or math.nan

        return math.nan

    except Exception:
        return math.nan


def _get_meta(grant, key, default=None):
    meta = grant.get("metadata", {})
    values = meta.get(key)
    if isinstance(values, list) and values:
        return values[0]
    return default


def process_grant(raw_grant) -> Grant:
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
        total_funding_opportunity=_extract_total_budget(
            _get_meta(raw_grant, "budgetOverview")
        ),
    )


def process_grants(raw_grants):
    """Process a batch of raw grants and return their Grant models."""
    return [process_grant(grant).model_dump() for grant in raw_grants]
