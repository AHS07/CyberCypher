"use client";

import { useCallback, useEffect, useState } from "react";
import ReactFlow, {
    Node,
    Edge,
    Background,
    Controls,
    MiniMap,
    useNodesState,
    useEdgesState,
    MarkerType,
} from "reactflow";
import "reactflow/dist/style.css";
import { ShadowTest } from "@/lib/types";

interface Props {
    test?: ShadowTest;
}

export function AgentTrace({ test }: Props) {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);

    useEffect(() => {
        if (!test) {
            // Default graph structure
            const defaultNodes: Node[] = [
                {
                    id: "start",
                    type: "input",
                    data: { label: "Start" },
                    position: { x: 0, y: 150 },
                    style: {
                        background: "hsl(217, 91%, 60%)",
                        color: "white",
                        border: "2px solid hsl(217, 91%, 50%)",
                        borderRadius: "8px",
                    },
                },
                {
                    id: "primary",
                    data: { label: "Primary Analyzer\n(Claude)" },
                    position: { x: 200, y: 150 },
                    style: {
                        background: "hsl(222, 47%, 15%)",
                        color: "hsl(213, 31%, 91%)",
                        border: "2px solid hsl(223, 23%, 23%)",
                        borderRadius: "8px",
                        padding: "12px",
                    },
                },
                {
                    id: "skeptic",
                    data: { label: "Skeptic Critic\n(Llama)" },
                    position: { x: 400, y: 150 },
                    style: {
                        background: "hsl(222, 47%, 15%)",
                        color: "hsl(213, 31%, 91%)",
                        border: "2px solid hsl(223, 23%, 23%)",
                        borderRadius: "8px",
                        padding: "12px",
                    },
                },
                {
                    id: "judge",
                    data: { label: "Consensus Judge\n(Gemini)" },
                    position: { x: 600, y: 150 },
                    style: {
                        background: "hsl(222, 47%, 15%)",
                        color: "hsl(213, 31%, 91%)",
                        border: "2px solid hsl(223, 23%, 23%)",
                        borderRadius: "8px",
                        padding: "12px",
                    },
                },
                {
                    id: "end",
                    type: "output",
                    data: { label: "Complete" },
                    position: { x: 800, y: 150 },
                    style: {
                        background: "hsl(142, 71%, 45%)",
                        color: "white",
                        border: "2px solid hsl(142, 71%, 40%)",
                        borderRadius: "8px",
                    },
                },
            ];

            const defaultEdges: Edge[] = [
                {
                    id: "e-start-primary",
                    source: "start",
                    target: "primary",
                    animated: false,
                    markerEnd: { type: MarkerType.ArrowClosed },
                },
                {
                    id: "e-primary-skeptic",
                    source: "primary",
                    target: "skeptic",
                    animated: false,
                    markerEnd: { type: MarkerType.ArrowClosed },
                },
                {
                    id: "e-skeptic-judge",
                    source: "skeptic",
                    target: "judge",
                    animated: false,
                    markerEnd: { type: MarkerType.ArrowClosed },
                },
                {
                    id: "e-judge-end",
                    source: "judge",
                    target: "end",
                    animated: false,
                    markerEnd: { type: MarkerType.ArrowClosed },
                },
            ];

            setNodes(defaultNodes);
            setEdges(defaultEdges);
            return;
        }

        // Update nodes based on test status
        const newNodes: Node[] = [...nodes];
        const opinions = test.council_opinions || [];

        // Highlight active nodes
        if (test.status === "analyzing") {
            const currentStage = opinions.length;

            newNodes.forEach((node) => {
                if (node.id === "primary" && currentStage >= 1) {
                    node.style = {
                        ...node.style,
                        border: "2px solid hsl(142, 71%, 45%)",
                        boxShadow: "0 0 20px rgba(34, 197, 94, 0.3)",
                    };
                }
                if (node.id === "skeptic" && currentStage >= 2) {
                    node.style = {
                        ...node.style,
                        border: "2px solid hsl(142, 71%, 45%)",
                        boxShadow: "0 0 20px rgba(34, 197, 94, 0.3)",
                    };
                }
                if (node.id === "judge" && currentStage >= 3) {
                    node.style = {
                        ...node.style,
                        border: "2px solid hsl(142, 71%, 45%)",
                        boxShadow: "0 0 20px rgba(34, 197, 94, 0.3)",
                    };
                }

                // Pulse current active node
                if (
                    (node.id === "primary" && currentStage === 0) ||
                    (node.id === "skeptic" && currentStage === 1) ||
                    (node.id === "judge" && currentStage === 2)
                ) {
                    node.style = {
                        ...node.style,
                        border: "2px solid hsl(217, 91%, 60%)",
                        boxShadow: "0 0 20px rgba(96, 165, 250, 0.5)",
                        animation: "pulse 2s infinite",
                    };
                }
            });
        }

        setNodes(newNodes);
    }, [test]);

    return (
        <div className="h-full flex flex-col bg-card rounded-lg border border-border overflow-hidden">
            <div className="px-4 py-3 border-b border-border">
                <h2 className="font-semibold text-sm">Agent Trace</h2>
                <p className="text-xs text-muted-foreground mt-1">
                    Live visualization of council deliberation
                </p>
            </div>

            <div className="flex-1">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    fitView
                    className="bg-background"
                >
                    <Background />
                    <Controls />
                    <MiniMap />
                </ReactFlow>
            </div>
        </div>
    );
}
