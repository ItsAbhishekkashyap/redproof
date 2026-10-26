"""Command-line interface for Redproof."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from rich.console import Console
from rich.markup import escape
from rich.table import Table

from redproof import __version__
from redproof.check import BROKEN, FAKE, INCONCLUSIVE, REAL, Report, check
from redproof.formatting import describe_outcome, short_test_name

EXIT_CODES = {
    "PROVEN": 0,
    "FAKE_TESTS_FOUND": 1,
    "BROKEN_TESTS": 1,
    "UNVERIFIED": 2,
    "NOTHING_TO_CHECK": 2,
}
VERDICT_STYLES = {REAL: "green", FAKE: "red", BROKEN: "red", INCONCLUSIVE: "yellow"}


class UsageError(Exception):
    """A problem with the command arguments or the target repository."""


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="redproof",
        description="Check whether new tests really catch the bug they fix.",
    )
    parser.add_argument(
        "--version", action="version", version=f"{parser.prog} {__version__}"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser(
        "check", help="run changed tests against the base code"
    )
    check_parser.add_argument("--repo", default=".", help="repository folder")
    check_parser.add_argument("--base", default="main", help="git ref with the old code")
    check_parser.add_argument("--timeout", type=int, default=60)
    check_parser.add_argument(
        "--json", dest="as_json", action="store_true", help="print JSON only"
    )
    check_parser.add_argument("--html", type=Path, help="write an HTML report here")
    check_parser.add_argument(
        "--history", type=Path, help="append one JSON line per run to this file"
    )
    return parser


def _resolve_repo(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_dir():
        raise UsageError(f"Repository folder does not exist: {path}")

    resolved = path.resolve()
    completed = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=resolved,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0 or completed.stdout.strip() != "true":
        raise UsageError(f"Not a git repository: {resolved}")
    return resolved


def _print_report(report: Report, console: Console) -> None:
    console.print(
        f"[bold]Redproof:[/bold] checking changed tests against {escape(report.base)}"
    )
    if not report.results:
        console.print("No new or changed tests found, nothing to verify.")
        return

    table = Table(header_style="bold")
    table.add_column("Test", overflow="fold")
    table.add_column("Old code", no_wrap=True)
    table.add_column("New code", no_wrap=True)
    table.add_column("Verdict", no_wrap=True)

    for result in report.results:
        style = VERDICT_STYLES[result.verdict]
        table.add_row(
            escape(short_test_name(result.nodeid)),
            escape(describe_outcome(result.old_outcome, result.old_error_type)),
            escape(describe_outcome(result.new_outcome, result.new_error_type)),
            f"[{style}]{result.verdict}[/{style}]",
        )
    console.print(table)

    for result in report.results:
        if result.verdict != REAL:
            console.print(
                f"[bold]{escape(short_test_name(result.nodeid))}[/bold]: "
                f"{escape(result.reason)}"
            )

    summary = report.summary()
    console.print(
        f"Verified: {summary['verified']}   Fake: {summary['fake']}   "
        f"Broken: {summary['broken']}   Unverified: {summary['unverified']}"
    )


def _load_history(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        return [json.loads(line) for line in lines if line.strip()]
    except (OSError, json.JSONDecodeError) as error:
        raise UsageError(f"Could not read history file {path}: {error}") from error


def _append_history(path: Path, report: Report) -> list[dict[str, Any]]:
    rounds = _load_history(path)
    entry = {
        "round": len(rounds) + 1,
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "summary": report.summary(),
        "results": report.to_dict()["results"],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(entry) + "\n")
    return [*rounds, entry]


def _run_check(args: argparse.Namespace) -> int:
    if args.timeout <= 0:
        raise UsageError("Timeout must be a positive number of seconds.")

    repo = _resolve_repo(args.repo)
    try:
        report = check(repo, base=args.base, timeout=args.timeout)
    except (ValueError, RuntimeError) as error:
        raise UsageError(str(error)) from error

    rounds = _append_history(args.history, report) if args.history else []

    if args.as_json:
        sys.stdout.write(json.dumps(report.to_dict(), indent=2) + "\n")
    else:
        _print_report(report, Console())

    if args.html:
        from redproof.report_html import write_report_html

        write_report_html(report, args.html, rounds)
        if not args.as_json:
            Console().print(f"HTML report written to {escape(str(args.html))}")

    return EXIT_CODES[report.summary()["result"]]


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return _run_check(args)
    except UsageError as error:
        Console(stderr=True).print(f"[red]Error:[/red] {escape(str(error))}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())