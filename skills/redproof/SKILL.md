---
name: redproof
description: Use after writing or changing tests for a bug fix in a Python repository, before saying the fix is done. Verifies the tests actually catch the bug by running them against the old code.
---

1. When you have fixed a bug and written or changed tests, call the `redproof_check` MCP tool with `repo_path` = the repository folder and `base` = the branch or commit before your fix (use `"HEAD"` if your changes are not committed yet). Pass `history_path` = `"<repo>/.redproof/history.jsonl"` and `html_path` = `"<repo>/.redproof/report.html"`.

   If the tool is not available, run: `redproof check --base <base> --json --history .redproof/history.jsonl --html .redproof/report.html`

2. Read `summary.result` and `next_steps`.

3. For every FAKE test: rewrite it so it fails on the old code. Assert the exact value or boundary the fix changed.

4. Never delete, skip, or weaken a test to change the result. Never change the source code just to make a test pass.

5. Run the check again. Repeat at most 3 rounds.

6. In your final message: list REAL tests as verified, INCONCLUSIVE tests as unverified (with the reason), and give the path of the HTML report. If alan-test-feature produced a test report, add Redproof's result to it.