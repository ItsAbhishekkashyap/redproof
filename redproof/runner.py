"""Run pytest and load the structured outcomes recorded by the plugin."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import redproof


@dataclass(frozen=True)
class TestOutcome:
    __test__ = False  # keep pytest from collecting this data class

    outcome: str
    error_type: str | None = None


@dataclass
class RunResult:
    outcomes: dict[str, TestOutcome]
    file_errors: dict[str, TestOutcome]
    timed_out: bool = False


def _relative_test_path(folder: Path, test_file: Path) -> str:
    candidate = test_file if test_file.is_absolute() else folder / test_file
    try:
        return candidate.resolve().relative_to(folder.resolve()).as_posix()
    except ValueError:
        raise ValueError(f"Test file must be inside {folder}: {test_file}") from None


def _pythonpath(folder: Path) -> str:
    entries = [str(folder.resolve())]
    source_folder = folder / "src"
    if source_folder.is_dir():
        entries.append(str(source_folder.resolve()))
    entries.append(str(Path(redproof.__file__).resolve().parent.parent))
    return os.pathsep.join(entries)


def _build_command(test_paths: list[str]) -> list[str]:
    return [
        sys.executable,
        "-m",
        "pytest",
        *test_paths,
        "-q",
        "--continue-on-collection-errors",
        "-p",
        "no:cacheprovider",
        "-p",
        "redproof.outcomes",
    ]


def _load_outcomes(
    output_path: Path,
) -> tuple[dict[str, TestOutcome], dict[str, TestOutcome]]:
    if not output_path.is_file():
        return {}, {}

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    outcomes = {
        nodeid: TestOutcome(item["outcome"], item.get("error_type"))
        for nodeid, item in payload.get("tests", {}).items()
    }
    file_errors = {
        path: TestOutcome(item["outcome"], item.get("error_type"))
        for path, item in payload.get("collection_errors", {}).items()
    }
    return outcomes, file_errors


def run_tests(folder: Path, test_files: list[Path], timeout: int = 60) -> RunResult:
    """Run the selected tests in folder and return structured outcomes."""
    folder = folder.resolve()
    test_paths = [_relative_test_path(folder, path) for path in test_files]

    with tempfile.TemporaryDirectory(prefix="redproof-outcomes-") as temp_dir:
        output_path = Path(temp_dir) / "outcomes.json"
        env = os.environ.copy()
        env["PYTHONPATH"] = _pythonpath(folder)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["REDPROOF_OUT"] = str(output_path)

        try:
            subprocess.run(
                _build_command(test_paths),
                cwd=folder,
                env=env,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            file_errors = {
                path: TestOutcome("error", "Timeout") for path in test_paths
            }
            return RunResult({}, file_errors, timed_out=True)

        outcomes, file_errors = _load_outcomes(output_path)
        return RunResult(outcomes, file_errors)