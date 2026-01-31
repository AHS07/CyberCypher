"""Skeptic Critic Agent - Identifies false positives and semantic matches using Mistral (via Ollama)."""
import logging
from datetime import datetime

from app.models.state import ShadowState
from app.models.schemas import CouncilOpinion
from app.core.llm_manager import llm_manager, with_failover

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are the Skeptic Critic in the Shadow Twin Guardian council.

Your role is to CHALLENGE the Primary Analyzer's findings and look for FALSE POSITIVES.

You will receive:
1. The Primary Analyzer's opinion and detected issues
2. The original diff report
3. Full API responses from both systems

Your responsibilities:
1. Identify "semantic matches" - differences that are functionally equivalent:
   - $100 vs $100.00 (format difference, same value)
   - "true" vs true (string vs boolean, but equivalent)
   - [] vs null (both represent empty/no data)
   - Different timestamps for "created_at" fields (expected to differ)
2. Challenge severity assessments - is this really Critical or just Medium?
3. Find acceptable transformations vs genuine bugs
4. Update the risk score based on your skeptical review
5. List which of the Primary Analyzer's issues are FALSE POSITIVES

Be skeptical and question everything. Your job is to prevent over-alerting.

Return your analysis in the following JSON structure:
{
  "analysis": "Your skeptical review",
  "false_positives": ["issue1 from primary that is actually OK", ...],
  "genuine_issues": ["issues that are real problems"],
  "adjusted_risk_score": 0.0 to 1.0,
  "confidence": 0.0 to 1.0
}
"""


async def skeptic_critic_node(state: ShadowState) -> dict:
    """Skeptic critic node that identifies false positives and semantic matches.
    
    Args:
        state: Current ShadowState from LangGraph
        
    Returns:
        State updates to merge into ShadowState
    """
    logger.info(f"Skeptic Critic starting for test_id: {state['test_id']}")
    
    # Get primary analyzer's opinion
    if not state["council_opinions"]:
        logger.warning("No primary opinion found, skipping skeptic")
        return {}
    
    primary_opinion = state["council_opinions"][0]
    
    # Prepare prompt
    human_prompt = f"""Review the Primary Analyzer's findings:

PRIMARY ANALYZER OPINION:
Analysis: {primary_opinion['analysis']}
Detected Issues: {primary_opinion['detected_issues']}
Risk Score: {primary_opinion['risk_score']}

ORIGINAL DIFF REPORT:
{state['diff_report']}

LEGACY RESPONSE:
{state['legacy_response']}

HEADLESS RESPONSE:
{state['headless_response']}

Apply your skeptical perspective and identify any false positives or acceptable differences."""
    
    # Call LLM with failover (prioritize local Ollama, then fallback to cloud)
    @with_failover(test_id=state["test_id"])
    async def critique(provider: str) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": human_prompt}
        ]
        response = await llm_manager.call_llm(provider, messages, temperature=0.2)
        return response
    
    try:
        result = await critique()
        analysis_text, provider_used = result  # Unpack the tuple returned by with_failover
        
        # Parse response
        import json
        try:
            analysis_json = json.loads(analysis_text)
        except json.JSONDecodeError:
            analysis_json = {
                "analysis": analysis_text,
                "false_positives": [],
                "genuine_issues": primary_opinion['detected_issues'],
                "adjusted_risk_score": primary_opinion['risk_score'],
                "confidence": 0.5,
            }
        
        opinion = CouncilOpinion(
            agent="skeptic_critic",
            provider=provider_used,
            timestamp=datetime.utcnow(),
            analysis=analysis_json.get("analysis", analysis_text),
            detected_issues=analysis_json.get("genuine_issues", []),
            false_positives=analysis_json.get("false_positives", []),
            risk_score=analysis_json.get("adjusted_risk_score", primary_opinion['risk_score']),
            confidence=analysis_json.get("confidence", 0.7),
        )
        
        logger.info(
            f"Skeptic Critic completed. Found {len(opinion.false_positives)} false positives. "
            f"Adjusted risk: {opinion.risk_score}"
        )
        
        return {
            "council_opinions": [opinion.model_dump()],
            "active_provider": provider_used,
            "providers_attempted": [provider_used],
        }
        
    except Exception as e:
        logger.error(f"Skeptic Critic failed: {e}")
        return {
            "status": "failed",
            "error_message": f"Skeptic Critic failed: {str(e)}",
        }
