import { Demo } from "@/components/Demo";
import { Footer } from "@/components/Footer";
import { Hero } from "@/components/Hero";
import { HowItWorks } from "@/components/HowItWorks";
import { Nav } from "@/components/Nav";
import { Problem } from "@/components/Problem";
import { UnderTheHood } from "@/components/UnderTheHood";
import { UseWithAlan } from "@/components/UseWithAlan";

export default function Home() {
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <Problem />
        <HowItWorks />
        <Demo />
        <UseWithAlan />
        <UnderTheHood />
      </main>
      <Footer />
    </>
  );
}