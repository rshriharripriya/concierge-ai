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
    sources?: {
        title: string;
        source: string;
        similarity: number;
        chapter?: string;
        source_url?: string;
    }[];
}

export function ChatBubble({ role, content, className, sources }: ChatBubbleProps) {
    const isUser = role === "user";
    const [isSourcesOpen, setIsSourcesOpen] = useState(false);

    return (
        <div
            className={cn(
                "max-w-[80%] p-5 text-sm leading-relaxed shadow-sm",
                isUser
                    ? "bg-concierge-gradient/10 border border-crimson-700/20 text-gray-800 rounded-[20px_20px_4px_20px] ml-auto"
                    : "bg-white/70 backdrop-blur-md border border-crimson-700/20 text-gray-800 rounded-[20px_20px_20px_4px] mr-auto",
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
                            strong: ({ node, ...props }) => <span className="font-bold text-crimson-800" {...props} />,
                            a: ({ node, ...props }) => <a className="text-crimson-700 hover:underline font-medium" target="_blank" rel="noopener noreferrer" {...props} />,
                        }}
                    >
                        {content}
                    </ReactMarkdown>

                    {sources && sources.length > 0 && (
                        <div className="pt-2 border-t border-crimson-700/10">
                            <button
                                onClick={() => setIsSourcesOpen(!isSourcesOpen)}
                                className="flex items-center gap-2 text-xs font-medium text-[#610a0a] hover:text-[#821e1e] transition-colors"
                            >
                                <BookOpen className="w-3 h-3 text-[#610a0a]" />
                                {isSourcesOpen ? "Hide Sources" : "Show Sources"}
                                {isSourcesOpen ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                            </button>

                            {isSourcesOpen && (
                                <div className="mt-2 space-y-2 animate-in fade-in slide-in-from-top-1 duration-200">
                                    {sources.map((source, idx) => {
                                        // Format source text with chapter if available
                                        const sourceText = source.chapter
                                            ? `${source.source} - ${source.chapter}`
                                            : source.source;

                                        const SourceWrapper = source.source_url
                                            ? ({ children }: { children: React.ReactNode }) => (
                                                <a
                                                    href={source.source_url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="block hover:bg-white/70 transition-colors rounded-lg"
                                                >
                                                    {children}
                                                </a>
                                            )
                                            : ({ children }: { children: React.ReactNode }) => <>{children}</>;

                                        return (
                                            <div key={idx} className="bg-white/50 border border-crimson-700/10 text-xs rounded-lg overflow-hidden">
                                                <SourceWrapper>
                                                    <div className="p-2">
                                                        <div className="font-medium text-gray-700 flex justify-between items-start gap-2">
                                                            <span className="flex-1">
                                                                <span className="text-[#610a0a] font-bold">[{idx + 1}]</span> <span className="text-[#610a0a]">{source.title}</span>
                                                            </span>
                                                            <span className="text-gray-400 text-[10px] whitespace-nowrap">
                                                                {Math.round(source.similarity * 100)}% match
                                                            </span>
                                                        </div>
                                                        {sourceText !== 'Internal' && (
                                                            <div className="text-gray-500 mt-0.5 text-[10px] flex items-center gap-1">
                                                                <BookOpen className="w-3 h-3 inline text-[#610a0a]" />
                                                                {sourceText}
                                                                {source.source_url && (
                                                                    <span className="text-crimson-700 ml-1">↗</span>
                                                                )}
                                                            </div>
                                                        )}
                                                    </div>
                                                </SourceWrapper>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
