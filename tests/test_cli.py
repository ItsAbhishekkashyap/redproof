from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

import pytest

from redproof import __version__
from redproof.check import (
    BROKEN,
    FAKE,
    INCONCLUSIVE,
    REAL,
    Report,
    TestResult,
)
from redproof.cli import main

ONLY_REAL_TESTS = (
    "from shop.pricing import apply_discount\n"
    "\n"
    "\n"
    "def test_discount_at_exactly_100() -> None:\n"
    "    assert apply_discount(100) == 90\n"
)

BROKEN_TESTS = (
    "from shop.pricing import apply_discount\n"
    "\n"
    "\n"
    "def test_discount_at_exactly_100() -> None:\n"
    "    assert apply_discount(100) == 90\n"
    "\n"
    "\n"
    "def test_discount_returns_something() -> None:\n"
    "    assert apply_discount(150) is not None\n"
    "\n"
    "\n"
    "def test_broken_expectation() -> None:\n"
    "    assert apply_discount(150) == 999\n"
)


def _make_report(*verdicts: str) -> Report:
    counts = {REAL: 0, FAKE: 0, INCONCLUSIVE: 0, BROKEN: 0}
    results = []
    for position, verdict in enumerate(verdicts):
        counts[verdict] += 1
        results.append(
            TestResult(
                nodeid=f"tests/test_sample.py::test_{position}",
                file="tests/test_sample.py",
                old_outcome="failed",
                old_error_type="AssertionError",
                new_outcome="passed",
                new_error_type=None,
                verdict=verdict,
                reason="Sample reason.",
            )
        )
    return Report(repo=Path("repo"), base="main", results=results, counts=counts)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _run_cli(repo: Path, *extra: str) -> int:
    return main(["check", "--repo", str(repo), "--base", "HEAD", *extra])


@pytest.mark.parametrize(
    ("verdicts", "result", "counts"),
    [
        ((), "NOTHING_TO_CHECK", (0, 0, 0, 0)),
        ((REAL,), "PROVEN", (1, 0, 0, 0)),
        ((REAL, REAL), "PROVEN", (2, 0, 0, 0)),
        ((FAKE,), "FAKE_TESTS_FOUND", (0, 1, 0, 0)),
        ((BROKEN,), "BROKEN_TESTS", (0, 0, 1, 0)),
        ((INCONCLUSIVE,), "UNVERIFIED", (0, 0, 0, 1)),
        ((REAL, INCONCLUSIVE), "UNVERIFIED", (1, 0, 0, 1)),
        ((REAL, FAKE, INCONCLUSIVE), "FAKE_TESTS_FOUND", (1, 1, 0, 1)),
        ((FAKE, BROKEN), "BROKEN_TESTS", (0, 1, 1, 0)),
    ],
)
def test_summary_result_rules(
    verdicts: tuple[str, ...],
    result: str,
    counts: tuple[int, int, int, int],
) -> None:
    report = _make_report(*verdicts)

    summary = report.summary()

    assert summary["result"] == result
    assert (
        summary["verified"],
        summary["fake"],
        summary["broken"],
        summary["unverified"],
    ) == counts
    assert report.to_dict()["summary"] == summary


def test_exit_code_proven(demo_repo: Path) -> None:
    (demo_repo / "tests" / "test_format.py").unlink()
    (demo_repo / "tests" / "test_discount.py").write_text(
        ONLY_REAL_TESTS, encoding="utf-8"
    )

    assert _run_cli(demo_repo) == 0


def test_exit_code_fake_tests_found(demo_repo: Path, capsys) -> None:
    assert _run_cli(demo_repo) == 1

    output = capsys.readouterr().out
    assert "FAKE" in output
    assert "Verified: 1   Fake: 1   Broken: 0   Unverified: 1" in output


