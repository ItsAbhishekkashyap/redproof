from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import redproof

MIXED_TESTS = '''\
import pytest


@pytest.fixture
def broken_fixture():
    raise ImportError("fixture dependency missing")


def test_passes():
    assert True


def test_fails():
    assert False


def test_raises_type_error():
    raise TypeError("boom")


def test_skipped():
    pytest.skip("not relevant")


def test_fixture_error(broken_fixture):
    assert True
'''

COLLECTION_ERROR = "import dependency_that_does_not_exist\n"


def test_plugin_records_outcomes_and_collection_errors(tmp_path: Path) -> None:
    project = tmp_path / "project"
    tests = project / "tests"
    tests.mkdir(parents=True)
    (tests / "test_mixed.py").write_text(MIXED_TESTS, encoding="utf-8")
    (tests / "test_broken_collection.py").write_text(
        COLLECTION_ERROR, encoding="utf-8"
    )

    output = tmp_path / "outcomes.json"
    env = os.environ.copy()
    env["REDPROOF_OUT"] = str(output)
    env["PYTHONPATH"] = str(Path(redproof.__file__).resolve().parent.parent)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--tb=no",
            "--continue-on-collection-errors",
            "-p",
            "no:cacheprovider",
            "-p",
            "redproof.outcomes",
        ],
        cwd=project,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    tests_by_name = {
        nodeid.split("::", 1)[1]: result
        for nodeid, result in payload["tests"].items()
        if "::" in nodeid
    }

    assert tests_by_name["test_passes"]["outcome"] == "passed"
    assert tests_by_name["test_passes"]["error_type"] is None
    assert tests_by_name["test_fails"]["outcome"] == "failed"
    assert tests_by_name["test_fails"]["error_type"] == "AssertionError"
    assert tests_by_name["test_raises_type_error"]["outcome"] == "failed"
    assert tests_by_name["test_raises_type_error"]["error_type"] == "TypeError"
    assert tests_by_name["test_skipped"]["outcome"] == "skipped"
    assert tests_by_name["test_fixture_error"]["outcome"] == "error"
    assert tests_by_name["test_fixture_error"]["error_type"] == "ImportError"

    assert payload["collection_errors"] == {
        "tests/test_broken_collection.py": {
            "outcome": "error",
            "error_type": "CollectionError",
        }
    }