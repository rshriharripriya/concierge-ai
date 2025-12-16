"use client";

import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface FrostedButtonProps {
    children: ReactNode;
    onClick?: () => void;
    className?: string;
    variant?: "primary" | "secondary";
}

export function FrostedButton({
    children,
    onClick,
    className = "",
    variant = "primary"
}: FrostedButtonProps) {
    const baseStyles = "relative px-8 py-4 rounded-[1.15rem] font-medium transition-all duration-300 flex items-center gap-2";

    const variantStyles = variant === "primary"
        ? "bg-white/10 backdrop-blur-md border border-white/5 text-[#F5F5F5] hover:bg-white/20 hover:border-white/30"
        : "bg-white/10 backdrop-blur-md text-[#F5F5F5] hover:bg-white/20 hover:border-white/30";

    return (
        <button
            onClick={onClick}
            className={cn(baseStyles, variantStyles, className)}
        >
            {children}
        </button>
    );
}
