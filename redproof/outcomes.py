"""Pytest plugin that records structured per-test outcomes as JSON.

Load with ``-p redproof.outcomes`` and set ``REDPROOF_OUT`` to the output
file path. Without ``REDPROOF_OUT`` the plugin is a no-op.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest

_RECORDS: dict[str, dict[str, Any]] = {}
_COLLECTION_ERRORS: dict[str, dict[str, str]] = {}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[Any]):
    outcome = yield
    report = outcome.get_result()

    record = _RECORDS.setdefault(
        item.nodeid, {"nodeid": item.nodeid, "phases": {}}
    )
    error_type = None
    if report.failed and call.excinfo is not None:
        error_type = call.excinfo.typename
    record["phases"][report.when] = {
        "outcome": report.outcome,
        "error_type": error_type,
    }


def pytest_collectreport(report: pytest.CollectReport) -> None:
    if not report.failed:
        return
    path = report.nodeid.split("::", 1)[0]
    if path.endswith(".py"):
        _COLLECTION_ERRORS[path] = {
            "outcome": "error",
            "error_type": "CollectionError",
        }


def _final_outcome(phases: dict[str, dict[str, Any]]) -> tuple[str, str | None]:
    setup = phases.get("setup")
    call = phases.get("call")

    if setup is None:
        return "error", "SetupMissing"
    if setup["outcome"] == "failed":
        return "error", setup["error_type"]
    if setup["outcome"] == "skipped":
        return "skipped", None
    if call is None:
        return "error", "CallMissing"
    if call["outcome"] == "failed":
        return "failed", call["error_type"]
    if call["outcome"] == "skipped":
        return "skipped", None

    teardown = phases.get("teardown")
    if teardown is not None and teardown["outcome"] == "failed":
        return "error", teardown["error_type"]
    return "passed", None


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    output_path = os.environ.get("REDPROOF_OUT")
    if not output_path:
        return

    tests: dict[str, dict[str, Any]] = {}
    for nodeid, record in _RECORDS.items():
        outcome, error_type = _final_outcome(record["phases"])
        tests[nodeid] = {
            "nodeid": nodeid,
            "outcome": outcome,
            "error_type": error_type,
            "phases": record["phases"],
        }

    payload = {"tests": tests, "collection_errors": _COLLECTION_ERRORS}
    Path(output_path).write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )