"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { createClient } from "@supabase/supabase-js";
import { ShadowTest } from "@/lib/types";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

interface Props {
  onSelectTest: (test: ShadowTest) => void;
}

export function RealTimeFeed({ onSelectTest }: Props) {
  const [tests, setTests] = useState<ShadowTest[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    // Fetch initial tests
    const fetchTests = async () => {
      const { data } = await supabase
        .from("shadow_tests")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(20);

      if (data) setTests(data);
    };

    fetchTests();

    // Subscribe to real-time updates
    const channel = supabase
      .channel("shadow_tests_changes")
      .on(
        "postgres_changes",
        { event: "*", schema: "public", table: "shadow_tests" },
        (payload) => {
          if (payload.eventType === "INSERT") {
            setTests((prev) => [payload.new as ShadowTest, ...prev].slice(0, 20));
          }
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  const handleSelect = (test: ShadowTest) => {
    setSelectedId(test.id.toString());
    onSelectTest(test);
  };

  return (
    <div className="glass-effect squircle-lg p-6 h-calc-viewport flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold">Live Tests</h2>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-success breathing-glow" />
          <span className="text-xs text-muted">Monitoring</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar space-y-2">
        <AnimatePresence mode="popLayout">
          {tests.map((test, index) => (
            <motion.div
              key={test.id}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{
                type: "spring",
                stiffness: 400,
                damping: 28,
                delay: index * 0.05,
              }}
              layout
            >
              <motion.button
                onClick={() => handleSelect(test)}
                className={`w-full p-4 squircle text-left transition-all haptic-press ${selectedId === test.id.toString()
                    ? "bg-primary-10 border-2 border-primary-30 hover:shadow-lg"
                    : "bg-card border border-border hover:border-primary-20 haptic-hover"
                  }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.97 }}
              >
                <div className="flex items-start justify-between mb-2">
                  <span className="text-xs font-medium text-muted">
                    {test.merchant_id}
                  </span>
                  <span
                    className={`text-xs font-bold px-2 py-1 rounded-full ${test.status === "complete"
                        ? "bg-success-20 text-success"
                        : test.status === "failed"
                          ? "bg-danger-20 text-danger"
                          : "bg-warning-20 text-warning"
                      }`}
                  >
                    {test.status}
                  </span>
                </div>

                <div className="text-sm text-primary-90 mb-2 line-clamp-2">
                  {test.test_id || "Unnamed Test"}
                </div>

                <div className="flex items-center gap-3 text-xs text-muted">
                  <span>{new Date(test.created_at).toLocaleTimeString()}</span>
                  {test.risk_score !== undefined && (
                    <span className="flex items-center gap-1">
                      <div className="w-1 h-2 rounded-full bg-muted" />
                      {(test.risk_score * 100).toFixed(0)}% risk
                    </span>
                  )}
                </div>
              </motion.button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
