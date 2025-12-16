"use client";

import { useRouter } from "next/navigation";
import { FrostedButton } from "@/components/ui/FrostedButton";

interface NavigationProps {
    onNavigate: (id: string) => void;
}

export function Navigation({ onNavigate }: NavigationProps) {
    const router = useRouter();

    return (
        <nav className="fixed top-6 left-0 right-0 z-50 px-4 sm:px-6">
            <div className="max-w-7xl mx-auto">
                {/* Mobile Layout: Simplified navbar + button on same line */}
                <div className="flex md:hidden items-center justify-between gap-3">
                    {/* Simplified mobile navbar */}
                    <div className="flex-1 px-3 py-2.5 bg-white/10 backdrop-blur-md rounded-full border border-white/20 flex items-center text-[#F5F5F5] sm:text-sm font-medium font-serif hover:text-crimson-700 transition-colors whitespace-nowrap justify-center gap-2">
                        <button onClick={() => onNavigate('features')} className="text-[12px] font-medium font-serif hover:text-crimson-700 transition-colors whitespace-nowrap">Features</button>
                        <button onClick={() => onNavigate('architecture')} className="text-[12px] font-medium font-serif hover:text-crimson-700 transition-colors whitespace-nowrap">Architecture</button>
                        <button onClick={() => onNavigate('technical-overview')} className="text-[12px] font-medium font-serif hover:text-crimson-700 transition-colors whitespace-nowrap">Technical Overview</button>
                    </div>

                    {/* Compact Try Concierge button for mobile */}
                    <FrostedButton
                        variant="primary"
                        onClick={() => router.push('/chat')}
                        className="flex-1 px-3 py-2.5 bg-white/10 backdrop-blur-md rounded-full border border-white/20 flex items-center text-[#F5F5F5] sm:text-sm font-medium font-serif hover:text-crimson-700 transition-colors whitespace-nowrap justify-center gap-2">
                        <span className="text-[12px] font-medium font-serif hover:text-crimson-700 transition-colors whitespace-nowrap">Try Concierge</span>
                    </FrostedButton>
                </div>

                {/* Desktop Layout: Full navbar with integrated button */}
                <div className="hidden md:flex items-center justify-center relative">
                    <div className="px-8 py-3 flex items-center gap-6 bg-white/10 backdrop-blur-md rounded-full border border-white/20">
                        <button onClick={() => onNavigate('overview')} className="text-sm font-medium font-serif text-[#F5F5F5] hover:text-crimson-700 transition-colors">Overview</button>
                        <button onClick={() => onNavigate('features')} className="text-sm font-medium font-serif text-[#F5F5F5] hover:text-crimson-700 transition-colors">Features</button>
                        <button onClick={() => onNavigate('technical-overview')} className="text-sm font-medium font-serif text-[#F5F5F5] hover:text-crimson-700 transition-colors">Technical Overview</button>
                        <button onClick={() => onNavigate('architecture')} className="text-sm font-medium font-serif text-[#F5F5F5] hover:text-crimson-700 transition-colors">Architecture</button>
                    </div>

                    {/* Try Concierge button - positioned separately on the right */}
                    <div className="absolute right-0">
                        <FrostedButton
                            variant="primary"
                            onClick={() => router.push('/chat')}
                            className="font-serif"
                        >
                            <span>Try Concierge</span>
                        </FrostedButton>
                    </div>
                </div>
            </div>
        </nav>
    );
}
