"use client";

import { useEffect, useState } from "react";
import { Activity, AlertTriangle, CheckCircle } from "lucide-react";
import { ProviderHealth } from "@/lib/types";

export function ReliabilityBadge() {
    const [providers, setProviders] = useState<ProviderHealth[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchHealth() {
            try {
                const response = await fetch(
                    `${process.env.NEXT_PUBLIC_API_URL}/api/health/providers`
                );
                if (response.ok) {
                    const data = await response.json();
                    setProviders(data);
                }
            } catch (error) {
                console.error("Failed to fetch provider health:", error);
            } finally {
                setLoading(false);
            }
        }

        fetchHealth();
        const interval = setInterval(fetchHealth, 30000); // Refresh every 30s

        return () => clearInterval(interval);
    }, []);

    const getHealthyProvider = () => {
        return providers.find((p) => p.is_healthy);
    };

    const healthyProvider = getHealthyProvider();

    return (
        <div className="flex items-center gap-3 px-4 py-2 bg-muted/30 rounded-lg border border-border">
            <Activity className="w-4 h-4 text-muted-foreground" />
            <div className="flex-1">
                <div className="text-xs font-semibold">LLM Provider Status</div>
                {loading ? (
                    <div className="text-xs text-muted-foreground">Loading...</div>
                ) : healthyProvider ? (
                    <div className="flex items-center gap-2 text-xs">
                        <CheckCircle className="w-3 h-3 text-success" />
                        <span className="text-success font-medium">
                            {healthyProvider.provider.toUpperCase()} Online
                        </span>
                    </div>
                ) : (
                    <div className="flex items-center gap-2 text-xs">
                        <AlertTriangle className="w-3 h-3 text-danger" />
                        <span className="text-danger font-medium">All Providers Down</span>
                    </div>
                )}
            </div>

            {/* Provider Indicators */}
            <div className="flex gap-1">
                {providers.map((provider) => (
                    <div
                        key={provider.provider}
                        className={`w-2 h-2 rounded-full ${provider.is_healthy ? "bg-success" : "bg-danger"
                            }`}
                        title={`${provider.provider}: ${provider.is_healthy ? "Healthy" : "Unhealthy"}`}
                    />
                ))}
            </div>
        </div>
    );
}
