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

    return (
        <div
            className="relative flex h-[500px] w-[50%] items-center  justify-center overflow-hidden rounded-lg border bg-background p-10 md:shadow-xl"
            ref={containerRef}
        >
            <div className="flex size-full max-w-5xl flex-col items-stretch justify-between">
                {/* Top Row */}
                {/* Top Row - Removed */}
                <div className="flex flex-row items-center justify-center h-0 opacity-0 pointer-events-none">
                    {/* Placeholder to maintain layout structure if needed, or just empty */}
                </div>

                {/* Middle Row */}
                <div className="flex flex-row items-center justify-between">
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

            {/* Main Flow: Left to Right */}
            <AnimatedBeam containerRef={containerRef} fromRef={userRef} toRef={interfaceRef} startXOffset={55} endXOffset={-75} curvature={0} startYOffset={-15}
                endYOffset={-15} />
            <AnimatedBeam containerRef={containerRef} fromRef={interfaceRef} toRef={aiRef} startXOffset={75} endXOffset={-75} curvature={0} />
            <AnimatedBeam containerRef={containerRef} fromRef={aiRef} toRef={serviceRef} startXOffset={75} endXOffset={-75} curvature={0} />
            <AnimatedBeam containerRef={containerRef} fromRef={serviceRef} toRef={validateRef} startXOffset={75} endXOffset={-75} curvature={0} />

            {/* Feedback Loop: Validate -> interface */}
            <AnimatedBeam
                containerRef={containerRef}
                fromRef={validateRef}
                toRef={interfaceRef}
                curvature={150}
                gradientStartColor="#EC4899"
                gradientStopColor="#8B5CF6"
                startYOffset={-50}
                endYOffset={-50}
                reverse
            />

            {/* Feedback Loop: interface -> user */}
            <AnimatedBeam containerRef={containerRef} fromRef={interfaceRef} toRef={userRef} startXOffset={-75} endXOffset={55} curvature={0} startYOffset={15}
                endYOffset={15} reverse />

            {/* Data Flow: AI <-> DB (Bidirectional RAG) */}
            <AnimatedBeam
                containerRef={containerRef}
                fromRef={aiRef}
                toRef={dbRef}
                curvature={0}
                gradientStartColor="#EC4899"
                gradientStopColor="#8B5CF6"
                startYOffset={50}
                endYOffset={-50}
                startXOffset={-15}
                endXOffset={-15}
            />
            <AnimatedBeam
                containerRef={containerRef}
                fromRef={dbRef}
                toRef={aiRef}
                curvature={0}
                gradientStartColor="#8B5CF6"
                gradientStopColor="#EC4899"
                startYOffset={-50}
                endYOffset={50}
                startXOffset={15}
                endXOffset={15}
                reverse
            />

            {/* Logging Flow: Service/Validate -> DB */}
            <AnimatedBeam
                containerRef={containerRef}
                fromRef={serviceRef}
                toRef={dbRef}
                curvature={0}
                gradientStartColor="#8B5CF6"
                gradientStopColor="#EC4899"
                startYOffset={50}
                endYOffset={-50}
                endXOffset={60}
                reverse
            />

        </div>
    );
}
