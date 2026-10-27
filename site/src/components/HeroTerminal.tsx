"use client";

import { motion, useReducedMotion } from "motion/react";
import { useEffect, useState } from "react";

const COMMAND = "redproof check --base main";
const TYPE_MS = 45;

function TerminalRow({
  name,
  verdict,
}: {
  name: string;
  verdict: "REAL" | "FAKE";
}) {
  const isFake = verdict === "FAKE";
  return (
    <div className="flex items-start justify-between gap-3 py-1.5">
      <span className="min-w-0 break-all font-mono text-[11px] text-muted sm:text-xs">
        {name}
      </span>
      <motion.span
        initial={
          isFake ? { rotateY: -80, opacity: 0 } : { opacity: 0, y: 4 }
        }
        animate={{ rotateY: 0, opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
        className={
          isFake
            ? "-mt-1 shrink-0 rounded-md border border-fake/50 bg-fake/15 px-2 py-1 font-mono text-[10px] font-medium tracking-[0.08em] text-fake rotate-[-4deg]"
            : "shrink-0 font-mono text-[10px] font-medium tracking-[0.08em] text-real"
        }
      >
        {verdict}
      </motion.span>
    </div>
  );
}

export function HeroTerminal() {
  const reduce = useReducedMotion();
  const [chars, setChars] = useState(reduce ? COMMAND.length : 0);
  const [step, setStep] = useState(reduce ? 5 : 0);

  useEffect(() => {
    if (reduce) {
      setChars(COMMAND.length);
      setStep(5);
      return;
    }
    if (chars >= COMMAND.length) return;
    const timer = setTimeout(() => setChars((value) => value + 1), TYPE_MS);
    return () => clearTimeout(timer);
  }, [chars, reduce]);

  useEffect(() => {
    if (reduce || chars < COMMAND.length) return;
    const timers = [
      setTimeout(() => setStep(1), 350),
      setTimeout(() => setStep(2), 850),
      setTimeout(() => setStep(3), 1350),
      setTimeout(() => setStep(4), 1850),
      setTimeout(() => setStep(5), 2350),
      setTimeout(() => {
        setStep(0);
        setChars(0);
      }, 7200),
    ];
    return () => timers.forEach(clearTimeout);
  }, [chars, reduce]);

  return (
    <motion.div
      initial={reduce ? false : { opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55, delay: 0.15, ease: [0.22, 1, 0.36, 1] }}
      className="relative"
    >
      <div
        aria-hidden="true"
        className="absolute -inset-6 -z-10 rounded-[32px] bg-fake/5 blur-3xl"
      />
      <div className="overflow-hidden rounded-2xl border border-line bg-[#0C0C0E] shadow-[0_24px_80px_-32px_rgba(0,0,0,0.9)]">
        <div className="flex items-center gap-2 border-b border-line px-4 py-3">
          <span className="h-2.5 w-2.5 rounded-full bg-[#3A3A3F]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#3A3A3F]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#3A3A3F]" />
          <span className="ml-2 font-mono text-[10px] uppercase tracking-[0.18em] text-muted">
            redproof — zsh
          </span>
        </div>

        <div className="min-h-[292px] px-4 py-5 font-mono text-xs leading-relaxed sm:min-h-[306px] sm:px-5">
          <p className="text-paper">
            <span className="text-real">$</span> {COMMAND.slice(0, chars)}
            <span className="ml-0.5 inline-block h-3.5 w-[7px] translate-y-[2px] animate-pulse bg-muted" />
          </p>

          {step >= 1 && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-4 text-[11px] text-muted sm:text-xs"
            >
              Redproof: checking changed tests against{" "}
              <span className="text-paper">main</span>
            </motion.p>
          )}

          {step >= 2 && (
            <div className="mt-3 border-t border-line pt-2">
              <TerminalRow
                name="test_discount_at_exactly_100"
                verdict="REAL"
              />
            </div>
          )}

          {step >= 3 && (
            <div className="border-t border-line">
              <TerminalRow
                name="test_discount_returns_something"
                verdict="FAKE"
              />
            </div>
          )}

          {step >= 4 && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-4 text-[11px] text-muted sm:text-xs"
            >
              Verified: <span className="text-paper">1</span> &nbsp; Fake:{" "}
              <span className="text-fake">1</span>
            </motion.p>
          )}

          {step >= 5 && (
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 inline-flex items-center gap-2 rounded-lg border border-fake/40 bg-fake/10 px-3 py-2"
            >
              <span className="h-3 w-2 rotate-[-10deg] rounded-[2px] bg-fake" />
              <span className="font-mono text-[10px] font-medium tracking-[0.14em] text-fake">
                FAKE_TESTS_FOUND
              </span>
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
}