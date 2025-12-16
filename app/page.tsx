"use client";

import { motion } from "framer-motion";
import Footer from "@/components/main/Footer";
import SystemArchitecture from "@/components/main/SystemArchitecture";
import { Features } from "@/components/main/Features";
import { Navigation } from "@/components/main/Navigation";
import { Hero } from "@/components/main/Hero";
import { TechnicalOverview } from "@/components/main/TechnicalOverview";

import Silk from "@/components/ui/Silk";

export default function Home() {
  const scrollToSection = (id: string) => {
    if (typeof window === 'undefined') return;

    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="min-h-screen relative text-gray-900 font-sans selection:bg-crimson-700/30">
      {/* Silk Animated Background */}
      <div className="fixed inset-0 -z-10 bg-[#3f060f] ">
        <Silk color="#6b0b19" speed={6} scale={1.2} noiseIntensity={1.5} rotation={1.09} />
      </div>

      {/* Radial Vignette Overlay - Full Viewport */}
      <div
        className="fixed inset-0 pointer-events-none z-0"
        style={{
          background: 'radial-gradient(ellipse at center, transparent 30%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0.4) 100%)'
        }}
      />

      {/* Navigation */}
      <Navigation onNavigate={scrollToSection} />

      <div className="relative z-10 pt-40 px-6">
        {/* Hero Section */}
        <Hero />

        {/* Gradient Transition */}
        <div className="h-40 bg-gradient-to-b from-transparent to-black/40 -mx-6" />

        <div className="bg-gradient-to-b from-black/40 via-black/50 to-black/55  -mx-6 px-6">



          {/* Feature Cards */}
          <div id="features" className="scroll-mt-24">
            <Features />
          </div>

          {/* Technical Overview Section */}
          <TechnicalOverview />




        </div>

        {/* Architecture Section */}
        <div className="py-20 -mx-6 px-6 bg-[#f5f5f5]">
          <motion.div
            id="architecture"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="scroll-mt-24"
          >
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-[#610a0a] mb-4 font-serif">System Architecture</h2>
            </div>

            <div className="flex justify-center items-center w-full">
              <SystemArchitecture />
            </div>
          </motion.div>
        </div>

      </div>

      {/* Gradient Transition to Footer
      <div className="h-32 bg-gradient-to-b from-black/55 to-black" /> */}

      <Footer />
    </div>
  );
}
