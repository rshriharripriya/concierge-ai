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
            icon: <MessageSquare className="w-6 h-6 text-violet-500" />,
        },
        {
            title: "Smart Question Routing",
            description: "Complex scenario? Our system automatically identifies when you need a human expert and connects you with the right tax professional.",
            icon: <Brain className="w-6 h-6 text-pink-500" />,
        },
        {
            title: "Conversational Memory",
            description: "Ask follow-up questions naturally. The AI remembers your conversation context for more relevant answers.",
            icon: <History className="w-6 h-6 text-blue-500" />,
        },
    ];


    return (
        <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-8 mb-32">
            {features.map((feature, index) => (
                <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 + index * 0.1, duration: 0.6 }}
                >
                    <GlareCard className="flex flex-col items-start justify-center p-8 bg-white/80 backdrop-blur-md">
                        <IconBadge className="mb-6">
                            {feature.icon}
                        </IconBadge>
                        <h3 className="text-xl font-bold text-gray-900 mb-3">{feature.title}</h3>
                        <p className="text-gray-600 leading-relaxed">
                            {feature.description}
                        </p>
                    </GlareCard>
                </motion.div>
            ))}
        </div>
    );
}
