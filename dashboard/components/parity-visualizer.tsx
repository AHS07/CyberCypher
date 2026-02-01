"use client";

import { useState } from "react";
import { motion } from "framer-motion";

interface Props {
    legacy: Record<string, any>;
    headless: Record<string, any>;
    diff: Record<string, any>;
}

export function ParityVisualizer({ legacy, headless, diff }: Props) {
    const [view, setView] = useState<"split" | "diff">("split");

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
            className="glass-effect squircle-lg overflow-hidden"
        >
            <div className="p-4 border-b border-border-30 flex justify-between items-center">
                <h2 className="text-sm font-semibold">API Comparison</h2>
                <div className="flex gap-2">
                    <motion.button
                        onClick={() => setView("split")}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className={`px-4 py-1-5 squircle text-xs font-medium transition-all ${view === "split"
                                ? "bg-primary text-background"
                                : "bg-card border border-border text-muted hover:text-primary"
                            }`}
                    >
                        Split
                    </motion.button>
                    <motion.button
                        onClick={() => setView("diff")}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className={`px-4 py-1-5 squircle text-xs font-medium transition-all ${view === "diff"
                                ? "bg-primary text-background"
                                : "bg-card border border-border text-muted hover:text-primary"
                            }`}
                    >
                        Diff
                    </motion.button>
                </div>
            </div>

            {view === "split" ? (
                <div className="grid grid-cols-2 gap-4 p-4">
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3 }}
                    >
                        <div className="text-xs text-muted mb-2 font-medium">Legacy</div>
                        <div className="bg-card-50 border border-border squircle p-4 max-h-300 overflow-auto custom-scrollbar">
                            <pre className="text-xs font-mono text-primary-80">
                                {JSON.stringify(legacy, null, 2)}
                            </pre>
                        </div>
                    </motion.div>
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3 }}
                    >
                        <div className="text-xs text-muted mb-2 font-medium">Headless</div>
                        <div className="bg-card-50 border border-border squircle p-4 max-h-300 overflow-auto custom-scrollbar">
                            <pre className="text-xs font-mono text-primary-80">
                                {JSON.stringify(headless, null, 2)}
                            </pre>
                        </div>
                    </motion.div>
                </div>
            ) : (
                <div className="p-4">
                    {Object.keys(diff).length > 0 ? (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ duration: 0.3 }}
                            className="space-y-2"
                        >
                            {Object.entries(diff).map(([key, value], index) => (
                                <motion.div
                                    key={key}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.3, delay: index * 0.05 }}
                                    className="bg-card-50 border border-warning-20 squircle p-4 text-xs haptic-hover"
                                >
                                    <div className="text-warning font-semibold mb-2">{key}</div>
                                    <pre className="text-primary-70 font-mono">
                                        {JSON.stringify(value, null, 2)}
                                    </pre>
                                </motion.div>
                            ))}
                        </motion.div>
                    ) : (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.4 }}
                            className="text-center py-12"
                        >
                            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-success-10 flex items-center justify-center">
                                <svg
                                    className="w-8 h-8 text-success"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M5 13l4 4L19 7"
                                    />
                                </svg>
                            </div>
                            <p className="text-muted text-sm">No differences detected</p>
                        </motion.div>
                    )}
                </div>
            )}
        </motion.div>
    );
}
