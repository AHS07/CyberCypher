"use client";

import { motion } from "framer-motion";

interface Props {
    uptime?: number;
    latency?: number;
    errorRate?: number;
}

export function ReliabilityBadge({
    uptime = 99.9,
    latency = 45,
    errorRate = 0.05
}: Props) {
    const getStatus = () => {
        if (uptime >= 99.9 && errorRate < 0.1) return "operational";
        if (uptime >= 99 && errorRate < 1) return "degraded";
        return "outage";
    };

    const status = getStatus();

    const statusConfig = {
        operational: {
            label: "Operational",
            color: "text-success",
            bg: "bg-success-10",
            border: "border-success-20",
        },
        degraded: {
            label: "Degraded",
            color: "text-warning",
            bg: "bg-warning-10",
            border: "border-warning-20",
        },
        outage: {
            label: "Outage",
            color: "text-danger",
            bg: "bg-danger-10",
            border: "border-danger-20",
        },
    };

    const config = statusConfig[status];

    return (
        <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="glass-effect squircle-lg p-6"
        >
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-sm font-semibold">System Health</h2>
                <motion.div
                    initial={{ scale: 0.9 }}
                    animate={{ scale: 1 }}
                    transition={{ duration: 0.3, delay: 0.2 }}
                    className={`px-4 py-1-5 rounded-full text-xs font-medium ${config.bg} ${config.color} ${config.border} border breathing-glow`}
                >
                    {config.label}
                </motion.div>
            </div>

            <div className="space-y-5">
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: 0.1 }}
                >
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-xs text-muted font-medium">Uptime</span>
                        <span className="text-sm font-bold">{uptime.toFixed(2)}%</span>
                    </div>
                    <div className="h-2 bg-card rounded-full overflow-hidden">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${uptime}%` }}
                            transition={{ duration: 1, delay: 0.3, ease: "easeOut" }}
                            className="h-full bg-success rounded-full"
                        />
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: 0.2 }}
                >
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-xs text-muted font-medium">Latency</span>
                        <span className="text-sm font-bold">{latency}ms</span>
                    </div>
                    <div className="h-2 bg-card rounded-full overflow-hidden">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${Math.min((latency / 500) * 100, 100)}%` }}
                            transition={{ duration: 1, delay: 0.4, ease: "easeOut" }}
                            className={`h-full rounded-full ${latency < 100 ? "bg-success" : latency < 300 ? "bg-warning" : "bg-danger"
                                }`}
                        />
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: 0.3 }}
                >
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-xs text-muted font-medium">Error Rate</span>
                        <span className="text-sm font-bold">{errorRate.toFixed(2)}%</span>
                    </div>
                    <div className="h-2 bg-card rounded-full overflow-hidden">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${Math.min(errorRate * 10, 100)}%` }}
                            transition={{ duration: 1, delay: 0.5, ease: "easeOut" }}
                            className={`h-full rounded-full ${errorRate < 0.1 ? "bg-success" : errorRate < 1 ? "bg-warning" : "bg-danger"
                                }`}
                        />
                    </div>
                </motion.div>
            </div>
        </motion.div>
    );
}
