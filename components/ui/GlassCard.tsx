import React from "react";
import { cn } from "@/lib/utils";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
    children: React.ReactNode;
    className?: string;
    hoverEffect?: boolean;
}

export function GlassCard({
    children,
    className,
    hoverEffect = false,
    ...props
}: GlassCardProps) {
    return (
        <div
            className={cn(
                "glass-card rounded-3xl p-8 transition-all duration-300",
                hoverEffect && "hover:-translate-y-1 hover:shadow-glass-hover hover:border-violet-500/30",
                className
            )}
            {...props}
        >
            {children}
        </div>
    );
}
