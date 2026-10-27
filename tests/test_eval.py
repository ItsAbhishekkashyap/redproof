from __future__ import annotations

from pathlib import Path

from eval.cases import CASES
from eval.run import evaluate_case


def test_boundary_fake_case_is_fake(tmp_path: Path) -> None:
    case = next(case for case in CASES if case.name == "boundary_fake")

    result = evaluate_case(case, tmp_path)

    assert result.verdict == "FAKE"
    assert result.correct