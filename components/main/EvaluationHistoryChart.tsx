"use client";

import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getMetricsHistory } from "@/lib/api";

export function EvaluationHistoryChart() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [metric, setMetric] = useState('Context Relevancy');

    useEffect(() => {
        getMetricsHistory()
            .then(resData => {
                setData(resData.history || []);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch history:", err);
                setLoading(false);
            });
    }, []);

    const metricsOptions = [
        "Faithfulness",
        "Context Precision",
        "Context Recall",
        "Context Relevancy",
        "Answer Relevancy",
        "Routing Accuracy"
    ];

    if (loading) return <div className="h-64 flex items-center justify-center text-gray-500">Loading chart...</div>;
    if (!data.length) return <div className="h-64 flex items-center justify-center text-gray-500">No history data available</div>;

    return (
        <div className="bg-white rounded-2xl p-8 shadow-md border border-gray-200 mt-8">
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold text-[#610a0a] font-serif">
                    Metric History
                </h3>
                <div className="relative">
                    <select
                        value={metric}
                        onChange={(e) => setMetric(e.target.value)}
                        className="appearance-none bg-gray-50 border border-gray-200 text-gray-700 py-2 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-[#610a0a] font-serif text-sm cursor-pointer"
                    >
                        {metricsOptions.map(opt => (
                            <option key={opt} value={opt}>{opt}</option>
                        ))}
                    </select>
                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                        <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" /></svg>
                    </div>
                </div>
            </div>

            <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                        data={data}
                        margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
                    >
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#eee" />
                        <XAxis
                            dataKey="name"
                            tick={{ fontSize: 12, fill: '#666' }}
                            axisLine={false}
                            tickLine={false}
                            dy={10}
                        />
                        <YAxis
                            domain={[0, 1]}
                            tick={{ fontSize: 12, fill: '#666' }}
                            axisLine={false}
                            tickLine={false}
                            tickCount={6}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                                borderRadius: '8px',
                                border: '1px solid #eee',
                                boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                            }}
                            cursor={{ stroke: '#610a0a', strokeWidth: 1, strokeDasharray: '3 3' }}
                        />
                        <Line
                            type="monotone"
                            dataKey={metric}
                            stroke="#610a0a"
                            strokeWidth={3}
                            dot={{ fill: '#610a0a', strokeWidth: 2, r: 4, stroke: '#fff' }}
                            activeDot={{ r: 6, stroke: '#610a0a', strokeWidth: 2, fill: '#fff' }}
                            animationDuration={1500}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
            <p className="text-center text-xs text-gray-400 mt-4 font-serif">
                Showing last {Math.min(5, data.length)} evaluation runs
            </p>
        </div>
    );
}
