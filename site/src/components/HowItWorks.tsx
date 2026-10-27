import type { LucideIcon } from "lucide-react";
import { FileCode2, FlaskConical, Gavel, GitBranch } from "lucide-react";
import { Reveal } from "@/components/Reveal";
import {
  VERDICT_STYLES,
  type Verdict,
} from "@/lib/history";

const STEPS: { icon: LucideIcon; title: string; body: string }[] = [
  {
    icon: GitBranch,
    title: "Put the old code back",
    body: "Redproof creates a temporary git worktree at the base commit, without touching your files or your working tree.",
  },
  {
    icon: FlaskConical,
    title: "Run the new tests twice",
    body: "The changed tests run against the old code and against the new code. A small pytest plugin records every outcome and exception type.",
  },
  {
    icon: Gavel,
    title: "Give a verdict",
    body: "Each test gets one of four verdicts. The check is a short set of rules over real test results, not a model's opinion.",
  },
];

const VERDICTS: {
  verdict: Verdict;
  meaning: string;
  tilt: string;
  outline?: boolean;
}[] = [
  {
    verdict: "REAL",
    meaning: "Fails on the old code with an assertion, passes on the new code.",
    tilt: "-3deg",
  },
  {
    verdict: "FAKE",
    meaning: "Passes on both. It cannot catch this bug.",
    tilt: "2.5deg",
  },
  {
    verdict: "INCONCLUSIVE",
    meaning: "Could not run on the old code, for example an import error. Proves nothing.",
    tilt: "-2deg",
  },
  {
    verdict: "BROKEN",
    meaning: "Does not pass on the new code.",
    tilt: "3deg",
    outline: true,
  },
];

export function HowItWorks() {
  return (
    <section
      id="how-it-works"
      className="border-t border-line py-20 sm:py-28"
    >
      <div className="section-shell">
        <Reveal>
          <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-muted">
            How it works
          </p>
          <h2 className="display mt-6 max-w-[20ch] text-4xl sm:text-6xl">
            Three steps, one honest answer.
          </h2>
        </Reveal>

        <div className="mt-12 grid gap-8 sm:grid-cols-3">
          {STEPS.map((step, index) => (
            <Reveal key={step.title} delay={index * 0.06}>
              <div className="flex h-full flex-col rounded-2xl border border-line bg-panel/60 p-6">
                <div className="flex items-center justify-between">
                  <step.icon
                    className="h-5 w-5 text-muted"
                    aria-hidden="true"
                  />
                  <span className="font-mono text-[11px] text-muted">
                    0{index + 1}
                  </span>
                </div>
                <h3 className="mt-8 text-base font-medium">{step.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-muted">
                  {step.body}
                </p>
              </div>
            </Reveal>
          ))}
        </div>

        <div className="mt-16">
          <Reveal>
            <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-muted">
              The four verdicts
            </p>
          </Reveal>

          <div className="mt-6 grid grid-cols-2 gap-3 sm:gap-5 lg:grid-cols-4">
            {VERDICTS.map((item, index) => {
              const styles = VERDICT_STYLES[item.verdict];
              return (
                <Reveal key={item.verdict} delay={index * 0.05}>
                  <div
                    className={`flex min-h-[220px] flex-col rounded-2xl border p-5 transition-transform duration-300 hover:rotate-0 sm:min-h-[250px] ${styles.border} ${
                      item.outline ? "bg-transparent" : "bg-panel/70"
                    }`}
                    style={{ transform: `rotate(${item.tilt})` }}
                  >
                    <span
                      className={`h-1.5 w-10 rounded-full ${styles.dot}`}
                      aria-hidden="true"
                    />
                    <span
                      className={`mt-7 font-mono text-[10px] font-medium tracking-[0.16em] ${styles.text}`}
                    >
                      {item.verdict}
                    </span>
                    <span className="mt-auto pt-6 text-[13px] leading-relaxed text-muted">
                      {item.meaning}
                    </span>
                  </div>
                </Reveal>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}