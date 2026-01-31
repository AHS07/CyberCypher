"use client";

import { useState } from "react";
import { ShieldCheck, AlertTriangle } from "lucide-react";
import { ShadowTest } from "@/lib/types";

interface Props {
    test?: ShadowTest;
    onMitigate?: () => void;
}

export function MitigationGate({ test, onMitigate }: Props) {
    const [loading, setLoading] = useState(false);

    // Button is active when:
    // 1. Consensus Judge has completed (3 opinions)
    // 2. Risk score is high (>= 0.7) or verdict is FAIL/NEEDS_REVIEW
    // 3. Not already mitigated
    const isActive =
        test &&
        test.council_opinions?.length === 3 &&
        ((test.risk_score && test.risk_score >= 0.7) ||
            test.final_verdict === "FAIL" ||
            test.final_verdict === "NEEDS_REVIEW") &&
        !test.is_mitigated;

    const handleMitigate = async () => {
        if (!test || !isActive) return;

        setLoading(true);
        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/api/mitigate/${test.test_id}`,
                {
                    method: "POST",
                }
            );

            if (response.ok) {
                onMitigate?.();
            }
        } catch (error) {
            console.error("Failed to mitigate:", error);
        } finally {
            setLoading(false);
        }
    };

    if (!test) {
        return (
            <div className="p-4 bg-muted/20 rounded-lg border border-border text-center text-muted-foreground text-sm">
                Select a test to see mitigation options
            </div>
        );
    }

    return (
        <div className="p-4 bg-card rounded-lg border border-border">
            <div className="flex items-start gap-3 mb-4">
                {isActive ? (
                    <AlertTriangle className="w-5 h-5 text-warning flex-shrink-0 mt-0.5" />
                ) : (
                    <ShieldCheck className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                )}
                <div className="flex-1">
                    <h3 className="font-semibold text-sm mb-1">
                        Human-in-the-Loop Gate
                    </h3>
                    {test.is_mitigated ? (
                        <p className="text-xs text-success">
                            ✓ This test has been reviewed and mitigated
                        </p>
                    ) : isActive ? (
                        <p className="text-xs text-warning">
                            High-risk verdict detected. Human review required.
                        </p>
                    ) : (
                        <p className="text-xs text-muted-foreground">
                            {test.status === "analyzing"
                                ? "Waiting for council deliberation to complete..."
                                : "No mitigation needed"}
                        </p>
                    )}
                </div>
            </div>

            {test.mitigation_recommendation && (
                <div className="mb-4 p-3 bg-muted/30 rounded-md">
                    <div className="text-xs font-semibold mb-1">Recommendation:</div>
                    <div className="text-xs text-muted-foreground">
                        {test.mitigation_recommendation}
                    </div>
                </div>
            )}

            <button
                onClick={handleMitigate}
                disabled={!isActive || loading}
                className={`w-full py-2 px-4 rounded-md font-semibold text-sm transition-all ${isActive
                        ? "bg-warning text-background hover:bg-warning/90 shadow-glow cursor-pointer"
                        : "bg-muted/30 text-muted-foreground cursor-not-allowed"
                    }`}
            >
                {loading ? "Processing..." : test.is_mitigated ? "Mitigated" : "Mark as Mitigated"}
            </button>

            {test.risk_score !== undefined && (
                <div className="mt-3 text-center">
                    <div className="text-xs text-muted-foreground">Risk Score</div>
                    <div className={`text-2xl font-bold ${test.risk_score >= 0.7 ? "text-danger" :
                            test.risk_score >= 0.3 ? "text-warning" :
                                "text-success"
                        }`}>
                        {(test.risk_score * 100).toFixed(0)}%
                    </div>
                </div>
            )}
        </div>
    );
}
