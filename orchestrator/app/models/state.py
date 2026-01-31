"""ShadowState TypedDict for LangGraph state management."""
from typing import TypedDict, Annotated, Any
from typing_extensions import TypedDict as ExtTypedDict
import operator


class ShadowState(TypedDict):
    """State definition for Shadow Twin Guardian council deliberation.
    
    This state is passed between nodes in the LangGraph and persisted
    at each super-step to enable fault tolerance and replay.
    """
    
    # Test identification
    test_id: str
    merchant_id: str
    
    # Input data
    diff_report: dict[str, Any]  # JSON diff from DeepDiff
    legacy_response: dict[str, Any]  # Original legacy API response
    headless_response: dict[str, Any]  # New headless API response
    
    # Council opinions (accumulated using operator.add)
    council_opinions: Annotated[list[dict[str, Any]], operator.add]
    
    # Execution tracking
    active_provider: str  # Current LLM provider being used
    providers_attempted: Annotated[list[str], operator.add]  # Track all providers tried
    
    # Results
    is_mitigated: bool
    risk_score: float  # 0.0 to 1.0
    final_verdict: str  # "PASS", "FAIL", "NEEDS_REVIEW"
    mitigation_recommendation: str
    
    # Metadata
    status: str  # "pending", "analyzing", "complete", "failed"
    error_message: str | None
