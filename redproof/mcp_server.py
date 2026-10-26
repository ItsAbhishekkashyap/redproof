"""MCP server exposing Redproof's check as a single tool.

Run over stdio with ``python -m redproof.mcp_server`` or over streamable HTTP
with ``python -m redproof.mcp_server --http --port 8765``.
"""

from __future__ import annotations

import argparse
from importlib.metadata import version
from pathlib import Path
from typing import Any, Sequence

try:
    from mcp.server.mcpserver import MCPServer
except ImportError:  # mcp 1.x shipped the same API as FastMCP
    from mcp.server.fastmcp import FastMCP as MCPServer  # type: ignore[assignment]

from redproof.check import BROKEN, FAKE, INCONCLUSIVE, Report, check
from redproof.history import append_history
from redproof.report_html import write_report_html
from redproof.repository import resolve_repository

TOOL_DESCRIPTION = (
    "Verify that the tests written for a bug fix actually catch the bug. "
    "Redproof runs the changed tests against the OLD code (the base git ref) "
    "and the NEW code (the working tree). REAL = fails on old code with an "
    "assertion and passes on new code. FAKE = passes on both, so it cannot "
    "catch the bug. INCONCLUSIVE = could not run on old code (import error "
    "etc.), proves nothing. BROKEN = fails on new code. Call this after "
    "writing or changing tests for a fix, before saying the fix is done."
)

mcp = MCPServer("redproof")


def _next_steps(report: Report) -> list[str]:
    if report.summary()["result"] == "PROVEN":
        return ["All changed tests catch the bug. Report them as verified."]

    if not report.results:
        return ["No new or changed tests were found, so there is nothing to verify."]

    steps = []
    for result in report.results:
        if result.verdict == FAKE:
            steps.append(
                f"{result.nodeid} is FAKE: it passes on the old buggy code. "
                "Rewrite it to check the exact value or boundary the fix "
                "changed, so it fails on the old code."
            )
        elif result.verdict == INCONCLUSIVE:
            detail = result.old_error_type or result.old_outcome
            steps.append(
                f"{result.nodeid} is INCONCLUSIVE: it could not run on the "
                f"old code ({detail}). It proves nothing about the bug; if "
                "this change is a bug fix, add a test that calls code that "
                "already existed before the fix."
            )
        elif result.verdict == BROKEN:
            steps.append(
                f"{result.nodeid} is BROKEN: it fails on the new code. Fix "
                "the code or the test before anything else."
            )
    return steps


def _run_tool(
    repo_path: str,
    base: str,
    html_path: str | None,
    history_path: str | None,
    timeout: int,
) -> dict[str, Any]:
    if timeout <= 0:
        raise ValueError("Timeout must be a positive number of seconds.")

    repo = resolve_repository(repo_path)
    report = check(repo, base=base, timeout=timeout)

    rounds = []
    if history_path:
        rounds = append_history(Path(history_path).expanduser(), report)

    payload = report.to_dict()
    payload["next_steps"] = _next_steps(report)

    if html_path:
        report_path = Path(html_path).expanduser()
        write_report_html(report, report_path, rounds)
        payload["html_report"] = str(report_path.resolve())
    return payload


@mcp.tool(description=TOOL_DESCRIPTION)
def redproof_check(
    repo_path: str,
    base: str = "main",
    html_path: str | None = None,
    history_path: str | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    """Check whether the repository's changed tests catch the bug."""
    try:
        return _run_tool(repo_path, base, html_path, history_path, timeout)
    except (ValueError, RuntimeError, OSError) as error:
        return {"error": str(error)}


def _mcp_major_version() -> int:
    return int(version("mcp").split(".", 1)[0])


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="redproof-mcp", description="Serve Redproof over the Model Context Protocol."
    )
    parser.add_argument(
        "--http",
        action="store_true",
        help="serve streamable HTTP instead of stdio",
    )
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)

    if not args.http:
        mcp.run(transport="stdio")
    elif _mcp_major_version() >= 2:
        mcp.run(
            "streamable-http",
            host="127.0.0.1",
            port=args.port,
            streamable_http_path="/mcp",
        )
    else:
        # mcp 1.x reads the bind address from settings.
        mcp.settings.host = "127.0.0.1"
        mcp.settings.port = args.port
        mcp.run(transport="streamable-http")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())