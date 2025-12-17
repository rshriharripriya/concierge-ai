"use client";

import { motion } from "framer-motion";
import { CheckCircle2, ExternalLink } from "lucide-react";
import { useEffect, useState } from "react";

export function RAGASMetrics() {
    const [metricsData, setMetricsData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch real evaluation metrics from API
        fetch('http://localhost:8000/metrics/latest')
            .then(res => res.json())
            .then(data => {
                setMetricsData(data);
                setLoading(false);
            })
            .catch(err => {
                console.error('Failed to fetch metrics:', err);
                setLoading(false);
            });
    }, []);

    if (loading) {
        return (
            <div className="scroll-mt-24 py-20 bg-[#f5f5f5]">
                <div className="w-full text-center">
                    <p className="text-gray-600">Loading evaluation metrics...</p>
                </div>
            </div>
        );
    }

    if (!metricsData) {
        return null;
    }

    const ragas = metricsData.ragas_metrics || {};
    const routing = metricsData.routing_metrics || {};

    const metrics = [
        {
            name: "Faithfulness",
            score: ragas.faithfulness || 0,
            target: 0.90,
            description: "Answers grounded in retrieved docs",
            status: (ragas.faithfulness || 0) >= 0.90 ? "pass" : (ragas.faithfulness || 0) >= 0.85 ? "near" : "fail"
        },
        {
            name: "Context Precision",
            score: ragas.context_precision || 0,
            target: 0.80,
            description: "Hybrid search ranks relevant docs first",
            status: (ragas.context_precision || 0) >= 0.80 ? "pass" : (ragas.context_precision || 0) >= 0.75 ? "near" : "fail"
        },
        {
            name: "Context Relevancy",
            score: ragas.context_relevancy || 0,
            target: 0.70,
            description: "Retrieved content matches query intent",
            status: (ragas.context_relevancy || 0) >= 0.70 ? "pass" : (ragas.context_relevancy || 0) >= 0.65 ? "near" : "fail"
        },
        {
            name: "Answer Relevancy",
            score: ragas.answer_relevancy || 0,
            target: 0.85,
            description: "Responses directly address user questions",
            status: (ragas.answer_relevancy || 0) >= 0.85 ? "pass" : (ragas.answer_relevancy || 0) >= 0.80 ? "near" : "fail"
        }
    ];

    const routingMetrics = [
        {
            label: "Baseline (Keyword Matching)",
            value: `${Math.round((routing.baseline || 0) * 100)}%`,
            color: "text-gray-600"
        },
        {
            label: "LLM-as-Judge Routing",
            value: `${Math.round((routing.llm_based || 0) * 100)}%`,
            color: "text-[#610a0a]",
            highlight: true
        }
    ];

    return (
        <motion.div
            id="ragas-metrics"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="scroll-mt-24 py-20 bg-[#f5f5f5]"
        >
            <div className="max-w-6xl mx-auto px-6">

                <div className="text-center mb-12">
                    <h2 className="text-3xl font-bold text-[#610a0a] mb-4 font-serif">
                        Evaluation Results
                    </h2>
                    <p className="text-gray-700 font-serif max-w-2xl mx-auto">
                        Using the <strong className="text-[#610a0a]">RAGAS</strong> evaluation framework on 150 test queries,
                        measuring retrieval quality and answer faithfulness.
                    </p>
                </div>

                <div className="grid md:grid-cols-2 gap-8 mb-12">
                    {/* RAGAS Metrics Card */}
                    <div className="bg-white rounded-2xl p-8 shadow-md border border-gray-200">
                        <h3 className="text-xl font-bold text-[#610a0a] mb-6 font-serif">
                            RAG Quality Metrics
                        </h3>
                        <div className="space-y-4">
                            {metrics.map((metric, idx) => (
                                <div key={idx} className="space-y-2">
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm font-semibold text-gray-700">
                                            {metric.name}
                                        </span>
                                        <div className="flex items-center gap-2">
                                            <span className={`text-lg font-bold ${metric.status === 'pass' ? 'text-[#610a0a]' :
                                                metric.status === 'near' ? 'text-[#610a0a]' :
                                                    'text-gray-600'
                                                }`}>
                                                {metric.score.toFixed(2)}
                                            </span>
                                            {metric.status === 'pass' && (
                                                <CheckCircle2 className="w-4 h-4 text-[#610a0a]" />
                                            )}
                                        </div>
                                    </div>
                                    <p className="text-xs text-gray-600">{metric.description}</p>
                                    <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden">
                                        <div
                                            className={`absolute h-full rounded-full transition-all ${metric.status === 'pass' ? 'bg-[#610a0a]' :
                                                metric.status === 'near' ? 'bg-[#a0181e]' :
                                                    'bg-gray-400'
                                                }`}
                                            style={{ width: `${metric.score * 100}%` }}
                                        />
                                        {/* Target indicator */}
                                        <div
                                            className="absolute top-0 h-full w-0.5 bg-gray-400"
                                            style={{ left: `${metric.target * 100}%` }}
                                        />
                                    </div>
                                    <div className="flex justify-between text-xs text-gray-500">
                                        <span>0.0</span>
                                        <span className="text-gray-400">Target: {metric.target}</span>
                                        <span>1.0</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Routing Accuracy Card */}
                    <div className="bg-white rounded-2xl p-8 shadow-md border border-gray-200">
                        <h3 className="text-xl font-bold text-[#610a0a] mb-6 font-serif">
                            Routing Accuracy
                        </h3>

                        <div className="space-y-6">
                            {routingMetrics.map((metric, idx) => (
                                <div
                                    key={idx}
                                    className={`p-4 rounded-xl border-2 ${metric.highlight
                                        ? 'border-[#610a0a] bg-[#610a0a]/5'
                                        : 'border-gray-200 bg-gray-50'
                                        }`}
                                >
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm font-medium text-gray-700">
                                            {metric.label}
                                        </span>
                                        <span className={`text-2xl font-bold ${metric.color}`}>
                                            {metric.value}
                                        </span>
                                    </div>
                                </div>
                            ))}

                            {/* Dynamic Improvement Display */}
                            {routing.improvement_percentage !== null && routing.improvement_percentage !== undefined && routing.improvement_percentage > 0 && (
                                <div className="pt-4 border-t border-gray-200">
                                    <div className="flex items-center gap-2 text-sm text-gray-600">
                                        <span className="font-semibold text-[#610a0a]">
                                            +{routing.improvement_percentage}%
                                        </span>
                                        <span>improvement with LLM-based classification</span>
                                    </div>
                                </div>
                            )}

                        </div>

                        {/* GitHub Link */}
                        <a
                            href="https://github.com/rshriharripriya/concierge-ai/tree/main/evaluation"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="mt-8 flex items-center justify-center gap-2 px-4 py-3 bg-[#610a0a] text-white rounded-lg hover:bg-[#7d0d0d] transition-colors font-medium text-sm"
                        >
                            <span>View Evaluation Code</span>
                            <ExternalLink className="w-4 h-4" />
                        </a>
                    </div>
                </div>

                {/* Footer Note */}
                {/* <div className="text-center">
                    <p className="text-sm text-gray-600 font-serif">
                        All metrics measured on a golden dataset of {metricsData.total_tests || 150}+ tax queries across simple, complex, and urgent scenarios.
                        <br />
                        <span className="text-[#610a0a] font-semibold">Full test harness and reproducible results available in the repository.</span>
                        {metricsData.timestamp && (
                            <><br /><span className="text-xs text-gray-500">Last updated: {new Date(metricsData.timestamp).toLocaleDateString()}</span></>
                        )}
                    </p>
                </div> */}
            </div>
        </motion.div>
    );
}
