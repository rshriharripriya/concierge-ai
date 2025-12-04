
"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowRight, User } from "lucide-react";
import { GlassSurface } from "@/components/ui/GlassSurface";
import { HoverBorderGradient } from "@/components/ui/hover-border-gradient";
import { AuroraText } from "@/components/ui/aurora-text";
import Footer from "@/components/Footer";
import SystemArchitecture from "@/components/SystemArchitecture";
import { Features } from "@/components/Features";

export default function Home() {
  const router = useRouter();

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 bg-noise text-gray-900 font-sans selection:bg-pink-500/30">
      {/* Navigation */}
      <nav className="fixed top-6 left-0 right-0 z-50 flex justify-center items-center px-6">
        <GlassSurface className="px-8 py-3 flex items-center gap-8">
          {/* <span className="font-bold text-lg tracking-tight bg-clip-text text-transparent bg-concierge-gradient">Concierge AI</span> */}
          <div className="hidden md:flex items-center gap-6 text-sm font-medium text-gray-600">
            <button onClick={() => scrollToSection('overview')} className="hover:text-violet-500 transition-colors">Overview</button>
            <button onClick={() => scrollToSection('features')} className="hover:text-violet-500 transition-colors">Features</button>
            <button onClick={() => scrollToSection('architecture')} className="hover:text-violet-500 transition-colors">Architecture</button>
          </div>
        </GlassSurface>

        <div className="absolute right-6">
          <HoverBorderGradient
            containerClassName="rounded-full"
            as="button"
            className="dark:bg-black bg-white text-black dark:text-white flex items-center space-x-2"
            onClick={() => router.push('/chat')}
          >
            <span>Try Concierge</span>
          </HoverBorderGradient>
        </div>
      </nav>

      <div className="relative z-10 pt-40 pb-20 px-6">
        {/* Hero Section */}
        <div id="overview" className="max-w-4xl mx-auto text-center mb-32 scroll-mt-32">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            {/* <div className="inline-block mb-6 px-4 py-1.5 rounded-full bg-white/60 backdrop-blur-md border border-white/60 text-sm font-medium text-violet-600 shadow-sm">
              ✨ Intelligent Expert Routing

            </div> */}

            <h1 className="text-6xl md:text-7xl font-bold mb-8 tracking-tight text-gray-900 leading-tight">
              Concierge <AuroraText>AI</AuroraText>
            </h1>

            <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto leading-relaxed">
              An intelligent routing system that seamlessly connects your tax queries to the perfect human expert or AI assistant, ensuring faster and more accurate resolutions.
            </p>

            <div className="flex justify-center gap-4">
              <HoverBorderGradient
                containerClassName="rounded-full"
                as="button"
                className="dark:bg-black bg-white text-black dark:text-white flex items-center space-x-2 px-8 py-4 text-lg"
                onClick={() => router.push('/chat')}
              >
                <span>Start Chatting</span>
                <ArrowRight className="w-5 h-5 ml-2" />
              </HoverBorderGradient>
            </div>
          </motion.div>
        </div>

        {/* Feature Cards */}
        <div id="features" className="scroll-mt-24">
          <Features />
        </div>

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
            <p className="text-gray-600">Powered by advanced semantic analysis and RAG</p>
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


