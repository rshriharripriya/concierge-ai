import { ReactNode } from "react";

interface IconBadgeProps {
    children: ReactNode;
    variant?: "light" | "solid";
    size?: "sm" | "md" | "lg";
    colorFrom?: string;
    colorTo?: string;
    className?: string;
}

export function IconBadge({
    children,
    variant = "light",
    size = "md",
    colorFrom = "violet-500",
    colorTo = "pink-500",
    className = "",
}: IconBadgeProps) {
    const sizeClasses = {
        sm: "w-10 h-10",
        md: "w-14 h-14",
        lg: "w-16 h-16",
    };

    // Get the base classes without dynamic colors
    const baseClasses = variant === "light"
        ? "border border-white/50 shadow-sm"
        : "text-white font-bold shadow-lg";

    // Use default light variant background for Features
    const lightBg = "bg-gradient-to-br from-violet-500/10 to-pink-500/10";

    return (
        <div
            className={`${sizeClasses[size]} rounded-2xl flex items-center justify-center ${baseClasses} ${variant === "light" ? lightBg : ""} ${className}`}
        >
            {children}
        </div>
    );
}
