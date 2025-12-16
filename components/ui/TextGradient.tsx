"use client";

import { cn } from "@/lib/utils";

export default function TextGradient({
    text,
    className,
    from = "from-crimson-800",
    to = "to-crimson-700",
}: {
    text: string;
    className?: string;
    from?: string;
    to?: string;
}) {
    return (
        <span
            className={cn(
                "bg-clip-text text-transparent bg-gradient-to-r animate-gradient-x",
                from,
                to,
                className
            )}
        >
            {text}
        </span>
    );
}
