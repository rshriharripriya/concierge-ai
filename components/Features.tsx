"use client";

import { motion } from "framer-motion";
import { Zap, Shield, Users } from "lucide-react";
import { GlareCard } from "@/components/ui/glare-card";

export function Features() {
    const features = [
        {
            title: "Semantic Analysis",
            description: "Advanced intent classification to route your queries effectively between AI and human experts.",
            icon: <Zap className="w-6 h-6 text-violet-500" />,
        },
        {
            title: "Expert Matching",
            description: "Automatically find and connect with the perfect human expert for complex queries.",
            icon: <Users className="w-6 h-6 text-pink-500" />,
        },
        {
            title: "Secure RAG",
            description: "Retrieval-Augmented Generation ensures accurate, context-aware, and secure AI responses.",
            icon: <Shield className="w-6 h-6 text-violet-500" />,
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
                        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-500/10 to-pink-500/10 flex items-center justify-center border border-white/50 mb-6 shadow-sm">
                            {feature.icon}
                        </div>
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
