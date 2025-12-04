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
                "z-10 flex items-center justify-center rounded-full border  px-6 py-4 shadow-[0_0_20px_-12px_rgba(0,0,0,0.8)] text-sm font-semibold transition-all hover:scale-105 md:px-8 md:py-6 md:text-base",
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
            className="relative flex h-[800px] md:h-[500px] w-full md:w-[80%] lg:w-[70%] 2xl:w-[50%] items-center justify-center overflow-hidden rounded-lg border bg-background p-10 md:shadow-xl"
            ref={containerRef}
        >
            <div className="flex size-full max-w-5xl flex-col items-stretch justify-between gap-10 md:gap-0">

                <div className="flex flex-row items-center justify-center h-0 opacity-0 pointer-events-none">
                    {/* Placeholder */}
                </div>

                {/* Middle Row (Vertical on mobile, Horizontal on desktop) */}
                <div className="flex flex-col md:flex-row items-center justify-between gap-8 md:gap-0">
                    <LabelNode ref={userRef} className="border-gray-200 text-gray-700">
                        User
                    </LabelNode>
                    <LabelNode ref={interfaceRef} className="border-violet-300 text-violet-800">
                        Interface
                    </LabelNode>
                    <LabelNode ref={aiRef} className="border-pink-300 text-pink-800">
                        AI Agent
                    </LabelNode>
                    <LabelNode ref={serviceRef} className="border-violet-300 text-violet-800">
                        Service
                    </LabelNode>
                    <LabelNode ref={validateRef} className="border-pink-200 text-pink-700">
                        Validate
                    </LabelNode>
                </div>

                {/* Bottom Row */}
                <div className="flex flex-row items-center justify-center">
                    <LabelNode ref={dbRef} className="w-2/3 border-violet-500/30 bg-violet-50/50 text-violet-900">
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
                gradientStartColor="#EC4899"
                gradientStopColor="#8B5CF6"
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
                gradientStartColor="#EC4899"
                gradientStopColor="#8B5CF6"
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
                gradientStartColor="#8B5CF6"
                gradientStopColor="#EC4899"
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
                gradientStartColor="#8B5CF6"
                gradientStopColor="#EC4899"
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
