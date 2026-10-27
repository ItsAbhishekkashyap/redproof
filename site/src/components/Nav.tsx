import { ArrowUpRight } from "lucide-react";
import { GithubMark } from "@/components/GithubMark";

const LINKS = [
  { href: "#how-it-works", label: "How it works" },
  { href: "#demo", label: "Demo" },
  { href: "#get-started", label: "Get started" },
  { href: "#results", label: "Results" },
];

export function Nav() {
  return (
    <header className="sticky top-0 z-50 border-b border-line bg-ink/70 backdrop-blur-md">
      <div className="section-shell flex h-16 items-center justify-between gap-6">
        <a href="#top" className="flex items-center gap-2.5">
          <span aria-hidden="true" className="flex h-5 items-center gap-1">
            <span className="h-4 w-2.5 rotate-[-12deg] rounded-[3px] bg-fake" />
            <span className="-ml-1 h-4 w-2.5 rotate-[10deg] rounded-[3px] bg-real" />
          </span>
          <span className="text-[15px] font-medium tracking-[-0.01em]">
            Redproof
          </span>
        </a>

        <nav className="hidden items-center gap-7 text-sm text-muted md:flex">
          {LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="transition-colors duration-200 hover:text-paper"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <a
          href="https://github.com/ItsAbhishekkashyap/redproof"
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1.5 text-sm text-muted transition-colors duration-200 hover:text-paper"
        >
          <GithubMark className="h-4 w-4" />
          <span className="hidden sm:inline">GitHub</span>
          <ArrowUpRight className="h-3.5 w-3.5 sm:hidden" aria-hidden="true" />
        </a>
      </div>
    </header>
  );
}