"use client";

import { motion } from "framer-motion";
import { ShadowTest } from "@/lib/types";

interface Props {
  test?: ShadowTest;
}

export function MitigationGate({ test }: Props) {
  const handleApprove = async () => {
    if (!test) return;
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_ORCHESTRATOR_URL}/api/mitigate/${test.test_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        alert('Migration approved and marked as mitigated');
        // Refresh the page or update state
        window.location.reload();
      } else {
        alert('Failed to approve migration');
      }
    } catch (error) {
      console.error('Error approving migration:', error);
      alert('Error approving migration');
    }
  };

  const handleReview = () => {
    if (!test) return;
    alert(`Test ${test.test_id} flagged for manual review. A human reviewer will be notified.`);
  };

  const handleBlock = () => {
    if (!test) return;
    alert(`Migration blocked for test ${test.test_id}. This will prevent deployment until issues are resolved.`);
  };

  if (!test) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
        className="glass-effect squircle-lg p-6"
      >
        <h2 className="text-sm font-semibold mb-4">Risk Assessment</h2>
        <p className="text-muted text-xs">Select a test to view risk analysis</p>
      </motion.div>
    );
  }

  const riskScore = test.risk_score || 0;
  const riskLevel =
    riskScore > 0.7 ? "high" : riskScore > 0.3 ? "medium" : "low";

  const riskConfig = {
    high: {
      label: "High Risk",
      color: "text-danger",
      bg: "bg-danger-10",
      border: "border-danger-30",
      glow: "glow-soft",
    },
    medium: {
      label: "Medium Risk",
      color: "text-warning",
      bg: "bg-warning-10",
      border: "border-warning-30",
      glow: "glow-soft",
    },
    low: {
      label: "Low Risk",
      color: "text-success",
      bg: "bg-success-10",
      border: "border-success-30",
      glow: "glow-soft",
    },
  };

  const config = riskConfig[riskLevel];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
      className="glass-effect squircle-lg p-6"
    >
      <h2 className="text-sm font-semibold mb-6">Risk Assessment</h2>

      {/* Risk Score Circle */}
      <div className="flex flex-col items-center mb-6">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{
            type: "spring",
            stiffness: 400,
            damping: 28,
            delay: 0.2
          }}
          className={`w-32 h-32 rounded-full ${config.bg} ${config.border} border-2 flex items-center justify-center mb-3 ${config.glow}`}
        >
          <div className="text-center">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className={`text-3xl font-bold ${config.color}`}
            >
              {(riskScore * 100).toFixed(0)}%
            </motion.div>
            <div className="text-xs text-muted mt-1">Risk Score</div>
          </div>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className={`px-4 py-1-5 squircle ${config.bg} ${config.color} ${config.border} border text-xs font-semibold`}
        >
          {config.label}
        </motion.div>
      </div>

      {/* Action Buttons */}
      <div className="space-y-3">
        <motion.button
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.97 }}
          onClick={handleApprove}
          className="w-full py-3 squircle bg-success text-background font-semibold text-sm haptic-press hover:shadow-lg transition-all"
        >
          Approve Migration
        </motion.button>

        <motion.button
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.97 }}
          onClick={handleReview}
          className="w-full py-3 squircle bg-card border border-border text-primary font-semibold text-sm haptic-press hover:border-primary-30 transition-all"
        >
          Request Review
        </motion.button>

        <motion.button
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.97 }}
          onClick={handleBlock}
          className="w-full py-3 squircle bg-danger-10 border border-danger-30 text-danger font-semibold text-sm haptic-press hover:bg-danger-20 transition-all"
        >
          Block Migration
        </motion.button>
      </div>

      {/* Metadata */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.9 }}
        className="mt-6 pt-6 border-t border-border-30 space-y-2"
      >
        <div className="flex justify-between text-xs">
          <span className="text-muted">Merchant</span>
          <span className="text-primary font-medium">{test.merchant_id}</span>
        </div>
        <div className="flex justify-between text-xs">
          <span className="text-muted">Status</span>
          <span className={`font-medium ${test.status === "complete" ? "text-success" : "text-danger"
            }`}>
            {test.status}
          </span>
        </div>
        <div className="flex justify-between text-xs">
          <span className="text-muted">Timestamp</span>
          <span className="text-primary font-medium">
            {new Date(test.created_at).toLocaleString()}
          </span>
        </div>
      </motion.div>
    </motion.div>
  );
}
