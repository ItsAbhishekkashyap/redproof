import { ArrowDown, ArrowUpRight } from "lucide-react";
import { HeroTerminal } from "@/components/HeroTerminal";
import { Reveal } from "@/components/Reveal";

export function Hero() {
  return (
    <section id="top" className="relative pb-20 pt-14 sm:pb-28 sm:pt-20">
      <div className="section-shell grid items-center gap-14 lg:grid-cols-[1.05fr_0.95fr] lg:gap-10">
        <Reveal>
          <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-muted">
            git worktree + pytest &nbsp;/&nbsp; no AI in the judge
          </p>

          <h1 className="display mt-7 text-[clamp(3.1rem,8.4vw,6.3rem)]">
            A referee for
            <br />
            <em className="italic">AI-written</em> tests.
          </h1>

          <p className="mt-7 max-w-[34rem] text-[15px] leading-relaxed text-muted sm:text-base">
            Your AI agent fixed the bug and the tests are green. Redproof puts
            the old buggy code back and checks the tests would actually have
            caught it.
          </p>

          <div className="mt-9 flex flex-wrap items-center gap-3">
            <a
              href="https://github.com/ItsAbhishekkashyap/redproof"
              target="_blank"
              rel="noreferrer"
              className="group inline-flex items-center gap-2 rounded-full bg-paper px-5 py-3 text-sm font-medium text-ink transition-transform duration-200 hover:-translate-y-0.5"
            >
              View on GitHub
              <ArrowUpRight
                className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5"
                aria-hidden="true"
              />
            </a>
            <a
              href="#demo"
              className="inline-flex items-center gap-2 rounded-full border border-line px-5 py-3 text-sm text-paper transition-colors duration-200 hover:border-paper/40"
            >
              See the demo
              <ArrowDown className="h-4 w-4" aria-hidden="true" />
            </a>
          </div>
        </Reveal>

        <HeroTerminal />
      </div>
    </section>
  );
}