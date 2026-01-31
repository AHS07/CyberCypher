"""Primary Analyzer Agent - Deep-dive JSON diff analysis using Claude-3.5-Sonnet."""
import logging
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage

from app.models.state import ShadowState
from app.models.schemas import CouncilOpinion
from app.core.llm_manager import llm_manager, with_failover

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are the Primary Analyzer in the Shadow Twin Guardian council.

Your role is to perform the FIRST deep-dive analysis of JSON diff reports from e-commerce migration parity testing.

You will receive:
1. A DeepDiff report showing differences between Legacy and Headless API responses
2. The full Legacy API response (original system)
3. The full Headless API response (new system)

Your responsibilities:
1. Identify ALL significant differences that could impact business logic
2. Categorize differences by severity (Critical, High, Medium, Low)
3. Determine if differences are:
   - Breaking changes (data loss, incorrect values)
   - Acceptable transformations (format changes, null vs empty)
   - Potential bugs in the new system
4. Provide a preliminary risk score (0.0 to 1.0)
5. List specific issues that need investigation

Be thorough and pessimistic - it's better to flag potential issues for the Skeptic to review.

Return your analysis in the following JSON structure:
{
  "analysis": "Detailed analysis text",
  "detected_issues": ["issue1", "issue2", ...],
  "risk_score": 0.0 to 1.0,
  "confidence": 0.0 to 1.0,
  "severity_breakdown": {
    "critical": ["issue"],
    "high": [],
    "medium": [],
    "low": []
  }
}
"""


async def primary_analyzer_node(state: ShadowState) -> dict:
    """Primary analysis node that performs initial deep-dive into diff report.
    
    Args:
        state: Current ShadowState from LangGraph
        
    Returns:
        State updates to merge into ShadowState
    """
    logger.info(f"Primary Analyzer starting for test_id: {state['test_id']}")
    
    # Check if diff is empty
    if not state["diff_report"] or len(state["diff_report"]) == 0:
        logger.info("Empty diff detected, skipping analysis")
        return {
            "council_opinions": [{
                "agent": "primary_analyzer",
                "provider": "skip",
                "timestamp": datetime.utcnow(),
                "analysis": "No differences detected between legacy and headless responses. Test PASSED.",
                "detected_issues": [],
                "false_positives": [],
                "risk_score": 0.0,
                "confidence": 1.0,
            }],
            "status": "complete",
            "final_verdict": "PASS",
            "risk_score": 0.0,
        }
    
    # Prepare prompt
    human_prompt = f"""Analyze the following parity test:

MERCHANT ID: {state['merchant_id']}

DIFF REPORT:
{state['diff_report']}

LEGACY RESPONSE:
{state['legacy_response']}

HEADLESS RESPONSE:
{state['headless_response']}

Provide your detailed analysis following the JSON structure specified in your system prompt."""
    
    # Call LLM with failover
    @with_failover(test_id=state["test_id"])
    async def analyze(provider: str) -> str:
        llm = llm_manager.get_llm(provider, temperature=0.0)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=human_prompt)
        ]
        response = await llm.ainvoke(messages)
        return response.content
    
    try:
        analysis_text, provider_used = await analyze()
        
        # Parse the response (in production, you'd want more robust JSON parsing)
        import json
        try:
            analysis_json = json.loads(analysis_text)
        except json.JSONDecodeError:
            # Fallback if LLM doesn't return valid JSON
            analysis_json = {
                "analysis": analysis_text,
                "detected_issues": ["Failed to parse structured response"],
                "risk_score": 0.5,
                "confidence": 0.5,
            }
        
        opinion = CouncilOpinion(
            agent="primary_analyzer",
            provider=provider_used,
            timestamp=datetime.utcnow(),
            analysis=analysis_json.get("analysis", analysis_text),
            detected_issues=analysis_json.get("detected_issues", []),
            false_positives=[],  # Primary analyzer doesn't identify false positives
            risk_score=analysis_json.get("risk_score", 0.5),
            confidence=analysis_json.get("confidence", 0.8),
        )
        
        logger.info(f"Primary Analyzer completed with risk score: {opinion.risk_score}")
        
        return {
            "council_opinions": [opinion.model_dump()],
            "active_provider": provider_used,
            "providers_attempted": [provider_used],
            "status": "analyzing",
        }
        
    except Exception as e:
        logger.error(f"Primary Analyzer failed: {e}")
        return {
            "status": "failed",
            "error_message": f"Primary Analyzer failed: {str(e)}",
        }
