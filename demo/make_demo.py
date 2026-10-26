"""Create a demo repository with a committed bug and an uncommitted fix.

Usage:
    python demo/make_demo.py <target_folder>

The generated repository is intentionally left with the agent's work
uncommitted, because that is how agents often leave changes behind.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REDPROOF_ROOT = Path(__file__).resolve().parents[1]

BASE_PRICING = '''\
def apply_discount(total: float) -> float:
    """Orders of 100 or more get 10% off."""
    if total > 100:          # BUG: should be >= 100
        return round(total * 0.9, 2)
    return total
'''

FIXED_PRICING = '''\
def apply_discount(total: float) -> float:
    """Orders of 100 or more get 10% off."""
    if total >= 100:
        return round(total * 0.9, 2)
    return total


def format_price(amount: float) -> str:
    """Format an amount for display."""
    return f"Rs {amount:.2f}"
'''

BASE_TEST = '''\
from shop.pricing import apply_discount


def test_small_order_has_no_discount() -> None:
    assert apply_discount(50) == 50
'''

DISCOUNT_TESTS = '''\
from shop.pricing import apply_discount


def test_discount_at_exactly_100() -> None:
    assert apply_discount(100) == 90


def test_discount_returns_something() -> None:
    assert apply_discount(150) is not None
'''

FORMAT_TESTS = '''\
from shop.pricing import format_price


def test_format_price() -> None:
    assert format_price(5) == "Rs 5.00"
'''

EXPECTED_VERDICTS = {
    "tests/test_discount.py::test_discount_at_exactly_100": "REAL",
    "tests/test_discount.py::test_discount_returns_something": "FAKE",
    "tests/test_format.py::test_format_price": "INCONCLUSIVE",
}


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _prepare_target(target: Path) -> None:
    resolved = target.resolve()
    if resolved == REDPROOF_ROOT or resolved.is_relative_to(REDPROOF_ROOT):
        raise SystemExit(
            f"Refusing to create the demo inside the Redproof repository: {resolved}"
        )
    if target.exists() and any(target.iterdir()):
        raise SystemExit(f"Target folder is not empty: {target}")
    target.mkdir(parents=True, exist_ok=True)


def _create_base_commit(repo: Path) -> None:
    _write(repo / "shop" / "__init__.py", "")
    _write(repo / "shop" / "pricing.py", BASE_PRICING)
    _write(repo / "tests" / "__init__.py", "")
    _write(repo / "tests" / "test_basic.py", BASE_TEST)
    _write(repo / "conftest.py", "")

    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Demo")
    _git(repo, "config", "user.email", "demo@example.com")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "base: shop with discount bug")


def _apply_agent_changes(repo: Path) -> None:
    _write(repo / "shop" / "pricing.py", FIXED_PRICING)
    _write(repo / "tests" / "test_discount.py", DISCOUNT_TESTS)
    _write(repo / "tests" / "test_format.py", FORMAT_TESTS)


def make_demo(target: Path) -> Path:
    """Build the demo repository at target and return its resolved path."""
    _prepare_target(target)
    _create_base_commit(target)
    _apply_agent_changes(target)
    return target.resolve()


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("Usage: python demo/make_demo.py <target_folder>", file=sys.stderr)
        return 2

    repo = make_demo(Path(args[0]))
    print(f"Demo repository: {repo}")
    print("Uncommitted agent changes are present.")
    print("Expected verdicts:")
    for nodeid, verdict in EXPECTED_VERDICTS.items():
        print(f"  {nodeid} -> {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())