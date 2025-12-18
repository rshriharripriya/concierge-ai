"use client";

import { motion } from "framer-motion";
import { MessageSquare, Brain, History } from "lucide-react";
import { GlareCard } from "@/components/ui/glare-card";
import { IconBadge } from "@/components/sub/IconBadge";

export function Features() {
    const features = [
        {
            title: "Instant AI Answers",
            description: "Get immediate responses to common tax questions with accurate, cited information from IRS publications and tax resources.",
            icon: <MessageSquare className="w-6 h-6 text-[#F5F5F5]" />,
        },
        {
            title: "Smart Question Routing",
            description: "Complex scenario? Our system automatically identifies when you need a human expert and connects you with the right tax professional.",
            icon: <Brain className="w-6 h-6 text-[#F5F5F5]" />,
        },
        {
            title: "Conversational Memory",
            description: "Ask follow-up questions naturally. The AI remembers your conversation context for more relevant answers.",
            icon: <History className="w-6 h-6 text-[#F5F5F5]" />,
        },
    ];


    return (
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-32 place-items-center md:place-items-stretch">
                {features.map((feature, index) => (
                    <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 + index * 0.1, duration: 0.6 }}
                        className="w-full max-w-sm md:max-w-none"
                    >
                        <GlareCard className="flex flex-col items-start justify-center p-8 bg-black/60 backdrop-blur-md border border-white/10 w-full h-full">
                            <div className="mb-6">
                                {feature.icon}
                            </div>
                            <h3 className="text-xl font-bold text-[#F5F5F5] mb-3 font-serif">{feature.title}</h3>
                            <p className="text-[#F5F5F5]/80 leading-relaxed font-serif">
                                {feature.description}
                            </p>
                        </GlareCard>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
