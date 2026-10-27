import { Reveal } from "@/components/Reveal";
import { VERDICT_STYLES, type Verdict } from "@/lib/history";

// Copied from eval/results.md. Re-run eval/run.py and update these if the eval changes.
const CASES: {
  name: string;
  expected: Verdict;
  redproof: Verdict;
  coverage: string;
  coverageApproves: boolean;
}[] = [
  { name: "boundary_real", expected: "REAL", redproof: "REAL", coverage: "100.0%", coverageApproves: true },
  { name: "boundary_fake", expected: "FAKE", redproof: "FAKE", coverage: "100.0%", coverageApproves: true },
  { name: "mock_fake", expected: "FAKE", redproof: "FAKE", coverage: "0.0%", coverageApproves: false },
  { name: "recompute_fake", expected: "FAKE", redproof: "FAKE", coverage: "100.0%", coverageApproves: true },
  { name: "raises_real", expected: "REAL", redproof: "REAL", coverage: "66.7%", coverageApproves: false },
  {
    name: "new_function_inconclusive",
    expected: "INCONCLUSIVE",
    redproof: "INCONCLUSIVE",
    coverage: "33.3%",
    coverageApproves: false,
  },
];

const STATS = [
  { value: "2 of 3", label: "fake tests approved by line coverage", tone: "text-fake" },
  { value: "3 of 3", label: "fake tests flagged by Redproof", tone: "text-real" },
  { value: "6 of 6", label: "cases Redproof got right", tone: "text-paper" },
  { value: "4.8 s", label: "median time per check", tone: "text-paper" },
];

function VerdictTag({ verdict }: { verdict: Verdict }) {
  const styles = VERDICT_STYLES[verdict];
  return (
    <span
      className={`inline-block rounded-md border px-2 py-1 font-mono text-[10px] tracking-[0.08em] ${styles.border} ${styles.soft} ${styles.text}`}
    >
      {verdict}
    </span>
  );
}

export function Results() {
  return (
    <section id="results" className="border-t border-line py-20 sm:py-28">
      <div className="section-shell">
        <Reveal>
          <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-muted">
            Results
          </p>
          <h2 className="display mt-6 max-w-[20ch] text-4xl sm:text-6xl">
            Coverage said fine. It wasn&apos;t.
          </h2>
          <p className="mt-5 max-w-[40rem] text-[15px] leading-relaxed text-muted">
            Six small repositories, each with a bug fix and one test. Line
            coverage counts which changed lines ran. Redproof checks whether
            the test would notice the bug.
          </p>
        </Reveal>

        <div className="mt-10 grid grid-cols-2 gap-4 lg:grid-cols-4">
          {STATS.map((stat, index) => (
            <Reveal key={stat.label} delay={index * 0.05}>
              <div className="h-full rounded-2xl border border-line bg-panel/60 p-5">
                <p className={`display text-4xl sm:text-5xl ${stat.tone}`}>
                  {stat.value}
                </p>
                <p className="mt-3 text-[13px] leading-relaxed text-muted">
                  {stat.label}
                </p>
              </div>
            </Reveal>
          ))}
        </div>

        <Reveal delay={0.1}>
          <div className="mt-5 overflow-x-auto rounded-2xl border border-line bg-panel/50">
            <table className="w-full min-w-[640px] border-collapse text-left text-[13px]">
              <thead>
                <tr className="border-b border-line text-[10px] uppercase tracking-[0.14em] text-muted">
                  <th className="px-5 py-3 font-normal sm:px-8">Case</th>
                  <th className="px-4 py-3 font-normal">Expected</th>
                  <th className="px-4 py-3 font-normal">Redproof</th>
                  <th className="px-4 py-3 font-normal">Changed-line coverage</th>
                  <th className="px-5 py-3 font-normal sm:px-8">Coverage approves?</th>
                </tr>
              </thead>
              <tbody>
                {CASES.map((item) => {
                  const coverageFooled = item.coverageApproves && item.expected === "FAKE";
                  return (
                    <tr key={item.name} className="border-b border-line last:border-b-0">
                      <td className="px-5 py-3.5 font-mono text-[11px] text-paper sm:px-8">
                        {item.name}
                      </td>
                      <td className="px-4 py-3.5">
                        <VerdictTag verdict={item.expected} />
                      </td>
                      <td className="px-4 py-3.5">
                        <VerdictTag verdict={item.redproof} />
                      </td>
                      <td className="px-4 py-3.5 font-mono text-[12px] text-muted">
                        {item.coverage}
                      </td>
                      <td
                        className={`px-5 py-3.5 text-[12px] sm:px-8 ${
                          coverageFooled ? "text-fake" : "text-muted"
                        }`}
                      >
                        {item.coverageApproves ? "yes" : "no"}
                        {coverageFooled && " (fake test approved)"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Reveal>

        <p className="mt-4 text-[12px] leading-relaxed text-muted">
          Coverage approves at 90% or more of the changed lines. The eval cases
          were written by the author, so treat them as a demonstration, not an
          independent benchmark. Reproduce with{" "}
          <code className="font-mono text-paper">python eval/run.py</code>.
        </p>
      </div>
    </section>
  );
}
