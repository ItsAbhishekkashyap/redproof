"""Check whether changed tests catch the bug fixed in the working tree."""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from redproof.changes import find_changed_tests
from redproof.runner import RunResult, TestOutcome, run_tests

REAL = "REAL"
FAKE = "FAKE"
INCONCLUSIVE = "INCONCLUSIVE"
BROKEN = "BROKEN"

VERDICTS = (REAL, FAKE, INCONCLUSIVE, BROKEN)
ASSERTION_ERRORS = {"AssertionError", "Failed"}


@dataclass(frozen=True)
class TestResult:
    __test__ = False  # keep pytest from collecting this data class

    nodeid: str
    file: str
    old_outcome: str
    old_error_type: str | None
    new_outcome: str
    new_error_type: str | None
    verdict: str
    reason: str


@dataclass
class Report:
    repo: Path
    base: str
    results: list[TestResult]
    counts: dict[str, int]
    message: str | None = None

    def summary(self) -> dict[str, Any]:
        """Return the shared verdict summary used by the CLI, HTML and MCP."""
        verified = self.counts.get(REAL, 0)
        fake = self.counts.get(FAKE, 0)
        broken = self.counts.get(BROKEN, 0)
        unverified = self.counts.get(INCONCLUSIVE, 0)

        if broken:
            result = "BROKEN_TESTS"
        elif fake:
            result = "FAKE_TESTS_FOUND"
        elif unverified:
            result = "UNVERIFIED"
        elif verified:
            result = "PROVEN"
        else:
            result = "NOTHING_TO_CHECK"

        return {
            "verified": verified,
            "fake": fake,
            "broken": broken,
            "unverified": unverified,
            "result": result,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo": str(self.repo),
            "base": self.base,
            "message": self.message,
            "counts": self.counts,
            "summary": self.summary(),
            "results": [asdict(result) for result in self.results],
        }


def _file_from_nodeid(nodeid: str) -> str:
    return nodeid.split("::", 1)[0]


def classify_test(
    nodeid: str, old: TestOutcome, new: TestOutcome
) -> TestResult:
    """Apply the Redproof verdict rules to one test's old and new outcomes."""
    file = _file_from_nodeid(nodeid)

    if new.outcome == "skipped":
        return TestResult(
            nodeid=nodeid,
            file=file,
            old_outcome=old.outcome,
            old_error_type=old.error_type,
            new_outcome=new.outcome,
            new_error_type=new.error_type,
            verdict=INCONCLUSIVE,
            reason="Skipped on the new code, so it proves nothing.",
        )

    if new.outcome != "passed":
        detail = new.error_type or new.outcome
        return TestResult(
            nodeid=nodeid,
            file=file,
            old_outcome=old.outcome,
            old_error_type=old.error_type,
            new_outcome=new.outcome,
            new_error_type=new.error_type,
            verdict=BROKEN,
            reason=f"Fails on the new code ({detail}).",
        )

    if old.outcome == "skipped":
        return TestResult(
            nodeid=nodeid,
            file=file,
            old_outcome=old.outcome,
            old_error_type=old.error_type,
            new_outcome=new.outcome,
            new_error_type=new.error_type,
            verdict=INCONCLUSIVE,
            reason="Skipped on the old code, so it proves nothing about the bug.",
        )

    if old.outcome == "passed":
        return TestResult(
            nodeid=nodeid,
            file=file,
            old_outcome=old.outcome,
            old_error_type=old.error_type,
            new_outcome=new.outcome,
            new_error_type=new.error_type,
            verdict=FAKE,
            reason="Passes even with the old buggy code, so it cannot catch this bug.",
        )

    if old.outcome == "failed" and old.error_type in ASSERTION_ERRORS:
        return TestResult(
            nodeid=nodeid,
            file=file,
            old_outcome=old.outcome,
            old_error_type=old.error_type,
            new_outcome=new.outcome,
            new_error_type=new.error_type,
            verdict=REAL,
            reason=(
                "Fails on the old code with an assertion and passes on the new "
                "code, so it catches the bug."
            ),
        )

    detail = old.error_type or old.outcome
    return TestResult(
        nodeid=nodeid,
        file=file,
        old_outcome=old.outcome,
        old_error_type=old.error_type,
        new_outcome=new.outcome,
        new_error_type=new.error_type,
        verdict=INCONCLUSIVE,
        reason=(
            f"Could not run on the old code ({detail}), so it proves nothing "
            "about the bug."
        ),
    )


