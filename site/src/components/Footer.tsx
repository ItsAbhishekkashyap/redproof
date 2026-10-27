import { GithubMark } from "@/components/GithubMark";

export function Footer() {
  return (
    <footer className="border-t border-line py-10">
      <div className="section-shell flex flex-col gap-5 text-[13px] text-muted sm:flex-row sm:items-center sm:justify-between">
        <p>Open source. Works with any coding agent that can run a command or call an MCP tool.</p>
        <div className="flex items-center gap-6">
          <a
            href="https://github.com/ItsAbhishekkashyap/redproof"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 transition-colors hover:text-paper"
          >
            <GithubMark className="h-3.5 w-3.5" />
            GitHub
          </a>
          <span>MIT licence</span>
          <span>Abhishek Gond</span>
        </div>
      </div>
    </footer>
  );
}