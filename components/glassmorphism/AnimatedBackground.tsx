"use client";

import { motion } from "framer-motion";

export default function AnimatedBackground() {
    return (
        <div className="fixed inset-0 -z-10 overflow-hidden bg-white">
            {/* Noise Texture */}
            <div className="absolute inset-0 bg-noise opacity-[0.03] pointer-events-none z-50" />

            {/* Gradient Orbs */}
            <div className="absolute top-[-10%] left-[-10%] w-[50vw] h-[50vw] rounded-full bg-gradient-to-r from-blue-400/30 to-purple-500/30 blur-[100px] animate-blob" />
            <div className="absolute top-[20%] right-[-10%] w-[40vw] h-[40vw] rounded-full bg-gradient-to-r from-pink-400/30 to-rose-500/30 blur-[100px] animate-blob animation-delay-2000" />
            <div className="absolute bottom-[-10%] left-[20%] w-[60vw] h-[60vw] rounded-full bg-gradient-to-r from-violet-400/30 to-indigo-500/30 blur-[100px] animate-blob animation-delay-4000" />

            {/* Floating Elements */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 1 }}
                className="absolute inset-0"
            >
                <div className="absolute top-1/4 left-1/4 w-4 h-4 bg-blue-400 rounded-full blur-sm animate-float opacity-60" />
                <div className="absolute top-3/4 right-1/4 w-6 h-6 bg-purple-400 rounded-full blur-md animate-float animation-delay-1000 opacity-50" />
                <div className="absolute bottom-1/4 left-1/2 w-3 h-3 bg-pink-400 rounded-full blur-sm animate-float animation-delay-3000 opacity-70" />
            </motion.div>
        </div>
    );
}
