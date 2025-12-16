
"use client";

import { motion } from "framer-motion";

export function ThinkingLoader() {
    const circumference = 2 * Math.PI * 22; // 2πr where r=22

    return (
        <div className="flex items-center gap-3">
            {/* Loader Circle with Bow Tie */}
            <div className="relative w-12 h-12">
                {/* Background Circle */}
                <div className="absolute inset-0 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                    {/* Bow Tie Icon */}
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        {/* Left triangle */}
                        <path d="M 4 12 L 9 8 L 9 16 Z" fill="#610a0a" />
                        {/* Right triangle */}
                        <path d="M 20 12 L 15 8 L 15 16 Z" fill="#610a0a" />
                        {/* Center circle */}
                        <circle cx="12" cy="12" r="2" fill="#610a0a" />
                    </svg>
                </div>

                {/* Animated Gradient Ring */}
                <svg className="absolute inset-0 -rotate-90" width="48" height="48">
                    <defs>
                        <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#610a0a" />
                            <stop offset="50%" stopColor="#821e1e" />
                            <stop offset="100%" stopColor="#610a0a" />
                        </linearGradient>
                    </defs>

                    {/* Background circle (full ring outline) */}
                    <circle
                        cx="24"
                        cy="24"
                        r="22"
                        stroke="rgba(209, 213, 219, 0.3)"
                        strokeWidth="3"
                        fill="none"
                    />

                    {/* Animated progress ring */}
                    <motion.circle
                        cx="24"
                        cy="24"
                        r="22"
                        stroke="url(#progressGradient)"
                        strokeWidth="3"
                        fill="none"
                        strokeLinecap="round"
                        strokeDasharray={circumference}
                        animate={{
                            strokeDashoffset: [circumference, 0, circumference],
                        }}
                        transition={{
                            duration: 2,
                            repeat: Infinity,
                            ease: "easeInOut",
                        }}
                    />
                </svg>
            </div>

            {/* Text */}
            <p className="text-gray-600 font-medium">
                <motion.span
                    animate={{ opacity: [1, 0.5, 1] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                >
                    Thinking
                </motion.span>
            </p>
        </div>
    );
}

