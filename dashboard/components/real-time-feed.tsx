"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";
import { ShadowTest } from "@/lib/types";
import { Clock, AlertCircle, CheckCircle2, XCircle } from "lucide-react";

interface RealTimeFeedProps {
    onSelectTest?: (test: ShadowTest) => void;
}

export function RealTimeFeed({ onSelectTest }: RealTimeFeedProps) {
    const [tests, setTests] = useState<ShadowTest[]>([]);
    const [isStale, setIsStale] = useState(false);
    const [selectedId, setSelectedId] = useState<string | null>(null);

    useEffect(() => {
        // Fetch initial tests
        async function fetchTests() {
            const { data, error } = await supabase
                .from("shadow_tests")
                .select("*")
                .order("created_at", { ascending: false })
                .limit(20);

            if (!error && data) {
                setTests(data);
                setIsStale(false);
            }
        }

        fetchTests();

        // Subscribe to realtime changes
        const channel = supabase
            .channel("shadow_tests_changes")
            .on(
                "postgres_changes",
                {
                    event: "*",
                    schema: "public",
                    table: "shadow_tests",
                },
                (payload) => {
                    console.log("Realtime update:", payload);
                    setIsStale(false);

                    if (payload.eventType === "INSERT") {
                        setTests((prev) => [payload.new as ShadowTest, ...prev].slice(0, 20));
                    } else if (payload.eventType === "UPDATE") {
                        setTests((prev) =>
                            prev.map((test) =>
                                test.test_id === (payload.new as ShadowTest).test_id
                                    ? (payload.new as ShadowTest)
                                    : test
                            )
                        );
                    }
                }
            )
            .subscribe();

        // Stale signal detector - if no updates in 5 minutes
        const staleTimer = setInterval(() => {
            const latestUpdate = tests[0]?.updated_at;
            if (latestUpdate) {
                const timeSinceUpdate = Date.now() - new Date(latestUpdate).getTime();
                if (timeSinceUpdate > 5 * 60 * 1000) {
                    setIsStale(true);
                }
            }
        }, 60000);

        return () => {
            channel.unsubscribe();
            clearInterval(staleTimer);
        };
    }, [tests]);

    const getStatusIcon = (status: string) => {
        switch (status) {
            case "complete":
                return <CheckCircle2 className="w-4 h-4 text-success" />;
            case "failed":
                return <XCircle className="w-4 h-4 text-danger" />;
            case "analyzing":
                return <Clock className="w-4 h-4 text-primary animate-pulse-fast" />;
            default:
                return <Clock className="w-4 h-4 text-muted-foreground" />;
        }
    };

    const getVerdictColor = (verdict?: string) => {
        switch (verdict) {
            case "PASS":
                return "text-success";
            case "FAIL":
                return "text-danger";
            case "NEEDS_REVIEW":
                return "text-warning";
            default:
                return "text-muted-foreground";
        }
    };

    return (
        <div className="h-full flex flex-col bg-card rounded-lg border border-border overflow-hidden">
            <div className="px-4 py-3 border-b border-border flex items-center justify-between">
                <h2 className="font-semibold text-sm">Real-Time Test Feed</h2>
                {isStale && (
                    <div className="flex items-center gap-2 text-warning text-xs">
                        <AlertCircle className="w-3 h-3" />
                        <span>Stale Signal</span>
                    </div>
                )}
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-2">
                {tests.length === 0 ? (
                    <div className="text-center text-muted-foreground py-8">
                        No tests yet
                    </div>
                ) : (
                    tests.map((test) => (
                        <div
                            key={test.test_id}
                            onClick={() => {
                                setSelectedId(test.test_id);
                                onSelectTest?.(test);
                            }}
                            className={`p-3 rounded-md bg-muted/30 border transition-colors cursor-pointer ${selectedId === test.test_id
                                    ? "border-primary bg-primary/10"
                                    : "border-border/50 hover:border-primary/50"
                                }`}
                        >
                            <div className="flex items-start justify-between gap-2">
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                        {getStatusIcon(test.status)}
                                        <span className="text-xs font-mono text-muted-foreground truncate">
                                            {test.test_id}
                                        </span>
                                    </div>
                                    <div className="text-sm font-medium mb-1">
                                        {test.merchant_id}
                                    </div>
                                    {test.final_verdict && (
                                        <div className={`text-xs font-semibold ${getVerdictColor(test.final_verdict)}`}>
                                            {test.final_verdict}
                                            {test.risk_score !== undefined && (
                                                <span className="ml-2 text-muted-foreground">
                                                    Risk: {(test.risk_score * 100).toFixed(0)}%
                                                </span>
                                            )}
                                        </div>
                                    )}
                                </div>
                                <div className="text-xs text-muted-foreground whitespace-nowrap">
                                    {new Date(test.updated_at).toLocaleTimeString()}
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
