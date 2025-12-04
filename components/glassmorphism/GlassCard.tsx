"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { ReactNode } from "react";

interface GlassCardProps {
    children: ReactNode;
    className?: string;
    hover?: boolean;
    delay?: number;
}

export default function GlassCard({
    children,
    className,
    hover = true,
    delay = 0
}: GlassCardProps) {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{
                duration: 0.4,
                delay: delay,
                ease: [0.68, -0.55, 0.265, 1.55],
            }}
            className={cn(
                "glass-card p-8 rounded-[24px]",
                hover && "glass-card-lift cursor-pointer",
                className
            )}
        >
            {children}
        </motion.div>
    );
}
