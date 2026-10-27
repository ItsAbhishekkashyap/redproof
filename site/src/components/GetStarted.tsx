import { ArrowUpRight } from "lucide-react";
import { CopyButton } from "@/components/CopyButton";
import { Reveal } from "@/components/Reveal";

const INSTALL = "pip install git+https://github.com/ItsAbhishekkashyap/redproof";
const MCP = "redproof-mcp";
const SKILL =
  "https://github.com/ItsAbhishekkashyap/redproof/tree/main/skills/redproof";

const CARDS = [
  {
    label: "CLI",
    title: "Install the command",
    value: INSTALL,
    note: "Then run redproof check --base main inside your repo.",
  },
  {
    label: "MCP",
    title: "Add the MCP server",
    value: MCP,
    note: "Add it as a command (stdio) MCP server in any MCP client: Alan, Claude Code, Cursor and others. Fallback: python -m redproof.mcp_server.",
  },
  {
    label: "Skill",
    title: "Import the skill",
    value: SKILL,
    note: "A SKILL.md that tells the agent when to call Redproof. Import it in any agent that supports skills, using this folder link.",
  },
];

export function GetStarted() {
  return (
    <section id="get-started" className="border-t border-line py-20 sm:py-28">
      <div className="section-shell">
        <Reveal>
          <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-muted">
            Use with any agent
          </p>
          <h2 className="display mt-6 max-w-[20ch] text-4xl sm:text-6xl">
            Give the agent a way to check itself.
          </h2>
        </Reveal>

        <div className="mt-12 grid gap-4 md:grid-cols-3">
          {CARDS.map((card, index) => (
            <Reveal key={card.label} delay={index * 0.06}>
              <div className="flex h-full flex-col rounded-2xl border border-line bg-panel/60 p-5">
                <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-muted">
                  {card.label}
                </p>
                <h3 className="mt-3 text-base font-medium">{card.title}</h3>

                <div className="mt-5 flex items-start justify-between gap-3 rounded-lg border border-line bg-ink/50 p-3">
                  <code className="break-all font-mono text-[11px] leading-relaxed text-paper">
                    {card.value}
                  </code>
                  <CopyButton value={card.value} />
                </div>

                <p className="mt-4 text-[13px] leading-relaxed text-muted">
                  {card.note}
                </p>
              </div>
            </Reveal>
          ))}
        </div>

        <Reveal delay={0.08}>
          <figure className="mt-16 border-l-2 border-unverified/60 pl-6 sm:pl-8">
            <blockquote className="display text-3xl leading-[1.08] sm:text-5xl">
              “A report that says what is unverified is more useful than one
              that claims a clean pass.”
            </blockquote>
            <figcaption className="mt-5 text-sm text-muted">
              Alan Testing evidence docs ·{" "}
              <a
                href="https://docs.tryalan.ai/docs/reviews-testing-deploys/testing-evidence"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-paper underline decoration-line underline-offset-4 transition-colors hover:decoration-paper"
              >
                read the docs
                <ArrowUpRight className="h-3.5 w-3.5" aria-hidden="true" />
              </a>
            </figcaption>
          </figure>
        </Reveal>
      </div>
    </section>
  );
}