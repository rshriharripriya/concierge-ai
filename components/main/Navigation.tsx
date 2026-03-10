"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { FrostedButton } from "@/components/ui/FrostedButton";

interface NavigationProps {
    onNavigate: (id: string) => void;
}

export function Navigation({ onNavigate }: NavigationProps) {
    const router = useRouter();
    const [isLightBg, setIsLightBg] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            const archElement = document.getElementById("architecture");
            if (archElement) {
                const container = archElement.parentElement;
                if (container) {
                    const rect = container.getBoundingClientRect();
                    // Check if the navbar (roughly top 0-80px) is overlapping with this light container
                    if (rect.top <= 60 && rect.bottom >= 60) {
                        setIsLightBg(true);
                    } else {
                        setIsLightBg(false);
                    }
                }
            }
        };

        window.addEventListener("scroll", handleScroll, { passive: true });
        handleScroll(); // Check initial state

        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    return (
        <nav className="fixed top-6 left-0 right-0 z-50 px-4 sm:px-6">
            <div className="max-w-7xl mx-auto">
                {/* Mobile Layout: Simplified navbar + button on same line */}
                <div className="flex md:hidden items-center justify-between gap-3">
                    {/* Simplified mobile navbar */}
                    <div className={`flex-1 px-3 py-2.5 backdrop-blur-md rounded-full border flex items-center sm:text-sm font-medium font-serif transition-colors whitespace-nowrap justify-center gap-2 duration-300 ${isLightBg ? 'bg-black/40 border-black/50 shadow-lg text-[#610a0a]' : 'bg-white/10 border-white/20 text-[#F5F5F5]'}`}>
                        <button onClick={() => onNavigate('features')} className={`text-[12px] font-medium font-serif transition-colors whitespace-nowrap ${isLightBg ? 'hover:text-[#821e1e]' : 'hover:text-crimson-400'}`}>Features</button>
                        <button onClick={() => onNavigate('architecture')} className={`text-[12px] font-medium font-serif transition-colors whitespace-nowrap ${isLightBg ? 'hover:text-[#821e1e]' : 'hover:text-crimson-400'}`}>Architecture</button>
                        <button onClick={() => onNavigate('technical-overview')} className={`text-[12px] font-medium font-serif transition-colors whitespace-nowrap ${isLightBg ? 'hover:text-[#821e1e]' : 'hover:text-crimson-400'}`}>Technical Overview</button>
                    </div>

                    {/* Compact Try Concierge button for mobile */}
                    <FrostedButton
                        variant="primary"
                        onClick={() => router.push('/chat')}
                        className={`flex-1 px-3 py-2.5 backdrop-blur-md rounded-full border flex items-center sm:text-sm font-medium font-serif transition-colors whitespace-nowrap justify-center gap-2 duration-300 ${isLightBg ? 'bg-black/10 border-none shadow-lg text-[#610a0a]' : 'bg-white/10 border-white/20 text-[#F5F5F5]'}`}>
                        <span className={`text-[12px] font-medium font-serif transition-colors whitespace-nowrap ${isLightBg ? 'hover:text-[#821e1e]' : 'hover:text-crimson-400'}`}>Try Concierge</span>
                    </FrostedButton>
                </div>

                {/* Desktop Layout: Full navbar with integrated button */}
                <div className="hidden md:flex items-center justify-center relative">
                    <div className={`px-8 py-3 flex items-center gap-6 backdrop-blur-md rounded-full border transition-all duration-300 ${isLightBg ? 'bg-black/10 border-none shadow-lg' : 'bg-white/10 border-white/20'}`}>
                        <button onClick={() => onNavigate('overview')} className={`text-sm font-medium font-serif transition-colors ${isLightBg ? 'text-[#610a0a] hover:text-[#821e1e]' : 'text-[#F5F5F5] hover:text-crimson-400'}`}>Overview</button>
                        <button onClick={() => onNavigate('features')} className={`text-sm font-medium font-serif transition-colors ${isLightBg ? 'text-[#610a0a] hover:text-[#821e1e]' : 'text-[#F5F5F5] hover:text-crimson-400'}`}>Features</button>
                        <button onClick={() => onNavigate('technical-overview')} className={`text-sm font-medium font-serif transition-colors ${isLightBg ? 'text-[#610a0a] hover:text-[#821e1e]' : 'text-[#F5F5F5] hover:text-crimson-400'}`}>Technical Overview</button>
                        <button onClick={() => onNavigate('architecture')} className={`text-sm font-medium font-serif transition-colors ${isLightBg ? 'text-[#610a0a] hover:text-[#821e1e]' : 'text-[#F5F5F5] hover:text-crimson-400'}`}>Architecture</button>
                    </div>

                    {/* Try Concierge button - positioned separately on the right */}
                    <div className="absolute right-0">
                        <FrostedButton
                            variant="primary"
                            onClick={() => router.push('/chat')}
                            className={`font-serif transition-all duration-300 ${isLightBg ? 'bg-black/10 border-none shadow-lg text-[#610a0a] hover:text-[#821e1e]' : 'bg-white/10 border-white/20 text-[#F5F5F5] hover:text-crimson-400'}`}
                        >
                            <span className="text-sm font-medium whitespace-nowrap">Try Concierge</span>
                        </FrostedButton>
                    </div>
                </div>
            </div>
        </nav>
    );
}
