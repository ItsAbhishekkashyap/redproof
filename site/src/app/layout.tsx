import type { Metadata } from "next";
import { Geist, Geist_Mono, Instrument_Serif } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
});

const instrumentSerif = Instrument_Serif({
  variable: "--font-instrument-serif",
  subsets: ["latin"],
  weight: "400",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Redproof — A referee for AI-written tests",
  description:
    "Your AI agent fixed the bug and the tests are green. Redproof puts the old buggy code back and checks the tests would actually have caught it.",
  openGraph: {
    title: "Redproof — A referee for AI-written tests",
    description:
      "Put the old buggy code back and check that the agent's new tests would actually have caught the bug.",
    type: "website",
    siteName: "Redproof",
  },
  twitter: {
    card: "summary",
    title: "Redproof — A referee for AI-written tests",
    description:
      "Put the old buggy code back and check that the agent's new tests would actually have caught the bug.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${instrumentSerif.variable} bg-ink font-sans text-paper antialiased`}
      >
        <div className="site-backdrop" aria-hidden="true" />
        {children}
      </body>
    </html>
  );
}