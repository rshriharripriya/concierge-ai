"use client";

import { cn } from "@/lib/utils";

export default function TextGradient({
    text,
    className,
    from = "from-[#8B5CF6]",
    to = "to-[#EC4899]",
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
