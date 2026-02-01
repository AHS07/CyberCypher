"use client";

import { motion } from "framer-motion";
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MarkerType
} from "reactflow";
import "reactflow/dist/style.css";
import { ShadowTest } from "@/lib/types";

interface Props {
  test?: ShadowTest;
}

export function AgentTrace({ test }: Props) {
  if (!test) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
        className="glass-effect squircle-lg p-8 h-400 flex items-center justify-center"
      >
        <p className="text-muted text-sm">Select a test to view agent trace</p>
      </motion.div>
    );
  }

  const nodes: Node[] = [
    {
      id: "1",
      type: "input",
      data: { label: "Request" },
      position: { x: 250, y: 0 },
      style: {
        background: "#0C0C0E",
        color: "#FFFFFF",
        border: "1px solid #1C1C1E",
        borderRadius: "28px",
        padding: "12px 20px",
        fontSize: "12px",
        fontWeight: "600",
      },
    },
    {
      id: "2",
      data: { label: "Primary Analyzer" },
      position: { x: 100, y: 100 },
      style: {
        background: "#10B981",
        color: "#000000",
        border: "2px solid #10B981",
        borderRadius: "28px",
        padding: "12px 20px",
        fontSize: "12px",
        fontWeight: "600",
      },
    },
    {
      id: "3",
      data: { label: "Skeptic Critic" },
      position: { x: 250, y: 100 },
      style: {
        background: "#F59E0B",
        color: "#000000",
        border: "2px solid #F59E0B",
        borderRadius: "28px",
        padding: "12px 20px",
        fontSize: "12px",
        fontWeight: "600",
      },
    },
    {
      id: "4",
      data: { label: "Consensus Judge" },
      position: { x: 400, y: 100 },
      style: {
        background: "#FFFFFF",
        color: "#000000",
        border: "2px solid #FFFFFF",
        borderRadius: "28px",
        padding: "12px 20px",
        fontSize: "12px",
        fontWeight: "600",
      },
    },
    {
      id: "5",
      type: "output",
      data: {
        label: test.status === "complete" ? "✓ Complete" : test.status === "failed" ? "✗ Failed" : "⏳ Processing"
      },
      position: { x: 250, y: 200 },
      style: {
        background: test.status === "complete" ? "#10B981" : test.status === "failed" ? "#EF4444" : "#F59E0B",
        color: "#000000",
        border: `2px solid ${test.status === "complete" ? "#10B981" : test.status === "failed" ? "#EF4444" : "#F59E0B"}`,
        borderRadius: "28px",
        padding: "12px 20px",
        fontSize: "12px",
        fontWeight: "600",
      },
    },
  ];

  const edges: Edge[] = [
    {
      id: "e1-2",
      source: "1",
      target: "2",
      animated: true,
      style: { stroke: "#10B981", strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: "#10B981" },
    },
    {
      id: "e1-3",
      source: "1",
      target: "3",
      animated: true,
      style: { stroke: "#F59E0B", strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: "#F59E0B" },
    },
    {
      id: "e1-4",
      source: "1",
      target: "4",
      animated: true,
      style: { stroke: "#FFFFFF", strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: "#FFFFFF" },
    },
    {
      id: "e2-5",
      source: "2",
      target: "5",
      style: { stroke: "#1C1C1E", strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: "#1C1C1E" },
    },
    {
      id: "e3-5",
      source: "3",
      target: "5",
      style: { stroke: "#1C1C1E", strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: "#1C1C1E" },
    },
    {
      id: "e4-5",
      source: "4",
      target: "5",
      style: { stroke: "#1C1C1E", strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: "#1C1C1E" },
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
      className="glass-effect squircle-lg overflow-hidden"
    >
      <div className="p-4 border-b border-border-30">
        <h2 className="text-sm font-semibold">Agent Council Flow</h2>
      </div>
      <div className="h-400 bg-card-30">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          fitView
          attributionPosition="bottom-left"
          proOptions={{ hideAttribution: true }}
        >
          <Background color="#1C1C1E" gap={16} />
          <Controls
            style={{
              background: "#0C0C0E",
              border: "1px solid #1C1C1E",
              borderRadius: "28px",
            }}
          />
        </ReactFlow>
      </div>
    </motion.div>
  );
}
