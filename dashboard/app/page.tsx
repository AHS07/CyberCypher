"use client";

import { useState, useEffect } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { RealTimeFeed } from "@/components/real-time-feed";
import { ParityVisualizer } from "@/components/parity-visualizer";
import { AgentTrace } from "@/components/agent-trace";
import { ReliabilityBadge } from "@/components/reliability-badge";
import { MitigationGate } from "@/components/mitigation-gate";
import { ShadowTest } from "@/lib/types";

export default function Dashboard() {
  const [selectedTest, setSelectedTest] = useState<ShadowTest | undefined>();
  const { scrollY } = useScroll();

  // Header shrinks on scroll - One UI style
  const headerHeight = useTransform(scrollY, [0, 100], [120, 60]);
  const headerOpacity = useTransform(scrollY, [0, 50], [1, 0.95]);
  const titleSize = useTransform(scrollY, [0, 100], [32, 20]);

  return (
    <div className="min-h-screen bg-background text-primary">
      {/* One UI Style Header - Large and Airy */}
      <motion.header
        style={{ height: headerHeight, opacity: headerOpacity }}
        className="sticky top-0 z-50 glass-effect border-b border-border-30 px-6 flex items-end pb-4 transition-all"
      >
        <div className="w-full max-w-1600 mx-auto">
          <motion.h1
            style={{ fontSize: titleSize }}
            className="font-bold tracking-tight"
          >
            Shadow Twin Guardian
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: scrollY.get() < 50 ? 1 : 0 }}
            className="text-muted text-sm mt-1"
          >
            AI-Powered Migration Safety Net
          </motion.p>
        </div>
      </motion.header>

      {/* Main Content */}
      <div className="max-w-1600 mx-auto px-6 py-8">
        {/* System Health - Breathing Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.68, -0.55, 0.265, 1.55] }}
          className="mb-8"
        >
          <ReliabilityBadge />
        </motion.div>

        {/* Bento Grid Layout */}
        <div className="grid grid-cols-12 gap-6">
          {/* Left Column - Test Feed */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="col-span-12 lg:col-span-3"
          >
            <RealTimeFeed onSelectTest={setSelectedTest} />
          </motion.div>

          {/* Center Column - Visualizations */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="col-span-12 lg:col-span-6 space-y-6"
          >
            <AgentTrace test={selectedTest} />
            <ParityVisualizer
              legacy={selectedTest?.legacy_response || {}}
              headless={selectedTest?.headless_response || {}}
              diff={selectedTest?.diff_report || {}}
            />
          </motion.div>

          {/* Right Column - Actions & Council */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="col-span-12 lg:col-span-3 space-y-6"
          >
            <MitigationGate test={selectedTest} />

            {/* Council Opinions - Chat Style */}
            {selectedTest && selectedTest.council_opinions && selectedTest.council_opinions.length > 0 && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4 }}
                className="glass-effect squircle-lg p-6"
              >
                <h3 className="text-sm font-semibold mb-4">Council Deliberation</h3>
                <div className="space-y-3">
                  {selectedTest.council_opinions.map((opinion: any, idx: number) => {
                    const isLeft = idx % 2 === 0;
                    return (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: isLeft ? -20 : 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{
                          duration: 0.4,
                          delay: idx * 0.1,
                          type: "spring",
                          stiffness: 400,
                          damping: 28
                        }}
                        style={{
                          display: 'flex',
                          justifyContent: isLeft ? 'flex-start' : 'flex-end'
                        }}
                      >
                        <div
                          className={`max-w-85 p-4 squircle haptic-hover ${isLeft
                              ? 'bg-card border border-border'
                              : 'bg-success-10 border border-success-20'
                            }`}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-medium text-muted uppercase tracking-wide">
                              {opinion.agent?.replace("_", " ")}
                            </span>
                            <span
                              className={`text-xs font-bold px-2 py-1 rounded-full ${opinion.risk_score > 0.7
                                  ? "bg-danger-20 text-danger"
                                  : opinion.risk_score > 0.3
                                    ? "bg-warning-20 text-warning"
                                    : "bg-success-20 text-success"
                                }`}
                            >
                              {(opinion.risk_score * 100).toFixed(0)}%
                            </span>
                          </div>
                          <p className="text-sm text-primary-90 leading-relaxed">
                            {opinion.analysis}
                          </p>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </motion.div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
}
