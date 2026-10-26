from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

import redproof.check
from redproof.check import (
    BROKEN,
    FAKE,
    INCONCLUSIVE,
    REAL,
    check,
    classify_test,
)
from redproof.runner import TestOutcome

DEMO_SCRIPT = Path(__file__).resolve().parents[1] / "demo" / "make_demo.py"


def _load_demo_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("make_demo", DEMO_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def demo() -> ModuleType:
    return _load_demo_module()


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _git_output(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def _make_clean_repo(repo: Path) -> None:
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "config", "user.email", "test@example.com")
    tests = repo / "tests"
    tests.mkdir()
    (tests / "test_old.py").write_text(
        "def test_old():\n    assert True\n", encoding="utf-8"
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "base")


@pytest.mark.parametrize(
    ("old", "new", "expected", "reason_fragment"),
    [
        (
            TestOutcome("failed", "AssertionError"),
            TestOutcome("passed"),
            REAL,
            "catches the bug",
        ),
        (TestOutcome("failed", "Failed"), TestOutcome("passed"), REAL, "assertion"),
        (TestOutcome("passed"), TestOutcome("passed"), FAKE, "cannot catch"),
        (
            TestOutcome("error", "ImportError"),
            TestOutcome("passed"),
            INCONCLUSIVE,
            "proves nothing",
        ),
        (
            TestOutcome("error", "ModuleNotFoundError"),
            TestOutcome("passed"),
            INCONCLUSIVE,
            "proves nothing",
        ),
        (
            TestOutcome("failed", "TypeError"),
            TestOutcome("passed"),
            INCONCLUSIVE,
            "proves nothing",
        ),
        (
            TestOutcome("error", "CollectionError"),
            TestOutcome("passed"),
            INCONCLUSIVE,
            "proves nothing",
        ),
        (
            TestOutcome("error", "Timeout"),
            TestOutcome("passed"),
            INCONCLUSIVE,
            "proves nothing",
        ),
        (
            TestOutcome("passed"),
            TestOutcome("skipped"),
            INCONCLUSIVE,
            "Skipped on the new code",
        ),
        (
            TestOutcome("skipped"),
            TestOutcome("passed"),
            INCONCLUSIVE,
            "Skipped on the old code",
        ),
        (
            TestOutcome("failed", "AssertionError"),
            TestOutcome("failed", "AssertionError"),
            BROKEN,
            "new code",
        ),
        (
            TestOutcome("passed"),
            TestOutcome("error", "ImportError"),
            BROKEN,
            "new code",
        ),
        (
            TestOutcome("error", "Timeout"),
            TestOutcome("error", "Timeout"),
            BROKEN,
            "new code",
        ),
    ],
)
def test_verdict_rules(
    old: TestOutcome,
    new: TestOutcome,
    expected: str,
    reason_fragment: str,
) -> None:
    result = classify_test("tests/test_sample.py::test_case", old, new)

    assert result.verdict == expected
    assert reason_fragment in result.reason
    assert result.nodeid == "tests/test_sample.py::test_case"
    assert result.file == "tests/test_sample.py"
    assert result.old_outcome == old.outcome
    assert result.old_error_type == old.error_type
    assert result.new_outcome == new.outcome
    assert result.new_error_type == new.error_type


def test_reports_when_no_tests_changed(tmp_path: Path) -> None:
    repo = tmp_path / "clean-repo"
    _make_clean_repo(repo)

    report = check(repo, base="HEAD")

    assert report.message == "No new or changed tests found."
    assert report.results == []
    assert report.counts == {REAL: 0, FAKE: 0, INCONCLUSIVE: 0, BROKEN: 0}


def test_worktree_is_removed_when_running_tests_fails(
    tmp_path: Path, demo: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = demo.make_demo(tmp_path / "demo-repo")
    before = _git_output(repo, "worktree", "list", "--porcelain")

    def explode(*args, **kwargs):
        raise RuntimeError("runner exploded")

    monkeypatch.setattr(redproof.check, "run_tests", explode)

    with pytest.raises(RuntimeError, match="runner exploded"):
        check(repo, base="HEAD")

    after = _git_output(repo, "worktree", "list", "--porcelain")
    assert after == before
    worktrees = [line for line in after.splitlines() if line.startswith("worktree ")]
    assert len(worktrees) == 1


def test_demo_repository_verdicts(tmp_path: Path, demo: ModuleType) -> None:
    repo = demo.make_demo(tmp_path / "demo-repo")
    status_before = _git_output(repo, "status", "--porcelain")

    report = check(repo, base="HEAD")

    verdicts = {result.nodeid: result.verdict for result in report.results}
    assert verdicts == {
        "tests/test_discount.py::test_discount_at_exactly_100": REAL,
        "tests/test_discount.py::test_discount_returns_something": FAKE,
        "tests/test_format.py::test_format_price": INCONCLUSIVE,
    }
    assert report.counts == {REAL: 1, FAKE: 1, INCONCLUSIVE: 1, BROKEN: 0}
    assert report.message is None
    assert _git_output(repo, "status", "--porcelain") == status_before