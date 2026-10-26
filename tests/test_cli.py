from redproof import __version__
from redproof.cli import main


def test_version_is_exposed() -> None:
    assert __version__ == "0.1.0"


def test_main_prints_version(capsys) -> None:
    assert main() == 0
    assert capsys.readouterr().out.strip() == "redproof 0.1.0"