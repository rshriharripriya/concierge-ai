import React from "react";
import { cn } from "@/lib/utils";

interface ChatBubbleProps {
    role: "user" | "assistant" | "expert";
    content: string;
    className?: string;
}

export function ChatBubble({ role, content, className }: ChatBubbleProps) {
    const isUser = role === "user";

    return (
        <div
            className={cn(
                "max-w-[80%] p-5 text-sm leading-relaxed shadow-sm",
                isUser
                    ? "bg-concierge-gradient/10 border border-pink-500/20 text-gray-800 rounded-[20px_20px_4px_20px] ml-auto"
                    : "bg-white/70 backdrop-blur-md border border-violet-500/20 text-gray-800 rounded-[20px_20px_20px_4px] mr-auto",
                className
            )}
        >
            {content}
        </div>
    );
}
