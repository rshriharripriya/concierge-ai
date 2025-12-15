"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { HoverBorderGradient } from "@/components/ui/hover-border-gradient";
import { AuroraText } from "@/components/ui/aurora-text";

export function Hero() {
    const router = useRouter();

    return (
        <div id="overview" className="max-w-4xl mx-auto text-center mb-32 scroll-mt-32">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
            >
                <h1 className="text-6xl md:text-7xl font-bold mb-8 tracking-tight text-gray-900 leading-tight">
                    Concierge <AuroraText>AI</AuroraText>
                </h1>

                <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto leading-relaxed">
                    Smart tax help that knows when you need AI speed and when you need human expertise.
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
    );
}
