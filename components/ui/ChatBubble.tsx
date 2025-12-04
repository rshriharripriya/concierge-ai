import React from "react";
import { cn } from "@/lib/utils";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

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
            {isUser ? (
                content
            ) : (
                <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                        ul: ({ node, ...props }) => <ul className="list-disc pl-4 mb-2 space-y-1" {...props} />,
                        ol: ({ node, ...props }) => <ol className="list-decimal pl-4 mb-2 space-y-1" {...props} />,
                        li: ({ node, ...props }) => <li className="mb-1" {...props} />,
                        p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
                        strong: ({ node, ...props }) => <span className="font-bold text-violet-700" {...props} />,
                        a: ({ node, ...props }) => <a className="text-pink-600 hover:underline font-medium" target="_blank" rel="noopener noreferrer" {...props} />,
                    }}
                >
                    {content}
                </ReactMarkdown>
            )}
        </div>
    );
}
