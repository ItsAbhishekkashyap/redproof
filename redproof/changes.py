"""Find test and conftest files changed since a git ref."""

from __future__ import annotations

import subprocess
from pathlib import Path


def _run_git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout


def _is_test_file(path: Path) -> bool:
    name = path.name
    return (name.startswith("test_") and name.endswith(".py")) or name.endswith(
        "_test.py"
    )


def _is_conftest(path: Path) -> bool:
    return path.name == "conftest.py"


def _validate_ref(repo: Path, base: str) -> None:
    completed = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        raise ValueError(f"Unknown git ref: {base}")


def _split_null(output: str) -> list[str]:
    return [entry for entry in output.split("\0") if entry]


def find_changed_tests(repo: Path, base: str) -> list[Path]:
    """Return changed test and conftest paths relative to repo.

    Uncommitted and untracked files are included; deleted files are skipped.
    """
    repo = repo.resolve()
    _validate_ref(repo, base)

    tracked = _split_null(_run_git(repo, "diff", "--name-only", "-z", base, "--"))
    untracked = _split_null(
        _run_git(repo, "ls-files", "--others", "--exclude-standard", "-z")
    )

    changed: list[Path] = []
    for relative_name in sorted(set(tracked) | set(untracked)):
        relative = Path(relative_name)
        # Redproof's own reports live here and are never test inputs.
        if ".redproof" in relative.parts:
            continue
        if not (repo / relative).is_file():
            continue
        if _is_test_file(relative) or _is_conftest(relative):
            changed.append(relative)
    return changed