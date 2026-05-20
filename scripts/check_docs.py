#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_FILES = [
    path
    for path in ROOT.rglob("*.md")
    if not any(part in {".git", "node_modules", ".next", "venv", ".venv"} for part in path.parts)
]
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FORBIDDEN_PATTERNS = [
    re.compile(r"`search-engine`"),
    re.compile(r"search-engine/"),
    re.compile(r"Python 3\.13"),
]


def _target_exists(source: Path, target: str) -> bool:
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return True
    target_path = target.split("#", 1)[0]
    if not target_path:
        return True
    return (source.parent / target_path).resolve().exists()


def main() -> int:
    failures: list[str] = []
    for path in MARKDOWN_FILES:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)

        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                failures.append(f"{rel}: forbidden stale reference `{pattern.pattern}`")

        for match in LINK_RE.finditer(text):
            target = match.group(1).strip()
            if not _target_exists(path, target):
                failures.append(f"{rel}: broken link `{target}`")

    if failures:
        print("Documentation check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Documentation check passed for {len(MARKDOWN_FILES)} markdown files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
