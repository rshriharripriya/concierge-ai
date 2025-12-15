"use client";

import { motion } from "framer-motion";
import { IconBadge } from "@/components/sub/IconBadge";

export function TechnicalOverview() {
    return (
        <motion.div
            id="technical-overview"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="mb-32 scroll-mt-24"
        >
            <div className="max-w-5xl mx-auto">
                <div className="text-center mb-12">
                    <h2 className="text-3xl font-bold text-gray-900 mb-4">How It Works</h2>
                    <p className="text-gray-600">Multi-stage intelligent routing pipeline</p>
                </div>

                <div className="p-8 md:p-12 bg-white rounded-2xl shadow-[0_4px_20px_rgba(192,192,192,0.15)]">
                    <div className="space-y-8">
                        {/* Stage 1 */}
                        <div className="flex gap-6">
                            <div className="mt-3 flex-shrink-0">
                                <IconBadge size="sm">
                                    <span className="text-lg text-sky-800/50">1</span>
                                </IconBadge>
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-gray-900 mb-2">Intent Classification</h3>
                                <p className="text-gray-600 leading-relaxed">
                                    Your question is analyzed using semantic understanding to determine what type of tax help you need, from simple filing questions to complex investment scenarios.
                                </p>
                            </div>
                        </div>

                        {/* Stage 2 */}
                        <div className="flex gap-6">
                            <div className="mt-3 flex-shrink-0">
                                <IconBadge size="sm">
                                    <span className="text-lg text-violet-800/50">2</span>
                                </IconBadge>
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-gray-900 mb-2">Complexity Assessment</h3>
                                <p className="text-gray-600 leading-relaxed">
                                    An intelligent scoring system evaluates your question's complexity, checking for urgency indicators, technical terms, and multi-part scenarios to route you correctly.
                                </p>
                            </div>
                        </div>

                        {/* Stage 3 */}
                        <div className="flex gap-6">
                            <div className="mt-3 flex-shrink-0">
                                <IconBadge size="sm">
                                    <span className="text-lg text-pink-800/50">3</span>
                                </IconBadge>
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-gray-900 mb-2">AI Response or Expert Matching</h3>
                                <p className="text-gray-600 leading-relaxed">
                                    Simple questions get instant AI answers with cited sources. Complex questions are matched with specialized tax professionals based on expertise, availability, and your specific needs.
                                </p>
                            </div>
                        </div>

                        {/* Stage 4 */}
                        <div className="flex gap-6">
                            <div className="mt-3 flex-shrink-0">
                                <IconBadge size="sm" >
                                    <span className="text-lg text-blue-800/50">4</span>
                                </IconBadge>
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-gray-900 mb-2">Conversational Learning</h3>
                                <p className="text-gray-600 leading-relaxed">
                                    Throughout your conversation, the system remembers context so follow-up questions feel natural, and you don't have to repeat yourself.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
