# Evals

Executable evals live in `evals/search_eval.py`.

## Metrics

- `recall@k`: fraction of expected grants retrieved.
- `precision@k`: fraction of retrieved grants that are expected.
- `mrr@k`: reciprocal rank of the first expected grant.
- `negative_false_positive_rate`: fraction of negative pitches that return any grant.

## Modes

- `smoke`: fast fixture-backed check for PRs and local harness validation.
- `full`: same executable path with stricter baseline thresholds.

Notebooks under `evals/notebooks` are exploratory reports only. They are not the source of truth for automated quality gates.
