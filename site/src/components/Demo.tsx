"use client";

import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { useState } from "react";
import {
  describeOutcome,
  formatRoundTime,
  rounds,
  shortTestName,
  VERDICT_STYLES,
} from "@/lib/history";

const FINAL_TEST = [
  {
    indent: false,
    parts: [
      { text: "def ", tone: "keyword" },
      { text: "test_discount_threshold_boundary", tone: "plain" },
      { text: "() -> None:", tone: "muted" },
    ],
  },
  {
    indent: true,
    parts: [
      { text: "assert ", tone: "keyword" },
      { text: "apply_discount", tone: "plain" },
      { text: "(100) == ", tone: "muted" },
      { text: "90.0", tone: "number" },
    ],
  },
  {
    indent: true,
    parts: [
      { text: "assert ", tone: "keyword" },
      { text: "apply_discount", tone: "plain" },
      { text: "(150) == ", tone: "muted" },
      { text: "135.0", tone: "number" },
    ],
  },
  {
    indent: true,
    parts: [
      { text: "assert ", tone: "keyword" },
      { text: "apply_discount", tone: "plain" },
      { text: "(99.99) == ", tone: "muted" },
      { text: "99.99", tone: "number" },
    ],
  },
] as const;

const TONES: Record<string, string> = {
  keyword: "text-[#B4A7FF]",
  plain: "text-paper",
  muted: "text-muted",
  number: "text-unverified",
};

