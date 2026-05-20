from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_search_eval_smoke_passes():
    result = subprocess.run(
        [sys.executable, "evals/search_eval.py", "--mode", "smoke"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert '"recall_at_k": 1.0' in result.stdout
