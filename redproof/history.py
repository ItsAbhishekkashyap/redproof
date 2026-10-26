"""Read and append Redproof's JSON-lines history file."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from redproof.check import Report


def load_history(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        return [json.loads(line) for line in lines if line.strip()]
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Could not read history file {path}: {error}") from error


def append_history(path: Path, report: Report) -> list[dict[str, Any]]:
    """Append the current run and return every round including this one."""
    rounds = load_history(path)
    entry = {
        "round": len(rounds) + 1,
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "summary": report.summary(),
        "results": report.to_dict()["results"],
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(entry) + "\n")
    except OSError as error:
        raise ValueError(f"Could not write history file {path}: {error}") from error
    return [*rounds, entry]