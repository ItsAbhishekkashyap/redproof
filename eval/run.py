"""Run the six eval cases, including a line-coverage baseline.

Usage: python eval/run.py
"""

from __future__ import annotations

import json
import re
import statistics
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from eval.cases import CASES, EvalCase, build_case
from redproof.check import check

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


@dataclass
class CaseResult:
    case: str
    expected: str
    verdict: str
    correct: bool
    coverage_percent: float
    coverage_approved: bool
    seconds: float


def _git_output(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout


def changed_lines_from_diff(repo: Path) -> dict[str, set[int]]:
    """Map each changed file to the line numbers it has in the new file."""
    diff = _git_output(repo, "diff", "-U0", "HEAD", "--")
    changed: dict[str, set[int]] = {}
    current_file: str | None = None

    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[len("+++ b/") :]
            changed.setdefault(current_file, set())
        elif line.startswith("@@") and current_file is not None:
            match = HUNK.match(line)
            if match is None:
                continue
            start = int(match.group(1))
            count = int(match.group(2) or "1")
            changed[current_file].update(range(start, start + count))

    return {path: lines for path, lines in changed.items() if lines}


def _coverage_run(repo: Path) -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "coverage", "run", "-m", "pytest", "-q"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode not in (0, 1):
        raise RuntimeError(
            f"coverage run failed in {repo}:\n{completed.stderr.strip()}"
        )


def executed_lines_from_coverage(repo: Path) -> dict[str, set[int]]:
    """Map repo-relative source files to the lines coverage executed."""
    json_path = repo / "coverage.json"
    completed = subprocess.run(
        [sys.executable, "-m", "coverage", "json", "-o", str(json_path)],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if not json_path.is_file():
        raise RuntimeError(
            f"coverage json failed in {repo}:\n{completed.stderr.strip()}"
        )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    executed: dict[str, set[int]] = {}
    for path, data in payload.get("files", {}).items():
        candidate = Path(path)
        if candidate.is_absolute():
            try:
                relative = candidate.resolve().relative_to(repo.resolve())
            except ValueError:
                continue
        else:
            relative = candidate
        executed[relative.as_posix()] = set(data.get("executed_lines", []))
    return executed


def changed_line_coverage(repo: Path) -> float:
    changed = changed_lines_from_diff(repo)
    _coverage_run(repo)
    executed = executed_lines_from_coverage(repo)

    total = 0
    covered = 0
    for path, lines in changed.items():
        total += len(lines)
        covered += len(lines & executed.get(path, set()))
    return 100.0 * covered / total if total else 0.0


def evaluate_case(case: EvalCase, root: Path) -> CaseResult:
    repo = build_case(case, root)

    started = time.perf_counter()
    report = check(repo, base="HEAD")
    seconds = time.perf_counter() - started

    if not report.results:
        raise RuntimeError(f"Case {case.name} produced no test results")
    verdict = report.results[0].verdict

    percent = changed_line_coverage(repo)
    return CaseResult(
        case=case.name,
        expected=case.expected,
        verdict=verdict,
        correct=verdict == case.expected,
        coverage_percent=percent,
        coverage_approved=percent >= 90.0,
        seconds=seconds,
    )


def _table(results: list[CaseResult]) -> str:
    lines = [
        "| case | expected | Redproof verdict | correct? | changed-line "
        "coverage | coverage approves? | seconds |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(
            f"| {result.case} | {result.expected} | {result.verdict} | "
            f"{'yes' if result.correct else 'no'} | "
            f"{result.coverage_percent:.1f}% | "
            f"{'yes' if result.coverage_approved else 'no'} | "
            f"{result.seconds:.2f} |"
        )
    return "\n".join(lines)


def _summary(results: list[CaseResult]) -> str:
    fake = [result for result in results if result.expected == "FAKE"]
    coverage_approved = sum(1 for result in fake if result.coverage_approved)
    flagged = sum(1 for result in fake if result.verdict == "FAKE")
    correct = sum(1 for result in results if result.correct)
    median = statistics.median(result.seconds for result in results)
    return (
        f"Fake tests: coverage approved {coverage_approved} of {len(fake)}. "
        f"Redproof flagged {flagged} of {len(fake)}. "
        f"Redproof correct on {correct} of {len(results)} cases. "
        f"Median time per case: {median:.2f} s."
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="redproof-eval-") as temp_dir:
        root = Path(temp_dir)
        results = [evaluate_case(case, root) for case in CASES]

    output = f"# Redproof eval\n\n{_table(results)}\n\n{_summary(results)}\n"
    results_path = Path(__file__).resolve().parent / "results.md"
    results_path.write_text(output, encoding="utf-8", newline="\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())