def _empty_counts() -> dict[str, int]:
    return {verdict: 0 for verdict in VERDICTS}


def _count_verdicts(results: list[TestResult]) -> dict[str, int]:
    counts = _empty_counts()
    for result in results:
        counts[result.verdict] += 1
    return counts


def _lookup(run: RunResult, nodeid: str, file: str) -> TestOutcome:
    if nodeid in run.outcomes:
        return run.outcomes[nodeid]
    if file in run.file_errors:
        return run.file_errors[file]
    return TestOutcome("error", "MissingResult")


def _candidate_nodeids(old: RunResult, new: RunResult) -> list[str]:
    nodeids = list(new.outcomes)
    extra: list[str] = []

    if new.timed_out:
        # The new run never got far enough to report individual tests.
        extra = list(old.outcomes)
    else:
        # A file that failed collection on the new code still has tests that
        # were discovered on the old code; report those as broken.
        for file in new.file_errors:
            extra.extend(
                nodeid
                for nodeid in old.outcomes
                if _file_from_nodeid(nodeid) == file
            )

    return list(dict.fromkeys([*nodeids, *extra]))


def _classify_results(old: RunResult, new: RunResult) -> list[TestResult]:
    results = []
    for nodeid in _candidate_nodeids(old, new):
        file = _file_from_nodeid(nodeid)
        old_outcome = _lookup(old, nodeid, file)
        new_outcome = _lookup(new, nodeid, file)
        results.append(classify_test(nodeid, old_outcome, new_outcome))
    return results


def _add_worktree(repo: Path, worktree: Path, base: str) -> None:
    completed = subprocess.run(
        ["git", "worktree", "add", "--detach", str(worktree), base],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Could not create a worktree at {worktree}: "
            f"{completed.stderr.strip() or completed.stdout.strip()}"
        )


def _copy_changed_files(repo: Path, worktree: Path, test_files: list[Path]) -> None:
    for relative in test_files:
        source = repo / relative
        destination = worktree / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def _remove_readonly(function, path: str, _exception) -> None:
    os.chmod(path, stat.S_IWRITE)
    function(path)


def _remove_tree(folder: Path) -> None:
    """Delete folder even when git left read-only files behind."""
    if not folder.exists():
        return
    if sys.version_info >= (3, 12):
        shutil.rmtree(folder, onexc=_remove_readonly)
    else:
        shutil.rmtree(folder, onerror=_remove_readonly)


def _cleanup_worktree(repo: Path, worktree: Path, temp_dir: Path) -> None:
    subprocess.run(
        ["git", "worktree", "remove", "--force", str(worktree)],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "worktree", "prune"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    _remove_tree(temp_dir)


def check(repo: Path, base: str = "main", timeout: int = 60) -> Report:
    """Run changed tests against base and the working tree, then classify them."""
    repo = repo.resolve()
    test_files = find_changed_tests(repo, base)
    if not test_files:
        return Report(
            repo=repo,
            base=base,
            results=[],
            counts=_empty_counts(),
            message="No new or changed tests found.",
        )

    temp_dir = Path(tempfile.mkdtemp(prefix="redproof-worktree-"))
    worktree = temp_dir / "old"
    try:
        _add_worktree(repo, worktree, base)
        _copy_changed_files(repo, worktree, test_files)
        old = run_tests(worktree, test_files, timeout=timeout)
        new = run_tests(repo, test_files, timeout=timeout)
        results = _classify_results(old, new)
        return Report(
            repo=repo,
            base=base,
            results=results,
            counts=_count_verdicts(results),
        )
    finally:
        _cleanup_worktree(repo, worktree, temp_dir)