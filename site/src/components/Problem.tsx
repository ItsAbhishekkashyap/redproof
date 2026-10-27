import { Reveal } from "@/components/Reveal";

export function Problem() {
  return (
    <section id="problem" className="border-t border-line py-20 sm:py-28">
      <div className="section-shell">
        <Reveal>
          <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-muted">
            The problem
          </p>
          <h2 className="display mt-6 max-w-[18ch] text-4xl sm:text-6xl">
            Green tests can still miss the bug.
          </h2>
        </Reveal>

        <div className="mt-12 grid gap-10 lg:grid-cols-2 lg:gap-16">
          <Reveal delay={0.05}>
            <div className="overflow-hidden rounded-2xl border border-line bg-panel">
              <div className="flex items-center justify-between border-b border-line px-4 py-2.5">
                <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted">
                  tests/test_discount.py
                </span>
                <span className="font-mono text-[10px] text-muted">
                  python
                </span>
              </div>
              <pre className="overflow-x-auto px-4 py-5 font-mono text-[12.5px] leading-7 sm:text-[13px]">
                <code>
                  <span className="code-line">
                    <span className="mr-5 select-none text-muted/50">1</span>
                    <span className="text-[#B4A7FF]">def</span>{" "}
                    <span className="text-paper">test_discount_applied</span>
                    <span className="text-muted">():</span>
                  </span>
                  <span className="code-line">
                    <span className="mr-5 select-none text-muted/50">2</span>
                    {"    "}
                    <span className="text-[#B4A7FF]">assert</span>{" "}
                    <span className="text-paper">apply_discount</span>
                    <span className="text-muted">(</span>
                    <span className="text-paper">150</span>
                    <span className="text-muted">)</span>{" "}
                    <span className="text-[#B4A7FF]">is not</span>{" "}
                    <span className="text-paper">None</span>
                  </span>
                </code>
              </pre>
              <div className="border-t border-line px-4 py-3">
                <p className="font-mono text-[11px] text-muted">
                  <span className="text-real">CI: green.</span> Coverage: 100%
                  of the changed line.
                </p>
              </div>
            </div>
          </Reveal>

          <Reveal delay={0.1} className="flex flex-col justify-center">
            <p className="text-lg leading-relaxed text-paper sm:text-xl">
              This test passes even if the bug is still there.
            </p>
            <p className="mt-4 text-[15px] leading-relaxed text-muted">
              <span className="font-mono text-paper">150</span> is above the
              threshold, so the buggy code and the fixed code both return a
              number. The test calls the pricing function, so line coverage
              counts it as covered. It never checks the boundary the fix
              changed.
            </p>
            <p className="mt-6 text-[15px] leading-relaxed text-muted">
              Coverage measures which lines ran. It does not measure whether
              the test would notice a wrong answer.
            </p>

            <p className="display mt-9 border-l-2 border-real/60 pl-5 text-3xl leading-tight sm:text-4xl">
              The real bug is the perfect test of your test.
            </p>
          </Reveal>
        </div>
      </div>
    </section>
  );
}