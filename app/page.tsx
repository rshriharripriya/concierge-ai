"use client";

import { motion } from "framer-motion";
import Footer from "@/components/main/Footer";
import SystemArchitecture from "@/components/main/SystemArchitecture";
import { Features } from "@/components/main/Features";
import { Navigation } from "@/components/main/Navigation";
import { Hero } from "@/components/main/Hero";
import { TechnicalOverview } from "@/components/main/TechnicalOverview";

export default function Home() {
  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 bg-noise text-gray-900 font-sans selection:bg-pink-500/30">
      {/* Navigation */}
      <Navigation onNavigate={scrollToSection} />

      <div className="relative z-10 pt-40 pb-20 px-6">
        {/* Hero Section */}
        <Hero />

        {/* Feature Cards */}
        <div id="features" className="scroll-mt-24">
          <Features />
        </div>

        {/* Technical Overview Section */}
        <TechnicalOverview />

        {/* Architecture Section */}
        <motion.div
          id="architecture"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mb-20 scroll-mt-24"
        >
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">System Architecture</h2>
          </div>

          <div className="flex justify-center items-center w-full">
            <SystemArchitecture />
          </div>
        </motion.div>
      </div>

      <Footer />
    </div>
  );
}
