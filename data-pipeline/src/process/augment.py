import json
import math


# TODO(LS): This code could probably be simplified.
def extract_total_budget(entry):
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