def test_exit_code_broken_tests(demo_repo: Path, capsys) -> None:
    (demo_repo / "tests" / "test_format.py").unlink()
    (demo_repo / "tests" / "test_discount.py").write_text(
        BROKEN_TESTS, encoding="utf-8"
    )

    assert _run_cli(demo_repo) == 1
    assert "BROKEN" in capsys.readouterr().out


def test_exit_code_unverified(demo_repo: Path, capsys) -> None:
    (demo_repo / "tests" / "test_discount.py").unlink()

    assert _run_cli(demo_repo) == 2
    assert "Verified: 0   Fake: 0   Broken: 0   Unverified: 1" in (
        capsys.readouterr().out
    )


def test_exit_code_nothing_to_check(demo_repo: Path, capsys) -> None:
    _git(demo_repo, "add", "-A")
    _git(demo_repo, "commit", "-m", "agent work")

    assert _run_cli(demo_repo) == 2
    assert "No new or changed tests found, nothing to verify." in (
        capsys.readouterr().out
    )


def test_exit_code_for_not_a_git_repository(tmp_path: Path, capsys) -> None:
    plain_folder = tmp_path / "plain"
    plain_folder.mkdir()

    assert main(["check", "--repo", str(plain_folder)]) == 3

    error = capsys.readouterr().err
    assert "Not a git repository" in error
    assert "Traceback" not in error


def test_exit_code_for_missing_repository(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "does-not-exist"

    assert main(["check", "--repo", str(missing)]) == 3

    assert "does not exist" in capsys.readouterr().err


def test_exit_code_for_unknown_base_ref(demo_repo: Path, capsys) -> None:
    assert main(["check", "--repo", str(demo_repo), "--base", "not-a-ref"]) == 3

    assert "Unknown git ref: not-a-ref" in capsys.readouterr().err


def test_json_prints_only_json(demo_repo: Path, capsys) -> None:
    exit_code = _run_cli(demo_repo, "--json")

    output = capsys.readouterr().out
    payload = json.loads(output)

    assert exit_code == 1
    assert output.strip().startswith("{")
    assert output.strip().endswith("}")
    assert "\x1b" not in output
    assert payload["summary"]["result"] == "FAKE_TESTS_FOUND"
    assert len(payload["results"]) == 3


def test_html_contains_tests_and_banner(demo_repo: Path, tmp_path: Path) -> None:
    html_path = tmp_path / "report.html"

    assert _run_cli(demo_repo, "--html", str(html_path)) == 1

    html = html_path.read_text(encoding="utf-8")
    assert "test_discount.py::test_discount_at_exactly_100" in html
    assert "test_discount.py::test_discount_returns_something" in html
    assert "test_format.py::test_format_price" in html
    assert "FAKE TESTS FOUND" in html
    assert "1 test would pass even if the bug was never fixed." in html
    assert "http://" not in html
    assert "https://" not in html


def test_history_appends_rounds(demo_repo: Path, tmp_path: Path) -> None:
    history_path = tmp_path / "history.jsonl"
    html_path = tmp_path / "report.html"

    assert _run_cli(demo_repo, "--history", str(history_path)) == 1
    assert (
        _run_cli(
            demo_repo,
            "--history",
            str(history_path),
            "--html",
            str(html_path),
        )
        == 1
    )

    entries = [
        json.loads(line)
        for line in history_path.read_text(encoding="utf-8").splitlines()
    ]
    assert [entry["round"] for entry in entries] == [1, 2]
    assert entries[0]["summary"]["result"] == "FAKE_TESTS_FOUND"
    assert entries[1]["summary"]["verified"] == 1
    assert datetime.fromisoformat(entries[0]["time"])
    assert "Rounds" in html_path.read_text(encoding="utf-8")


def test_version_flag_prints_version(capsys) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])

    assert exit_info.value.code == 0
    assert capsys.readouterr().out.strip() == f"redproof {__version__}"


def test_version_is_exposed() -> None:
    assert __version__ == "0.1.0"