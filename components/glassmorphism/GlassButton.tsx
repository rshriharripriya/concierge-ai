"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { ReactNode, useState } from "react";

interface GlassButtonProps {
    children: ReactNode;
    onClick?: () => void;
    variant?: "primary" | "secondary" | "ghost";
    className?: string;
    disabled?: boolean;
}

export default function GlassButton({
    children,
    onClick,
    variant = "primary",
    className,
    disabled = false
}: GlassButtonProps) {
    const [ripples, setRipples] = useState<Array<{ x: number; y: number; id: number }>>([]);

    const createRipple = (e: React.MouseEvent<HTMLButtonElement>) => {
        if (disabled) return;

        const button = e.currentTarget;
        const rect = button.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const newRipple = { x, y, id: Date.now() };
        setRipples((prev) => [...prev, newRipple]);

        setTimeout(() => {
            setRipples((prev) => prev.filter((r) => r.id !== newRipple.id));
        }, 600);

        onClick?.();
    };

    const variants = {
        primary: "px-6 py-2 rounded-full bg-portfolio-gradient text-white font-medium shadow-lg hover:shadow-xl hover:opacity-90 transition-all duration-300  border-white/20border",
        secondary: "px-6 py-2 rounded-full bg-white/30 backdrop-blur-md border border-white/40 text-text-dark font-medium hover:bg-white/50 transition-all duration-300",
        ghost: "bg-transparent hover:bg-white/20 text-gray-600 hover:text-gray-900",
    };

    return (
        <motion.button
            whileHover={{ scale: disabled ? 1 : 1.05 }}
            whileTap={{ scale: disabled ? 1 : 0.98 }}
            onClick={createRipple}
            disabled={disabled}
            className={cn(
                "relative overflow-hidden backdrop-blur-[16px] rounded-full px-8 py-3 font-semibold transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed",
                variants[variant],
                className
            )}
        >
            {/* Ripple effects */}
            {ripples.map((ripple) => (
                <motion.span
                    key={ripple.id}
                    initial={{ scale: 0, opacity: 1 }}
                    animate={{ scale: 4, opacity: 0 }}
                    transition={{ duration: 0.6 }}
                    className="absolute rounded-full bg-white/30"
                    style={{
                        left: ripple.x,
                        top: ripple.y,
                        width: 20,
                        height: 20,
                        transform: "translate(-50%, -50%)",
                    }}
                />
            ))}
            {children}
        </motion.button>
    );
}
