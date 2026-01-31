"""LangGraph StateGraph definition for the Shadow Twin Guardian council."""
import logging
from typing import Literal

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig

from app.models.state import ShadowState
from app.agents.primary_analyzer import primary_analyzer_node
from app.agents.skeptic_critic import skeptic_critic_node
from app.agents.consensus_judge import consensus_judge_node
from app.db.checkpointer import SupabaseCheckpointer

logger = logging.getLogger(__name__)


def should_continue(state: ShadowState) -> Literal["skeptic", "end"]:
    """Conditional edge to determine if we should continue to skeptic or end early.
    
    Args:
        state: Current state
        
    Returns:
        Next node name or "end"
    """
    # If empty diff was detected, primary analyzer set status to "complete"
    if state.get("status") == "complete":
        logger.info("Empty diff detected, skipping remaining council")
        return "end"
    
    # If primary analyzer failed, end
    if state.get("status") == "failed":
        logger.error("Primary analyzer failed, ending graph")
        return "end"
    
    # Continue to skeptic
    return "skeptic"


def create_council_graph() -> StateGraph:
    """Create the LangGraph StateGraph for council deliberation.
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Initialize graph with ShadowState
    workflow = StateGraph(ShadowState)
    
    # Add nodes
    workflow.add_node("primary", primary_analyzer_node)
    workflow.add_node("skeptic", skeptic_critic_node)
    workflow.add_node("judge", consensus_judge_node)
    
    # Set entry point
    workflow.set_entry_point("primary")
    
    # Add edges
    # Primary -> conditional (either skeptic or end)
    workflow.add_conditional_edges(
        "primary",
        should_continue,
        {
            "skeptic": "skeptic",
            "end": END,
        }
    )
    
    # Skeptic -> Judge
    workflow.add_edge("skeptic", "judge")
    
    # Judge -> END
    workflow.add_edge("judge", END)
    
    # Compile with checkpointer
    checkpointer = SupabaseCheckpointer()
    compiled_graph = workflow.compile(checkpointer=checkpointer)
    
    logger.info("Council graph compiled successfully")
    
    return compiled_graph


# Global graph instance
council_graph = create_council_graph()


async def run_council_analysis(
    test_id: str,
    merchant_id: str,
    legacy_response: dict,
    headless_response: dict,
    diff_report: dict,
) -> ShadowState:
    """Execute the council graph for a test.
    
    Args:
        test_id: Unique test identifier
        merchant_id: Merchant identifier
        legacy_response: Legacy API response
        headless_response: Headless API response
        diff_report: DeepDiff report
        
    Returns:
        Final ShadowState after council deliberation
    """
    logger.info(f"Starting council analysis for test {test_id}")
    
    # Initialize state
    initial_state: ShadowState = {
        "test_id": test_id,
        "merchant_id": merchant_id,
        "diff_report": diff_report,
        "legacy_response": legacy_response,
        "headless_response": headless_response,
        "council_opinions": [],
        "active_provider": "",
        "providers_attempted": [],
        "is_mitigated": False,
        "risk_score": 0.0,
        "final_verdict": "",
        "mitigation_recommendation": "",
        "status": "pending",
        "error_message": None,
    }
    
    # Run graph with thread_id for checkpointing
    config = RunnableConfig(
        configurable={"thread_id": test_id}
    )
    
    try:
        # Invoke graph
        final_state = await council_graph.ainvoke(initial_state, config)
        
        logger.info(f"Council analysis completed for test {test_id}")
        return final_state
        
    except Exception as e:
        logger.error(f"Council analysis failed for test {test_id}: {e}")
        raise
