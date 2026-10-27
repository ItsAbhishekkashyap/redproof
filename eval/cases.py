"""The six eval cases: tiny repositories with a bug and a candidate test."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


BUGGY_PRICING = '''\
def apply_discount(total: float) -> float:
    """Orders of 100 or more get 10% off."""
    if total > 100:          # BUG: should be >= 100
        return round(total * 0.9, 2)
    return total
'''

BOUNDARY_PRICING = '''\
def apply_discount(total: float) -> float:
    """Orders of 100 or more get 10% off."""
    if total >= 100:
        return round(total * 0.9, 2)
    return total
'''

VALIDATION_PRICING = '''\
def apply_discount(total: float) -> float:
    """Orders of 100 or more get 10% off."""
    if total < 0:
        raise ValueError("total must not be negative")
    if total >= 100:
        return round(total * 0.9, 2)
    return total
'''

FORMAT_PRICING = BOUNDARY_PRICING + '''

def format_price(amount: float) -> str:
    """Format an amount for display."""
    return f"Rs {amount:.2f}"
'''


@dataclass(frozen=True)
class EvalCase:
    name: str
    expected: str
    base_pricing: str
    new_pricing: str
    test_source: str


CASES = (
    EvalCase(
        name="boundary_real",
        expected="REAL",
        base_pricing=BUGGY_PRICING,
        new_pricing=BOUNDARY_PRICING,
        test_source=(
            "from shop.pricing import apply_discount\n"
            "\n"
            "\n"
            "def test_discount_at_exactly_100() -> None:\n"
            "    assert apply_discount(100) == 90\n"
        ),
    ),
    EvalCase(
        name="boundary_fake",
        expected="FAKE",
        base_pricing=BUGGY_PRICING,
        new_pricing=BOUNDARY_PRICING,
        test_source=(
            "from shop.pricing import apply_discount\n"
            "\n"
            "\n"
            "def test_discount_returns_something() -> None:\n"
            "    assert apply_discount(150) is not None\n"
        ),
    ),
    EvalCase(
        name="mock_fake",
        expected="FAKE",
        base_pricing=BUGGY_PRICING,
        new_pricing=BOUNDARY_PRICING,
        test_source=(
            "from unittest.mock import patch\n"
            "\n"
            "import shop.pricing\n"
            "\n"
            "\n"
            "def test_mocked_discount() -> None:\n"
            "    with patch.object(shop.pricing, \"apply_discount\", "
            "return_value=90.0):\n"
            "        assert shop.pricing.apply_discount(100) == 90.0\n"
        ),
    ),
    EvalCase(
        name="recompute_fake",
        expected="FAKE",
        base_pricing=BUGGY_PRICING,
        new_pricing=BOUNDARY_PRICING,
        test_source=(
            "from shop.pricing import apply_discount\n"
            "\n"
            "\n"
            "def test_matches_itself() -> None:\n"
            "    assert apply_discount(100) == apply_discount(100)\n"
        ),
    ),
    EvalCase(
        name="raises_real",
        expected="REAL",
        base_pricing=BUGGY_PRICING,
        new_pricing=VALIDATION_PRICING,
        test_source=(
            "import pytest\n"
            "\n"
            "from shop.pricing import apply_discount\n"
            "\n"
            "\n"
            "def test_negative_total_raises() -> None:\n"
            "    with pytest.raises(ValueError):\n"
            "        apply_discount(-1)\n"
        ),
    ),
    EvalCase(
        name="new_function_inconclusive",
        expected="INCONCLUSIVE",
        base_pricing=BUGGY_PRICING,
        new_pricing=FORMAT_PRICING,
        test_source=(
            "from shop.pricing import format_price\n"
            "\n"
            "\n"
            "def test_format_price() -> None:\n"
            "    assert format_price(5) == \"Rs 5.00\"\n"
        ),
    ),
)


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


def build_case(case: EvalCase, root: Path) -> Path:
    """Create the case repository with the fix and tests left uncommitted."""
    repo = root / case.name
    repo.mkdir(parents=True)

    _write(repo / "shop" / "__init__.py", "")
    _write(repo / "shop" / "pricing.py", case.base_pricing)
    _write(repo / "conftest.py", "")

    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Eval")
    _git(repo, "config", "user.email", "eval@example.com")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "base: shop with discount bug")

    _write(repo / "shop" / "pricing.py", case.new_pricing)
    _write(repo / "tests" / "test_case.py", case.test_source)
    return repo