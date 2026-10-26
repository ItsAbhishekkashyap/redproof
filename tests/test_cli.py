from __future__ import annotations

import subprocess

import pytest

from redproof import __version__
from redproof.cli import main


def test_version_is_exposed() -> None:
    assert __version__ == "0.1.0"


def test_version_flag_prints_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])

    assert exit_info.value.code == 0
    assert capsys.readouterr().out.strip() == f"redproof {__version__}"