export function Demo() {
  const reduce = useReducedMotion();
  // Start on the first round so the page tells the story in order: fake, then proven.
  const [selected, setSelected] = useState(0);
  const round = rounds[selected];
  const proven = round.summary.result === "PROVEN";

  return (
    <section id="demo" className="border-t border-line py-20 sm:py-28">
      <div className="section-shell">
        <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-muted">
          Demo
        </p>
        <h2 className="display mt-6 max-w-[22ch] text-4xl sm:text-6xl">
          An Alan agent fixes its own fake test.
        </h2>
        <p className="mt-5 max-w-[38rem] text-[15px] leading-relaxed text-muted">
          Three real rounds from the demo shop. The demo starts with the bug
          fixed and one weak test, the way agents often leave a fix. The Alan
          agent called Redproof, saw the test rejected, and rewrote it until it
          would have failed on the buggy code.
        </p>

        <div className="mt-9 flex flex-wrap items-center gap-2">
          {rounds.map((item, index) => {
            const active = index === selected;
            const itemProven = item.summary.result === "PROVEN";
            return (
              <button
                key={item.round}
                type="button"
                onClick={() => setSelected(index)}
                aria-pressed={active}
                className={`inline-flex items-center gap-2 rounded-full border px-4 py-2 font-mono text-[11px] tracking-[0.06em] transition-colors duration-200 ${
                  active
                    ? "border-paper bg-paper text-ink"
                    : "border-line text-muted hover:border-paper/40 hover:text-paper"
                }`}
              >
                <span
                  className={`h-1.5 w-1.5 rounded-full ${
                    itemProven ? "bg-real" : "bg-fake"
                  }`}
                  aria-hidden="true"
                />
                Round {item.round}
              </button>
            );
          })}
          <span className="ml-1 font-mono text-[10px] text-muted">
            {formatRoundTime(round.time)} · live run
          </span>
        </div>

        <div className="mt-8 overflow-hidden rounded-2xl border border-line bg-panel/50">
          <div
            className={`flex flex-wrap items-end justify-between gap-6 border-b border-line px-5 py-6 sm:px-8 ${
              proven ? "bg-real/[0.06]" : "bg-fake/[0.06]"
            }`}
          >
            <div>
              <p
                className={`font-mono text-[10px] uppercase tracking-[0.18em] ${
                  proven ? "text-real" : "text-fake"
                }`}
              >
                Round {round.round} result
              </p>
              <p
                className={`display mt-2 text-4xl sm:text-5xl ${
                  proven ? "text-real" : "text-fake"
                }`}
              >
                {proven ? "PROVEN" : "FAKE TESTS FOUND"}
              </p>
            </div>
            <p className="max-w-[22rem] text-sm leading-relaxed text-muted">
              {proven
                ? "Every changed test fails on the old code and passes on the new code."
                : "At least one test passes on the old buggy code, so it cannot catch the bug."}
            </p>
          </div>

          <div className="grid grid-cols-2 border-b border-line sm:grid-cols-4">
            {[
              ["Verified", round.summary.verified],
              ["Fake", round.summary.fake],
              ["Broken", round.summary.broken],
              ["Unverified", round.summary.unverified],
            ].map(([label, value], index) => (
              <div
                key={label}
                className={`px-5 py-4 sm:px-8 ${
                  index > 0 ? "border-l border-line" : ""
                } ${index > 1 ? "border-t sm:border-t-0" : ""}`}
              >
                <p className="font-mono text-2xl">{value}</p>
                <p className="mt-1 text-[11px] uppercase tracking-[0.12em] text-muted">
                  {label}
                </p>
              </div>
            ))}
          </div>

          <AnimatePresence mode="wait" initial={false}>
            <motion.div
              key={round.round}
              initial={reduce ? false : { opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={reduce ? undefined : { opacity: 0, y: -10 }}
              transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
              className="overflow-x-auto"
            >
              <table className="w-full min-w-[760px] border-collapse text-left text-[13px]">
                <thead>
                  <tr className="border-b border-line text-[10px] uppercase tracking-[0.14em] text-muted">
                    <th className="px-5 py-3 font-normal sm:px-8">Test</th>
                    <th className="px-4 py-3 font-normal">Old code</th>
                    <th className="px-4 py-3 font-normal">New code</th>
                    <th className="px-4 py-3 font-normal">Verdict</th>
                    <th className="px-5 py-3 font-normal sm:px-8">Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {round.results.map((result) => {
                    const styles = VERDICT_STYLES[result.verdict];
                    return (
                      <tr
                        key={result.nodeid}
                        className="border-b border-line last:border-b-0"
                      >
                        <td className="max-w-[15rem] px-5 py-4 sm:px-8">
                          <p className="break-all font-mono text-[11px] text-paper">
                            {shortTestName(result.nodeid)}
                          </p>
                          <p className="mt-1 text-[10px] text-muted">
                            {result.file}
                          </p>
                        </td>
                        <td className="px-4 py-4 text-muted">
                          {describeOutcome(
                            result.old_outcome,
                            result.old_error_type,
                          )}
                        </td>
                        <td className="px-4 py-4 text-muted">
                          {describeOutcome(
                            result.new_outcome,
                            result.new_error_type,
                          )}
                        </td>
                        <td className="px-4 py-4">
                          <span
                            className={`inline-block rounded-md border px-2 py-1 font-mono text-[10px] tracking-[0.08em] ${styles.border} ${styles.soft} ${styles.text}`}
                          >
                            {result.verdict}
                          </span>
                        </td>
                        <td className="px-5 py-4 text-[12px] leading-relaxed text-muted sm:px-8">
                          {result.reason}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </motion.div>
          </AnimatePresence>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_1.1fr] lg:items-center">
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-muted">
              The test that finally proved it
            </p>
            <p className="mt-3 max-w-[30rem] text-sm leading-relaxed text-muted">
              The agent stopped asserting that a number exists and started
              asserting the exact boundary the bug changed.
            </p>
          </div>

          <div className="overflow-hidden rounded-2xl border border-line bg-panel">
            <div className="flex items-center justify-between border-b border-line px-4 py-2.5">
              <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted">
                tests/test_discount.py
              </span>
              <span className="font-mono text-[10px] text-real">
                round 3 · REAL
              </span>
            </div>
            <pre className="overflow-x-auto px-4 py-5 font-mono text-[12px] leading-7 sm:text-[12.5px]">
              <code>
                {FINAL_TEST.map((line, index) => (
                  <span key={index} className="code-line">
                    <span className="mr-5 select-none text-muted/50">
                      {index + 1}
                    </span>
                    {line.indent ? "    " : ""}
                    {line.parts.map((part, partIndex) => (
                      <span key={partIndex} className={TONES[part.tone]}>
                        {part.text}
                      </span>
                    ))}
                  </span>
                ))}
              </code>
            </pre>
          </div>
        </div>
      </div>
    </section>
  );
}