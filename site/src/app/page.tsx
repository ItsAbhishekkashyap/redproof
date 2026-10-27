import { Demo } from "@/components/Demo";
import { Footer } from "@/components/Footer";
import { Hero } from "@/components/Hero";
import { HowItWorks } from "@/components/HowItWorks";
import { Nav } from "@/components/Nav";
import { Problem } from "@/components/Problem";
import { Results } from "@/components/Results";
import { UnderTheHood } from "@/components/UnderTheHood";
import { GetStarted } from "@/components/GetStarted";

export default function Home() {
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <Problem />
        <HowItWorks />
        <Demo />
        <GetStarted />
        <UnderTheHood />
        <Results />
      </main>
      <Footer />
    </>
  );
}