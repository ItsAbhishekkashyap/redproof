from __future__ import annotations

from pathlib import Path

from redproof.runner import TestOutcome, run_tests


def _write(project: Path, relative: str, content: str) -> None:
    path = project / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_records_passed_and_failed_tests(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "tests/test_sample.py",
        "def test_passes():\n"
        "    assert 1 + 1 == 2\n"
        "\n"
        "def test_fails():\n"
        "    assert 1 + 1 == 3\n",
    )

    result = run_tests(tmp_path, [Path("tests/test_sample.py")])

    assert result.outcomes["tests/test_sample.py::test_passes"] == TestOutcome(
        "passed", None
    )
    assert result.outcomes["tests/test_sample.py::test_fails"] == TestOutcome(
        "failed", "AssertionError"
    )
    assert result.file_errors == {}
    assert not result.timed_out


def test_collection_error_does_not_stop_other_tests(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "tests/test_good.py",
        "def test_good():\n    assert True\n",
    )
    _write(tmp_path, "tests/test_broken.py", "import missing_dependency_xyz\n")

    result = run_tests(
        tmp_path,
        [Path("tests/test_good.py"), Path("tests/test_broken.py")],
    )

    assert result.outcomes["tests/test_good.py::test_good"] == TestOutcome(
        "passed", None
    )
    assert result.file_errors["tests/test_broken.py"] == TestOutcome(
        "error", "CollectionError"
    )


def test_timeout_marks_every_file(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "tests/test_slow.py",
        "import time\n\n"
        "def test_slow():\n"
        "    time.sleep(5)\n",
    )

    result = run_tests(tmp_path, [Path("tests/test_slow.py")], timeout=1)

    assert result.timed_out
    assert result.outcomes == {}
    assert result.file_errors["tests/test_slow.py"] == TestOutcome("error", "Timeout")