import React from "react";
import { cn } from "@/lib/utils";

interface ConciergeButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "ghost";
    children: React.ReactNode;
    className?: string;
}

export function ConciergeButton({
    variant = "primary",
    children,
    className,
    ...props
}: ConciergeButtonProps) {
    const baseStyles = "inline-flex items-center justify-center rounded-full px-6 py-3 text-sm font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none";

    const variants = {
        primary: "bg-concierge-gradient text-white shadow-lg hover:opacity-90 hover:-translate-y-0.5 hover:shadow-glass-hover active:scale-95",
        secondary: "bg-white/50 border border-white/60 text-gray-900 backdrop-blur-md hover:bg-white/80 hover:border-crimson-700 transition-colors",
        ghost: "bg-transparent text-gray-600 hover:text-primary-purple hover:bg-white/10",
    };

    return (
        <button
            className={cn(baseStyles, variants[variant], className)}
            {...props}
        >
            {children}
        </button>
    );
}
