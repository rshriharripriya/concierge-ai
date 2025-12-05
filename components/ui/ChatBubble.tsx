import React from "react";
import { cn } from "@/lib/utils";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { useState } from "react";
import { ChevronDown, ChevronUp, BookOpen } from "lucide-react";

interface ChatBubbleProps {
    role: "user" | "assistant" | "expert";
    content: string;
    className?: string;
    sources?: { title: string; source: string; similarity: number }[];
}

export function ChatBubble({ role, content, className, sources }: ChatBubbleProps) {
    const isUser = role === "user";
    const [isSourcesOpen, setIsSourcesOpen] = useState(false);

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
                <div className="space-y-3">
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

                    {sources && sources.length > 0 && (
                        <div className="pt-2 border-t border-violet-100">
                            <button
                                onClick={() => setIsSourcesOpen(!isSourcesOpen)}
                                className="flex items-center gap-2 text-xs font-medium text-violet-600 hover:text-violet-800 transition-colors"
                            >
                                <BookOpen className="w-3 h-3" />
                                {isSourcesOpen ? "Hide Sources" : "Show Sources"}
                                {isSourcesOpen ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                            </button>

                            {isSourcesOpen && (
                                <div className="mt-2 space-y-2 animate-in fade-in slide-in-from-top-1 duration-200">
                                    {sources.map((source, idx) => (
                                        <div key={idx} className="bg-white/50 p-2 rounded-lg border border-violet-50 text-xs">
                                            <div className="font-medium text-gray-700 flex justify-between">
                                                <span>[{idx + 1}] {source.title}</span>
                                                <span className="text-gray-400 text-[10px]">{Math.round(source.similarity * 100)}% match</span>
                                            </div>
                                            {source.source !== 'Internal' && (
                                                <div className="text-gray-500 mt-0.5 text-[10px]">{source.source}</div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
