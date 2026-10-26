from __future__ import annotations

from pathlib import Path
from types import ModuleType

from redproof.check import FAKE, REAL, check

REAL_BOUNDARY_TEST = (
    "from shop.pricing import apply_discount\n"
    "\n"
    "\n"
    "def test_discount_at_exactly_100() -> None:\n"
    "    assert apply_discount(100) == 90\n"
)


def test_loop_scenario_progresses_to_proven(
    tmp_path: Path, demo_module: ModuleType
) -> None:
    repo = demo_module.make_demo(tmp_path / "demo-repo", scenario="loop")
    test_file = repo / "tests" / "test_discount.py"

    report = check(repo, base="HEAD")
    assert report.summary()["result"] == "FAKE_TESTS_FOUND"
    assert report.summary()["fake"] == 1
    assert [result.verdict for result in report.results] == [FAKE]

    test_file.write_text(
        test_file.read_text(encoding="utf-8") + "\n\n" + REAL_BOUNDARY_TEST,
        encoding="utf-8",
    )

    report = check(repo, base="HEAD")
    verdicts = {result.nodeid: result.verdict for result in report.results}
    assert report.summary()["result"] == "FAKE_TESTS_FOUND"
    assert report.summary()["verified"] == 1
    assert report.summary()["fake"] == 1
    assert verdicts == {
        "tests/test_discount.py::test_discount_applied": FAKE,
        "tests/test_discount.py::test_discount_at_exactly_100": REAL,
    }

    test_file.write_text(
        "from shop.pricing import apply_discount\n"
        "\n"
        "\n"
        "def test_discount_applied() -> None:\n"
        "    assert apply_discount(100) == 90\n"
        "\n"
        "\n"
        "def test_discount_at_exactly_100() -> None:\n"
        "    assert apply_discount(100) == 90\n",
        encoding="utf-8",
    )

    report = check(repo, base="HEAD")
    assert report.summary()["result"] == "PROVEN"
    assert report.summary()["verified"] == 2
    assert report.summary()["fake"] == 0