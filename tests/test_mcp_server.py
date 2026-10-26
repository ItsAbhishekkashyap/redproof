from __future__ import annotations

import asyncio
from pathlib import Path

from redproof.mcp_server import TOOL_DESCRIPTION, mcp, redproof_check


def test_server_lists_exactly_one_tool() -> None:
    tools = asyncio.run(mcp.list_tools())

    assert len(tools) == 1
    tool = tools[0]
    assert tool.name == "redproof_check"
    assert tool.description == TOOL_DESCRIPTION
    assert tool.description.startswith(
        "Verify that the tests written for a bug fix actually catch the bug."
    )
    assert "FAKE = passes on both, so it cannot catch the bug." in tool.description


def test_tool_checks_demo_repo_and_writes_html(
    demo_repo: Path, tmp_path: Path
) -> None:
    html_path = tmp_path / "report.html"

    result = redproof_check(
        str(demo_repo), base="HEAD", html_path=str(html_path)
    )

    assert result["summary"]["result"] == "FAKE_TESTS_FOUND"
    assert len(result["next_steps"]) == 2
    assert any("is FAKE:" in step for step in result["next_steps"])
    assert any("is INCONCLUSIVE:" in step for step in result["next_steps"])
    assert result["html_report"] == str(html_path.resolve())
    assert html_path.is_file()
    assert "FAKE TESTS FOUND" in html_path.read_text(encoding="utf-8")


def test_tool_returns_error_for_non_git_folder(tmp_path: Path) -> None:
    plain_folder = tmp_path / "plain"
    plain_folder.mkdir()

    result = redproof_check(str(plain_folder))

    assert set(result) == {"error"}
    assert "Not a git repository" in result["error"]