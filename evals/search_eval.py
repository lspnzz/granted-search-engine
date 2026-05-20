#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORD_RE = re.compile(r"[a-z0-9]+")
STOP_WORDS = {
    "a",
    "and",
    "are",
    "for",
    "in",
    "no",
    "of",
    "or",
    "the",
    "to",
    "we",
    "with",
}


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in WORD_RE.findall(text.lower())
        if token not in STOP_WORDS and len(token) > 2
    }


def _rank_grants(pitch: str, grants: list[dict], k: int) -> list[str]:
    pitch_tokens = _tokens(pitch)
    ranked = []
    for grant in grants:
        grant_text = " ".join(
            str(grant.get(field, ""))
            for field in ("id", "title", "summary", "description")
        )
        overlap = len(pitch_tokens & _tokens(grant_text))
        if overlap:
            ranked.append((overlap, grant["id"]))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [grant_id for _, grant_id in ranked[:k]]


def _metrics(golden: list[dict], grants: list[dict], k: int) -> dict[str, float]:
    recall_scores = []
    precision_scores = []
    reciprocal_ranks = []
    negative_total = 0
    negative_with_results = 0

    for case in golden:
        expected = set(case["matching_grant_ids"])
        retrieved = _rank_grants(case["pitch"], grants, k)
        retrieved_set = set(retrieved)

        if not expected:
            negative_total += 1
            if retrieved:
                negative_with_results += 1
            continue

        hits = expected & retrieved_set
        recall_scores.append(len(hits) / len(expected))
        precision_scores.append(len(hits) / max(len(retrieved), 1))

        rank = 0
        for idx, grant_id in enumerate(retrieved, 1):
            if grant_id in expected:
                rank = idx
                break
        reciprocal_ranks.append(1 / rank if rank else 0)

    return {
        "recall_at_k": round(sum(recall_scores) / len(recall_scores), 4),
        "precision_at_k": round(sum(precision_scores) / len(precision_scores), 4),
        "mrr_at_k": round(sum(reciprocal_ranks) / len(reciprocal_ranks), 4),
        "negative_false_positive_rate": round(
            negative_with_results / negative_total if negative_total else 0,
            4,
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    parser.add_argument("--k", type=int)
    args = parser.parse_args()

    baseline = _load_json(ROOT / "evals" / "baseline.json")
    golden = _load_json(ROOT / "evals" / "golden.json")
    grants = _load_json(ROOT / "tests" / "fixtures" / "grants.json")
    k = args.k or int(baseline["k"])

    results = _metrics(golden, grants, k)
    print(json.dumps({"mode": args.mode, "k": k, **results}, indent=2))

    min_recall = baseline["recall_at_k"] - baseline["max_recall_drop"]
    max_negative_fpr = baseline["max_negative_false_positive_rate"]

    failures = []
    if results["recall_at_k"] < min_recall:
        failures.append(
            f"recall_at_k {results['recall_at_k']} below minimum {min_recall}"
        )
    if results["negative_false_positive_rate"] > max_negative_fpr:
        failures.append(
            "negative_false_positive_rate "
            f"{results['negative_false_positive_rate']} above maximum {max_negative_fpr}"
        )

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
