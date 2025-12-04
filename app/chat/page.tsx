"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, ArrowLeft } from "lucide-react";
import { useRouter } from "next/navigation";
import { GlassCard } from "@/components/ui/GlassCard";
import { ConciergeButton } from "@/components/ui/ConciergeButton";
import { ChatBubble } from "@/components/ui/ChatBubble";
import { GlassSurface } from "@/components/ui/GlassSurface";
import { PlaceholdersAndVanishInput } from "@/components/ui/placeholders-and-vanish-input";

import { sendQuery } from "@/lib/api";

interface Message {
    id: string;
    role: "user" | "assistant" | "expert";
    content: string;
    metadata?: any;
}

export default function ChatPage() {
    const router = useRouter();
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [analyzing, setAnalyzing] = useState(false);
    const [conversationId, setConversationId] = useState<string | null>(null);
    const [matchedExpert, setMatchedExpert] = useState<any>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, analyzing]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: "user",
            content: input,
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);
        setAnalyzing(true);

        try {
            await new Promise(resolve => setTimeout(resolve, 1500));

            const data = await sendQuery(input, "demo_user", conversationId || undefined);
            setConversationId(data.conversation_id);
            setAnalyzing(false);

            if (data.expert) {
                setMatchedExpert(data.expert);
            }

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: data.route_decision === "human" ? "expert" : "assistant",
                content: data.response,
                metadata: {
                    intent: data.intent,
                    complexity: data.complexity_score,
                    confidence: data.confidence,
                    expert: data.expert,
                    sources: data.sources,
                    reasoning: data.reasoning,
                },
            };

            setMessages((prev) => [...prev, assistantMessage]);
        } catch (error: any) {
            console.error("Error:", error);
            setAnalyzing(false);
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: `Sorry, I encountered an error: ${error.message}. Please try again.`,
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen relative flex flex-col font-sans text-gray-900 bg-gray-50 bg-noise selection:bg-pink-500/30">

            {/* Navbar */}
            <nav className="fixed top-0 left-0 right-0 z-[100] flex justify-between items-center px-6 py-4 bg-gray-50/80 backdrop-blur-md ">
                <button
                    onClick={() => router.push('/')}
                    className="glass-card p-2 rounded-full hover:bg-white/50 transition-colors"
                >
                    <ArrowLeft className="w-5 h-5 text-gray-700" />
                </button>
                <GlassSurface className="px-6 py-2">
                    <span className="font-bold text-lg bg-clip-text text-gray-600 bg-gray-50/80 backdrop-blur-md">
                        Concierge AI
                    </span>
                </GlassSurface>
                <div className="w-10" />
            </nav>

            {/* Main Content Area */}
            <div className="flex-1 flex items-center justify-center p-6 pt-24 pb-10">
                {/* FIX: 
                   1. max-w-6xl: Sets a constant "Big but not too big" width.
                   2. w-full: Forces the container to fill that width even when empty.
                   3. mx-auto: Centers it perfectly.
                */}
                <div className="w-full max-w-6xl mx-auto flex h-[calc(100vh-140px)] gap-6">

                    {/* Chat Container */}
                    {/* FIX: 
                        1. w-full: Forces the card to stretch to the full width of the parent (6xl).
                        2. shrink-0: Prevents it from crushing when expert panel opens (if flex behavior tries to squish it).
                    */}
                    <GlassCard className="flex-1 w-full rounded-[32px] flex flex-col overflow-hidden relative h-full p-0 !border-white/60 min-w-0 transition-all duration-500 ease-in-out shadow-xl shrink-0">
                        <div className="flex-1 overflow-y-auto p-8 space-y-6 scrollbar-thin scrollbar-thumb-violet-200 w-full relative">

                            {/* Greeting Overlay */}
                            {messages.length === 0 && (
                                <div className="absolute inset-0 flex flex-col items-center justify-center text-center z-10 p-8">
                                    <p className="text-xl font-medium mb-8 text-gray-500">How can I help you today?</p>
                                    <div className="flex flex-wrap justify-center gap-3 max-w-md">
                                        {["What is the standard deduction for 2024?", "How do I file for an extension?", "Can I deduct my home office expenses?"].map((q, i) => (
                                            <button
                                                key={i}
                                                onClick={() => {
                                                    setInput(q);
                                                    setTimeout(() => handleSend(), 100);
                                                }}
                                                className="px-4 py-2 rounded-full bg-white/40 hover:bg-white/70 border border-white/20 text-sm text-gray-600 transition-all cursor-pointer shadow-sm hover:shadow-md hover:text-violet-600"
                                            >
                                                {q}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Messages List */}
                            <AnimatePresence mode="popLayout">
                                {messages.map((message) => (
                                    <motion.div
                                        key={message.id}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className={`flex ${message.role === "user" ? "justify-end" : "justify-start"} relative z-20`}
                                    >
                                        <div className="max-w-[85%]">
                                            <ChatBubble role={message.role} content={message.content} />

                                            {/* Routing Details (Debug Info) */}
                                            {message.role !== "user" && message.metadata && (
                                                <motion.div
                                                    initial={{ opacity: 0, height: 0 }}
                                                    animate={{ opacity: 1, height: "auto" }}
                                                    className="mt-2 mx-1 p-3 bg-white/40 backdrop-blur-sm rounded-2xl border border-white/20 text-[11px] text-gray-500 space-y-1.5 shadow-sm"
                                                >
                                                    <div className="flex items-center gap-3 flex-wrap">
                                                        <div className="flex items-center gap-1.5">
                                                            <span className="w-1.5 h-1.5 rounded-full bg-violet-400"></span>
                                                            <span className="font-medium text-gray-600">Intent:</span>
                                                            <span className="bg-violet-50/50 text-violet-700 px-1.5 py-0.5 rounded text-[10px] border border-violet-100 uppercase tracking-wider font-medium">{message.metadata.intent}</span>
                                                        </div>
                                                        <div className="flex items-center gap-1.5">
                                                            <span className="w-1.5 h-1.5 rounded-full bg-pink-400"></span>
                                                            <span className="font-medium text-gray-600">Confidence:</span>
                                                            <span>{message.metadata.confidence}</span>
                                                        </div>
                                                    </div>

                                                    <div className="flex items-center gap-3 flex-wrap">
                                                        <div className="flex items-center gap-1.5">
                                                            <span className="w-1.5 h-1.5 rounded-full bg-violet-400"></span>
                                                            <span className="font-medium text-gray-600">Complexity:</span>
                                                            <span>{message.metadata.complexity}/5</span>
                                                        </div>
                                                        <div className="flex items-center gap-1.5">
                                                            <span className="w-1.5 h-1.5 rounded-full bg-pink-400"></span>
                                                            <span className="font-medium text-gray-600">Route:</span>
                                                            <span className="uppercase tracking-wider font-medium text-[10px] text-pink-700">{message.role === 'expert' ? 'Human Expert' : 'AI Agent'}</span>
                                                        </div>
                                                    </div>

                                                    {message.metadata.expert && (
                                                        <div className="pt-1.5 mt-1.5 border-t border-gray-100 flex items-center gap-1.5">
                                                            <span className="w-1.5 h-1.5 rounded-full bg-violet-400"></span>
                                                            <span className="font-medium text-gray-600">Matched Expert:</span>
                                                            <span className="text-violet-700 font-medium">{message.metadata.expert.expert_name}</span>
                                                            <span className="text-gray-400">({message.metadata.expert.match_score})</span>
                                                        </div>
                                                    )}
                                                </motion.div>
                                            )}
                                        </div>
                                    </motion.div>
                                ))}
                            </AnimatePresence>

                            {/* Analyzing Overlay */}
                            {analyzing && (
                                <div className="absolute inset-0 flex flex-col items-center justify-center bg-white/20 backdrop-blur-[2px] z-30 rounded-[32px]">
                                    <motion.div
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        className="flex flex-col items-center justify-center"
                                    >
                                        <div className="relative w-16 h-16 mb-4">
                                            <div className="absolute inset-0 rounded-full border-4 border-t-gray-800 border-r-transparent border-b-gray-400 border-l-transparent animate-spin" />
                                            <div className="absolute inset-2 rounded-full border-4 border-t-gray-400 border-r-transparent border-b-gray-800 border-l-transparent animate-spin-reverse opacity-50" />
                                        </div>
                                        <p className="text-gray-600 font-medium animate-pulse">Analyzing complexity...</p>
                                    </motion.div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input Area */}
                        <div className="p-6 bg-white/40 backdrop-blur-md border-t border-white/30 relative z-20">
                            <PlaceholdersAndVanishInput
                                placeholders={[
                                    "What is the standard deduction for 2024?",
                                    "How do I file for an extension?",
                                    "Can I deduct my home office expenses?",
                                    "What are the tax brackets for 2024?",
                                    "Am I eligible for the Earned Income Tax Credit?"
                                ]}
                                onChange={(e) => setInput(e.target.value)}
                                onSubmit={(e) => {
                                    e.preventDefault();
                                    handleSend();
                                }}
                            />
                        </div>
                    </GlassCard>

                    {/* Expert Panel (Right Side) */}
                    <AnimatePresence>
                        {matchedExpert && (
                            <motion.div
                                initial={{ opacity: 0, width: 0, x: 20 }}
                                animate={{ opacity: 1, width: 350, x: 0 }}
                                exit={{ opacity: 0, width: 0, x: 20 }}
                                transition={{ duration: 0.5, ease: "easeInOut" }}
                                className="h-full overflow-hidden shrink-0"
                            >
                                <GlassCard className="rounded-[32px] p-6 flex flex-col h-full w-[350px]">
                                    <h3 className="text-lg font-bold text-gray-900 mb-6">Expert Chatter</h3>

                                    <div className="flex flex-col items-center text-center mb-6">
                                        <div className="w-24 h-24 rounded-full border-4 border-white shadow-lg mb-4 overflow-hidden relative">
                                            <img
                                                src={matchedExpert.avatar_url}
                                                alt={matchedExpert.expert_name}
                                                className="w-full h-full object-cover"
                                            />
                                        </div>
                                        <h4 className="text-xl font-bold text-gray-900">{matchedExpert.expert_name}</h4>
                                        <p className="text-sm text-violet-500 font-medium flex items-center gap-1 mt-1">
                                            <Sparkles className="w-3 h-3" /> Secondary Support
                                        </p>
                                    </div>

                                    <div className="bg-white/40 rounded-xl p-4 mb-6 text-sm text-gray-600 leading-relaxed border border-white/30 flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-violet-200">
                                        {matchedExpert.expert_bio}
                                    </div>

                                    <ConciergeButton
                                        variant="secondary"
                                        className="w-full justify-center shadow-sm"
                                    >
                                        View Profile
                                    </ConciergeButton>
                                </GlassCard>
                            </motion.div>
                        )}
                    </AnimatePresence>

                </div>
            </div>
        </div>
    );
}