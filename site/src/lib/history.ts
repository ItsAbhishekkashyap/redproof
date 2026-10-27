import historyData from "@/data/history.json";

export type Verdict = "REAL" | "FAKE" | "INCONCLUSIVE" | "BROKEN";

export type TestResult = {
  nodeid: string;
  file: string;
  old_outcome: string;
  old_error_type: string | null;
  new_outcome: string;
  new_error_type: string | null;
  verdict: Verdict;
  reason: string;
};

export type RoundSummary = {
  verified: number;
  fake: number;
  broken: number;
  unverified: number;
  result:
    | "PROVEN"
    | "FAKE_TESTS_FOUND"
    | "BROKEN_TESTS"
    | "UNVERIFIED"
    | "NOTHING_TO_CHECK";
};

export type Round = {
  round: number;
  time: string;
  summary: RoundSummary;
  results: TestResult[];
};

export const rounds = historyData as unknown as Round[];

export function describeOutcome(
  outcome: string,
  errorType: string | null,
): string {
  if (outcome === "passed") return "passes";
  if (outcome === "skipped") return "skipped";
  if (outcome === "failed") {
    return errorType ? `fails (${errorType})` : "fails";
  }
  return errorType ? `error (${errorType})` : "error";
}

export function shortTestName(nodeid: string): string {
  const [file, ...rest] = nodeid.split("::");
  const fileName = file.split("/").pop() ?? file;
  return rest.length ? `${fileName}::${rest.join("::")}` : fileName;
}

export function formatRoundTime(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "recorded run";
  const hours = String(date.getUTCHours()).padStart(2, "0");
  const minutes = String(date.getUTCMinutes()).padStart(2, "0");
  return `${hours}:${minutes} UTC`;
}

export const VERDICT_STYLES: Record<
  Verdict,
  { text: string; border: string; soft: string; dot: string }
> = {
  REAL: {
    text: "text-real",
    border: "border-real/40",
    soft: "bg-real/10",
    dot: "bg-real",
  },
  FAKE: {
    text: "text-fake",
    border: "border-fake/40",
    soft: "bg-fake/10",
    dot: "bg-fake",
  },
  INCONCLUSIVE: {
    text: "text-unverified",
    border: "border-unverified/40",
    soft: "bg-unverified/10",
    dot: "bg-unverified",
  },
  BROKEN: {
    text: "text-fake",
    border: "border-fake/70",
    soft: "bg-fake/5",
    dot: "bg-fake",
  },
};