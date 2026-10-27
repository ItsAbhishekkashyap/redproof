import type { LucideIcon } from "lucide-react";
import {
  ArrowRight,
  FileCode2,
  FlaskConical,
  Gavel,
  GitBranch,
  GitCompare,
  Plug,
  Scale,
  ShieldCheck,
  Terminal,
} from "lucide-react";
import { Reveal } from "@/components/Reveal";

const FLOW: { icon: LucideIcon; label: string }[] = [
  { icon: GitCompare, label: "git diff" },
  { icon: FileCode2, label: "changed tests" },
  { icon: GitBranch, label: "worktree at base" },
  { icon: FlaskConical, label: "pytest old + new" },
  { icon: Gavel, label: "verdicts" },
  { icon: Terminal, label: "CLI / JSON / HTML / MCP" },
];

const FACTS: { icon: LucideIcon; title: string; body: string }[] = [
  {
    icon: ShieldCheck,
    title: "Never touches your files",
    body: "One temporary worktree, removed in a finally block. Your working tree and git state stay as they were.",
  },
  {
    icon: Scale,
    title: "No AI in the judge",
    body: "Verdicts come from pytest results. No model, no API key, no network call inside the check.",
  },
  {
    icon: Plug,
    title: "Works with any agent",
    body: "A CLI, an MCP tool and a skill file. Alan, Claude Code, Cursor or any agent that can run a command can use it.",
  },
];

export function UnderTheHood() {
  return (
    <section className="border-t border-line py-20 sm:py-28">
      <div className="section-shell">
        <Reveal>
          <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-muted">
            Under the hood
          </p>
          <h2 className="display mt-6 max-w-[18ch] text-4xl sm:text-6xl">
            Boring on purpose.
          </h2>
        </Reveal>

        <Reveal delay={0.05}>
          <div className="mt-10 flex flex-wrap items-center gap-2 rounded-2xl border border-line bg-panel/40 p-4 sm:gap-1 sm:p-5">
            {FLOW.map((node, index) => (
              <div key={node.label} className="flex items-center gap-1">
                <div className="flex items-center gap-2 rounded-lg border border-line bg-ink/60 px-3 py-2">
                  <node.icon
                    className="h-3.5 w-3.5 shrink-0 text-muted"
                    aria-hidden="true"
                  />
                  <span className="font-mono text-[10px] text-paper sm:text-[11px]">
                    {node.label}
                  </span>
                </div>
                {index < FLOW.length - 1 && (
                  <ArrowRight
                    className="mx-1 hidden h-3.5 w-3.5 shrink-0 text-muted/60 sm:block"
                    aria-hidden="true"
                  />
                )}
              </div>
            ))}
          </div>
        </Reveal>

        <div className="mt-5 grid gap-4 md:grid-cols-3">
          {FACTS.map((fact, index) => (
            <Reveal key={fact.title} delay={index * 0.05}>
              <div className="rounded-2xl border border-line bg-panel/60 p-5">
                <fact.icon
                  className="h-4 w-4 text-muted"
                  aria-hidden="true"
                />
                <h3 className="mt-4 text-sm font-medium">{fact.title}</h3>
                <p className="mt-2 text-[13px] leading-relaxed text-muted">
                  {fact.body}
                </p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}