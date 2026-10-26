from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from redproof.changes import find_changed_tests


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _write(repo: Path, relative: str, content: str = "") -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.name", "Test")
    _git(root, "config", "user.email", "test@example.com")

    _write(root, "conftest.py", "")
    _write(root, "tests/__init__.py", "")
    _write(root, "tests/test_existing.py", "def test_existing():\n    pass\n")
    _write(root, "tests/test_deleted.py", "def test_deleted():\n    pass\n")
    _write(root, "tests/helper.py", "")
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "base")
    return root


def test_finds_changed_and_untracked_test_files(repo: Path) -> None:
    _write(repo, "tests/test_existing.py", "def test_changed():\n    pass\n")
    _write(repo, "tests/test_untracked.py", "def test_new():\n    pass\n")
    _write(repo, "tests/other_test.py", "def test_other():\n    pass\n")
    _write(repo, "tests/helper.py", "VALUE = 1\n")
    _write(repo, "notes.txt", "not a test\n")

    changed = set(find_changed_tests(repo, "HEAD"))

    assert changed == {
        Path("tests/test_existing.py"),
        Path("tests/test_untracked.py"),
        Path("tests/other_test.py"),
    }


def test_finds_changed_conftests(repo: Path) -> None:
    _write(repo, "conftest.py", "import pytest\n")
    _write(repo, "tests/conftest.py", "import pytest\n")

    changed = set(find_changed_tests(repo, "HEAD"))

    assert Path("conftest.py") in changed
    assert Path("tests/conftest.py") in changed


def test_ignores_deleted_test_files(repo: Path) -> None:
    (repo / "tests" / "test_deleted.py").unlink()

    changed = find_changed_tests(repo, "HEAD")

    assert Path("tests/test_deleted.py") not in changed


def test_ignores_redproof_output_folder(repo: Path) -> None:
    _write(
        repo,
        ".redproof/test_should_be_ignored.py",
        "def test_ignored():\n    pass\n",
    )

    changed = find_changed_tests(repo, "HEAD")

    assert Path(".redproof/test_should_be_ignored.py") not in changed


def test_rejects_unknown_base_ref(repo: Path) -> None:
    with pytest.raises(ValueError, match="Unknown git ref: not-a-ref"):
        find_changed_tests(repo, "not-a-ref")