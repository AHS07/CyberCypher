"use client";

import { useState } from "react";
import { RealTimeFeed } from "@/components/real-time-feed";
import { ParityVisualizer } from "@/components/parity-visualizer";
import { AgentTrace } from "@/components/agent-trace";
import { ReliabilityBadge } from "@/components/reliability-badge";
import { MitigationGate } from "@/components/mitigation-gate";
import { ShadowTest } from "@/lib/types";
import { Shield } from "lucide-react";

export default function Dashboard() {
  const [selectedTest, setSelectedTest] = useState<ShadowTest | undefined>();

  return (
    <div className="min-h-screen bg-background p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <Shield className="w-8 h-8 text-primary" />
          <h1 className="text-3xl font-bold">Shadow Twin Guardian</h1>
        </div>
        <p className="text-muted-foreground">
          Multi-Agent Orchestration for E-Commerce Migration Parity Testing
        </p>
      </div>

      {/* Reliability Badge */}
      <div className="mb-6">
        <ReliabilityBadge />
      </div>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-12 gap-6 h-[calc(100vh-220px)]">
        {/* Left Column - Real-Time Feed (3 cols) */}
        <div className="col-span-3 h-full">
          <RealTimeFeed />
        </div>

        {/* Center Column - Visualizers (6 cols) */}
        <div className="col-span-6 flex flex-col gap-6 h-full">
          {/* Agent Trace */}
          <div className="flex-1">
            <AgentTrace test={selectedTest} />
          </div>

          {/* Parity Visualizer */}
          <div className="flex-1">
            <ParityVisualizer
              legacy={selectedTest?.legacy_response || {}}
              headless={selectedTest?.headless_response || {}}
              diff={selectedTest?.diff_report || {}}
            />
          </div>
        </div>

        {/* Right Column - Actions & Details (3 cols) */}
        <div className="col-span-3 flex flex-col gap-6 h-full">
          {/* Mitigation Gate */}
          <MitigationGate test={selectedTest} />

          {/* Council Opinions */}
          {selectedTest && selectedTest.council_opinions.length > 0 && (
            <div className="flex-1 bg-card rounded-lg border border-border p-4 overflow-auto">
              <h3 className="font-semibold text-sm mb-4">Council Deliberation</h3>
              <div className="space-y-3">
                {selectedTest.council_opinions.map((opinion, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-muted/30 rounded-md border border-border/50"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-semibold capitalize">
                        {opinion.agent.replace("_", " ")}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {opinion.provider}
                      </span>
                    </div>
                    <div className="text-xs text-foreground/80 mb-2 line-clamp-3">
                      {opinion.analysis}
                    </div>
                    <div className="flex items-center gap-4 text-xs">
                      <span>
                        Risk: <span className="font-semibold">{(opinion.risk_score * 100).toFixed(0)}%</span>
                      </span>
                      <span>
                        Confidence: <span className="font-semibold">{(opinion.confidence * 100).toFixed(0)}%</span>
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
