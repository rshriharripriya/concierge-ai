"use client";

import { useRouter } from "next/navigation";
import { FrostedButton } from "@/components/ui/FrostedButton";

interface NavigationProps {
    onNavigate: (id: string) => void;
}

export function Navigation({ onNavigate }: NavigationProps) {
    const router = useRouter();

    return (
        <nav className="fixed top-6 left-0 right-0 z-50 flex justify-center items-center px-6">
            <div className="px-8 py-3 flex items-center gap-8 bg-white/10 backdrop-blur-md rounded-full border border-white/20">
                <div className="hidden md:flex items-center gap-6 text-sm font-medium font-serif text-[#F5F5F5]">
                    <button onClick={() => onNavigate('overview')} className="hover:text-crimson-700 transition-colors">Overview</button>
                    <button onClick={() => onNavigate('features')} className="hover:text-crimson-700 transition-colors">Features</button>
                    <button onClick={() => onNavigate('technical-overview')} className="hover:text-crimson-700 transition-colors">Technical Overview</button>
                    <button onClick={() => onNavigate('architecture')} className="hover:text-crimson-700 transition-colors">Architecture</button>

                </div>
            </div>

            <div className="absolute right-6">
                <FrostedButton
                    variant="primary"
                    onClick={() => router.push('/chat')}
                    className="font-serif"
                >
                    <span>Try Concierge</span>
                </FrostedButton>
            </div>
        </nav>
    );
}
