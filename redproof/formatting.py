"""Small shared helpers that turn check results into readable text."""

from __future__ import annotations

from pathlib import Path


def short_test_name(nodeid: str) -> str:
    """Turn tests/test_x.py::test_y into test_x.py::test_y."""
    test_file, _, test_name = nodeid.partition("::")
    file_name = Path(test_file).name
    return f"{file_name}::{test_name}" if test_name else file_name


def describe_outcome(outcome: str, error_type: str | None) -> str:
    if outcome == "passed":
        return "passes"
    if outcome == "skipped":
        return "skipped"
    if outcome == "failed":
        return f"fails ({error_type})" if error_type else "fails"
    return f"error ({error_type})" if error_type else "error"


def describe_result(result: str) -> str:
    return result.replace("_", " ")