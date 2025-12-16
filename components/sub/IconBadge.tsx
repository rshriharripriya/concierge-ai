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
    colorFrom = "crimson-800",
    colorTo = "crimson-700",
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

    // Use lighter variant background for dark feature cards
    const lightBg = "bg-white/5 border-white/20";

    return (
        <div
            className={`${sizeClasses[size]} rounded-2xl flex items-center justify-center ${baseClasses} ${variant === "light" ? lightBg : ""} ${className}`}
        >
            {children}
        </div>
    );
}
