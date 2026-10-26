"""Resolve and validate a repository folder."""

from __future__ import annotations

import subprocess
from pathlib import Path


def resolve_repository(path: str | Path) -> Path:
    """Return the resolved repository folder or raise a friendly ValueError."""
    folder = Path(path).expanduser()
    if not folder.is_dir():
        raise ValueError(f"Repository folder does not exist: {folder}")

    resolved = folder.resolve()
    completed = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=resolved,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0 or completed.stdout.strip() != "true":
        raise ValueError(f"Not a git repository: {resolved}")
    return resolved