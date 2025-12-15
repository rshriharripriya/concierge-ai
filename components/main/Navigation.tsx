"use client";

import { useRouter } from "next/navigation";
import GlassSurface from "@/components/ui/GlassSurface";
import { HoverBorderGradient } from "@/components/ui/hover-border-gradient";

interface NavigationProps {
    onNavigate: (id: string) => void;
}

export function Navigation({ onNavigate }: NavigationProps) {
    const router = useRouter();

    return (
        <nav className="fixed top-6 left-0 right-0 z-50 flex justify-center items-center px-6">
            <GlassSurface className="px-8 py-3 flex items-center gap-8" width="auto" height="auto">
                <div className="hidden md:flex items-center gap-6 text-sm font-medium text-gray-600">
                    <button onClick={() => onNavigate('overview')} className="hover:text-violet-500 transition-colors">Overview</button>
                    <button onClick={() => onNavigate('features')} className="hover:text-violet-500 transition-colors">Features</button>
                    <button onClick={() => onNavigate('technical-overview')} className="hover:text-violet-500 transition-colors">Technical Overview</button>
                    <button onClick={() => onNavigate('architecture')} className="hover:text-violet-500 transition-colors">Architecture</button>
                    
                </div>
            </GlassSurface>

            <div className="absolute right-6">
                <HoverBorderGradient
                    containerClassName="rounded-full"
                    as="button"
                    className="dark:bg-black bg-white text-black dark:text-white flex items-center space-x-2"
                    onClick={() => router.push('/chat')}
                >
                    <span>Try Concierge</span>
                </HoverBorderGradient>
            </div>
        </nav>
    );
}
