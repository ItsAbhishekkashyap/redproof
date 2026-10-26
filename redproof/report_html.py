"""Render the single-file HTML report."""

from __future__ import annotations

from datetime import datetime, timezone
from importlib import resources
from pathlib import Path
from typing import Any, Sequence

from jinja2 import Environment

from redproof.check import INCONCLUSIVE, Report, TestResult
from redproof.formatting import describe_outcome, describe_result, short_test_name


def _tests(count: int) -> str:
    return f"{count} test" if count == 1 else f"{count} tests"


def _banner(summary: dict[str, Any]) -> dict[str, str]:
    result = summary["result"]
    if result == "PROVEN":
        verified = summary["verified"]
        if verified == 1:
            text = (
                "The changed test fails on the old code and passes on the new "
                "code, so the fix is covered."
            )
        else:
            text = (
                f"All {verified} changed tests fail on the old code and pass on "
                "the new code, so the fix is covered."
            )
        return {"title": "PROVEN", "tone": "good", "text": text}
    if result == "FAKE_TESTS_FOUND":
        return {
            "title": "FAKE TESTS FOUND",
            "tone": "bad",
            "text": (
                f"{_tests(summary['fake'])} would pass even if the bug was "
                "never fixed."
            ),
        }
    if result == "BROKEN_TESTS":
        return {
            "title": "BROKEN TESTS",
            "tone": "bad",
            "text": f"{_tests(summary['broken'])} failed on the current code.",
        }
    if result == "UNVERIFIED":
        return {
            "title": "UNVERIFIED",
            "tone": "warn",
            "text": (
                f"{_tests(summary['unverified'])} could not prove anything "
                "about the bug."
            ),
        }
    return {
        "title": "NOTHING TO CHECK",
        "tone": "muted",
        "text": "No new or changed tests were found.",
    }


def _result_row(result: TestResult) -> dict[str, str]:
    return {
        "name": short_test_name(result.nodeid),
        "old": describe_outcome(result.old_outcome, result.old_error_type),
        "new": describe_outcome(result.new_outcome, result.new_error_type),
        "verdict": result.verdict,
        "badge": result.verdict.lower(),
        "reason": result.reason,
    }


def _round_rows(rounds: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for entry in rounds:
        summary = entry.get("summary", {})
        rows.append(
            {
                "round": entry.get("round", "?"),
                "verified": summary.get("verified", 0),
                "fake": summary.get("fake", 0),
                "broken": summary.get("broken", 0),
                "unverified": summary.get("unverified", 0),
                "result": describe_result(str(summary.get("result", ""))),
            }
        )
    return rows


def _template_text() -> str:
    template = resources.files("redproof").joinpath("templates").joinpath("report.html")
    return template.read_text(encoding="utf-8")


def render_report(
    report: Report,
    rounds: Sequence[dict[str, Any]] = (),
    generated_at: datetime | None = None,
) -> str:
    """Render the report to a self-contained HTML document."""
    summary = report.summary()
    moment = generated_at or datetime.now(timezone.utc)
    context = {
        "repo_name": report.repo.name,
        "base": report.base,
        "generated_at": moment.strftime("%Y-%m-%d %H:%M UTC"),
        "summary": summary,
        "banner": _banner(summary),
        "results": [_result_row(result) for result in report.results],
        "unverified": [
            _result_row(result)
            for result in report.results
            if result.verdict == INCONCLUSIVE
        ],
        "rounds": _round_rows(rounds) if len(rounds) > 1 else [],
        "empty_message": report.message or "No tests were run.",
    }

    environment = Environment(autoescape=True)
    return environment.from_string(_template_text()).render(**context)


def write_report_html(
    report: Report,
    path: Path,
    rounds: Sequence[dict[str, Any]] = (),
    generated_at: datetime | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_report(report, rounds, generated_at),
        encoding="utf-8",
        newline="\n",
    )