"use client";

import React, { useRef } from "react";
import { AnimatedBeam } from "@/components/ui/animated-beam";
import { cn } from "@/lib/utils";

const LabelNode = React.forwardRef<
    HTMLDivElement,
    { className?: string; children: React.ReactNode }
>(({ className, children }, ref) => {
    return (
        <div
            ref={ref}
            className={cn(
                "z-10 flex items-center justify-center rounded-full border px-6 py-4 shadow-[0_0_20px_-12px_rgba(0,0,0,0.8)] text-sm font-semibold font-serif transition-all hover:scale-105 md:px-8 md:py-6 md:text-base",
                className,
            )}
        >
            {children}
        </div>
    );
});

LabelNode.displayName = "LabelNode";

export default function SystemArchitecture() {
    const containerRef = useRef<HTMLDivElement>(null);
    const userRef = useRef<HTMLDivElement>(null);
    const interfaceRef = useRef<HTMLDivElement>(null);
    const aiRef = useRef<HTMLDivElement>(null);
    const serviceRef = useRef<HTMLDivElement>(null);
    const validateRef = useRef<HTMLDivElement>(null);
    const dbRef = useRef<HTMLDivElement>(null);

    const isDesktop = useMediaQuery("(min-width: 768px)");

    return (
        <div
            className="relative flex h-[800px] md:h-[500px] w-full md:w-[80%] lg:w-[70%] 2xl:w-[50%] items-center justify-center overflow-hidden rounded-lg border border-white/10 bg-[#f5f5f5]/20 backdrop-blur-md p-10 md:shadow-xl  bg-white rounded-2xl p-8 shadow-md border border-gray-200"
            ref={containerRef}
        >
            <div className="flex size-full max-w-5xl flex-col items-stretch justify-between gap-10 md:gap-0">

                <div className="flex flex-row items-center justify-center h-0 opacity-0 pointer-events-none">
                    {/* Placeholder */}
                </div>

                {/* Middle Row (Vertical on mobile, Horizontal on desktop) */}
                <div className="flex flex-col md:flex-row items-center justify-between gap-8 md:gap-0">
                    <LabelNode ref={userRef} className="border-[#821e1e]/30 text-[#610a0a]">
                        User
                    </LabelNode>
                    <LabelNode ref={interfaceRef} className="border-[#821e1e]/40 text-[#610a0a]">
                        Interface
                    </LabelNode>
                    <LabelNode ref={aiRef} className="border-[#610a0a]/40 text-[#610a0a]">
                        AI Agent
                    </LabelNode>
                    <LabelNode ref={serviceRef} className="border-[#821e1e]/40 text-[#610a0a]">
                        Service
                    </LabelNode>
                    <LabelNode ref={validateRef} className="border-[#821e1e]/30 text-[#821e1e]">
                        Validate
                    </LabelNode>
                </div>

                {/* Bottom Row */}
                <div className="flex flex-row items-center justify-center">
                    <LabelNode ref={dbRef} className="w-2/3 border-[#821e1e]/30 bg-[#610a0a]/5 text-[#3b0505]">
                        Supabase Vector DB
                    </LabelNode>
                </div>
            </div>

            {/* Main Flow */}
            <AnimatedBeam
                containerRef={containerRef}
                fromRef={userRef}
                toRef={interfaceRef}
                startXOffset={isDesktop ? 55 : -20}
                endXOffset={isDesktop ? -75 : -20}
                startYOffset={isDesktop ? -15 : 20}
                endYOffset={isDesktop ? -15 : -20}
                curvature={0}
            />
            <AnimatedBeam
                containerRef={containerRef}
                fromRef={interfaceRef}
                toRef={aiRef}
                startXOffset={isDesktop ? 75 : 0}
                endXOffset={isDesktop ? -75 : 0}
                startYOffset={isDesktop ? 0 : 20}
                endYOffset={isDesktop ? 0 : -20}
                curvature={0}
            />
            <AnimatedBeam
                containerRef={containerRef}
                fromRef={aiRef}
                toRef={serviceRef}
                startXOffset={isDesktop ? 75 : 0}
                endXOffset={isDesktop ? -75 : 0}
                startYOffset={isDesktop ? 0 : 20}
                endYOffset={isDesktop ? 0 : -20}
                curvature={0}
            />
            <AnimatedBeam
                containerRef={containerRef}
                fromRef={serviceRef}
                toRef={validateRef}
                startXOffset={isDesktop ? 75 : 0}
                endXOffset={isDesktop ? -75 : 0}
                startYOffset={isDesktop ? 0 : 20}
                endYOffset={isDesktop ? 0 : -20}
                curvature={0}
            />

            {/* Feedback Loop: Validate -> interface */}
            <AnimatedBeam
                containerRef={containerRef}
                fromRef={validateRef}
                toRef={interfaceRef}
                curvature={isDesktop ? 150 : 100}
                gradientStartColor="#821e1e"
                gradientStopColor="#610a0a"
                startYOffset={isDesktop ? -50 : 0}
                endYOffset={isDesktop ? -50 : 0}
                startXOffset={isDesktop ? 0 : -60}
                endXOffset={isDesktop ? 0 : -65}
                reverse
            />

            {/* Feedback Loop: interface -> user */}
            <AnimatedBeam
                containerRef={containerRef}
                fromRef={interfaceRef}
                toRef={userRef}
                startXOffset={isDesktop ? -75 : 20}
                endXOffset={isDesktop ? 55 : 20}
                startYOffset={isDesktop ? 15 : -20}
                endYOffset={isDesktop ? 15 : 20}
                reverse
            />

            {/* Data Flow: AI <-> DB (Bidirectional RAG) */}
            <AnimatedBeam
                containerRef={containerRef}
                fromRef={aiRef}
                toRef={dbRef}
                curvature={isDesktop ? 0 : 0}
                gradientStartColor="#821e1e"
                gradientStopColor="#610a0a"
                startYOffset={isDesktop ? 50 : 30}
                endYOffset={isDesktop ? -50 : -50}
                startXOffset={isDesktop ? -15 : 30}
                endXOffset={isDesktop ? -15 : 30}
            />
            <AnimatedBeam
                containerRef={containerRef}
                fromRef={dbRef}
                toRef={aiRef}
                curvature={0}
                gradientStartColor="#610a0a"
                gradientStopColor="#821e1e"
                startYOffset={isDesktop ? -50 : -50}
                endYOffset={isDesktop ? 50 : 30}
                startXOffset={isDesktop ? 15 : -30}
                endXOffset={isDesktop ? 15 : -30}
                reverse
            />

            {/* Logging Flow: Service/Validate -> DB */}
            <AnimatedBeam
                containerRef={containerRef}
                fromRef={serviceRef}
                toRef={dbRef}
                curvature={isDesktop ? 0 : -50}
                gradientStartColor="#610a0a"
                gradientStopColor="#821e1e"
                startYOffset={isDesktop ? 50 : 20}
                endYOffset={isDesktop ? -50 : -50}
                endXOffset={isDesktop ? 60 : 50}
                startXOffset={isDesktop ? 0 : 50}
                reverse
            />

        </div>
    );
}

function useMediaQuery(query: string) {
    const [value, setValue] = React.useState(false);

    React.useEffect(() => {
        function onChange(event: MediaQueryListEvent) {
            setValue(event.matches);
        }

        const result = matchMedia(query);
        result.addEventListener("change", onChange);
        setValue(result.matches);

        return () => result.removeEventListener("change", onChange);
    }, [query]);

    return value;
}
