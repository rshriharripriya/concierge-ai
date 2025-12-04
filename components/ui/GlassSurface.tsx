import React from "react";
import { cn } from "@/lib/utils";

interface GlassSurfaceProps extends React.HTMLAttributes<HTMLDivElement> {
    children: React.ReactNode;
    className?: string;
}

export function GlassSurface({
    children,
    className,
    ...props
}: GlassSurfaceProps) {
    return (
        <div
            className={cn(
                "relative overflow-hidden rounded-full border border-white/20 bg-white/30 p-1 backdrop-blur-xl transition-all duration-300 hover:bg-white/40 hover:border-white/30 hover:shadow-lg hover:shadow-violet-500/10",
                className
            )}
            {...props}
        >
            <div className="absolute inset-0 -z-10 bg-gradient-to-br from-violet-500/5 to-pink-500/5 opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
            {children}
        </div>
    );
}
