"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { FrostedButton } from "@/components/ui/FrostedButton";

export function Hero() {
    const router = useRouter();

    return (
        <div id="overview" className="max-w-4xl mx-auto text-center h-[calc(80vh-5rem)] scroll-mt-32 flex justify-center items-center">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
            >
                <h1 className="text-6xl md:text-7xl font-bold mb-8 tracking-tight text-[#F5F5F5] leading-tight font-serif">
                    Concierge AI
                </h1>

                <p className="text-xl mb-12 max-w-2xl mx-auto leading-relaxed text-[#F5F5F5] font-serif">
                    Smart tax help that knows when you need AI speed and when you need human expertise.
                </p>

                <div className="flex justify-center gap-4 font-serif">
                    <FrostedButton onClick={() => router.push('/chat')}>
                        <span>Start Chatting</span>
                        <ArrowRight className="w-5 h-5" />
                    </FrostedButton>
                </div>
            </motion.div>
        </div>
    );
}
