"use client";

import { useState } from "react";
import { ChevronRight, ChevronDown } from "lucide-react";

interface Props {
    legacy: Record<string, any>;
    headless: Record<string, any>;
    diff: Record<string, any>;
}

export function ParityVisualizer({ legacy, headless, diff }: Props) {
    const [expandedLegacy, setExpandedLegacy] = useState(true);
    const [expandedHeadless, setExpandedHeadless] = useState(true);

    return (
        <div className="h-full flex flex-col bg-card rounded-lg border border-border overflow-hidden">
            <div className="px-4 py-3 border-b border-border">
                <h2 className="font-semibold text-sm">Parity Visualizer</h2>
                <p className="text-xs text-muted-foreground mt-1">
                    Side-by-side comparison of API responses
                </p>
            </div>

            <div className="flex-1 grid grid-cols-2 gap-4 p-4 overflow-hidden">
                {/* Legacy Response */}
                <div className="flex flex-col border border-border/50 rounded-md overflow-hidden">
                    <button
                        onClick={() => setExpandedLegacy(!expandedLegacy)}
                        className="flex items-center gap-2 px-3 py-2 bg-muted/30 hover:bg-muted/50 transition-colors"
                    >
                        {expandedLegacy ? (
                            <ChevronDown className="w-4 h-4" />
                        ) : (
                            <ChevronRight className="w-4 h-4" />
                        )}
                        <span className="text-sm font-semibold text-primary">
                            Legacy Response
                        </span>
                    </button>
                    {expandedLegacy && (
                        <div className="flex-1 overflow-auto p-3">
                            <pre className="text-xs font-mono text-foreground whitespace-pre-wrap break-all">
                                {JSON.stringify(legacy, null, 2)}
                            </pre>
                        </div>
                    )}
                </div>

                {/* Headless Response */}
                <div className="flex flex-col border border-border/50 rounded-md overflow-hidden">
                    <button
                        onClick={() => setExpandedHeadless(!expandedHeadless)}
                        className="flex items-center gap-2 px-3 py-2 bg-muted/30 hover:bg-muted/50 transition-colors"
                    >
                        {expandedHeadless ? (
                            <ChevronDown className="w-4 h-4" />
                        ) : (
                            <ChevronRight className="w-4 h-4" />
                        )}
                        <span className="text-sm font-semibold text-secondary">
                            Headless Response
                        </span>
                    </button>
                    {expandedHeadless && (
                        <div className="flex-1 overflow-auto p-3">
                            <pre className="text-xs font-mono text-foreground whitespace-pre-wrap break-all">
                                {JSON.stringify(headless, null, 2)}
                            </pre>
                        </div>
                    )}
                </div>
            </div>

            {/* Diff Summary */}
            {Object.keys(diff).length > 0 && (
                <div className="px-4 py-3 border-t border-border bg-muted/20">
                    <div className="text-xs font-semibold mb-2">Detected Differences:</div>
                    <div className="text-xs text-muted-foreground font-mono">
                        {Object.entries(diff).map(([key, value]) => (
                            <div key={key} className="mb-1">
                                <span className="text-warning">{key}</span>: {JSON.stringify(value).slice(0, 100)}...
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
