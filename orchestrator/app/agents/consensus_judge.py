"""Consensus Judge Agent - Weighted vote fusion using Llama-3.2 (via Ollama)."""
import logging
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage

from app.models.state import ShadowState
from app.models.schemas import CouncilOpinion
from app.core.llm_manager import llm_manager, with_failover

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are the Consensus Judge in the Shadow Twin Guardian council.

Your role is to SYNTHESIZE opinions from the Primary Analyzer and Skeptic Critic into a FINAL VERDICT.

You will receive:
1. Primary Analyzer's opinion (pessimistic, thorough)
2. Skeptic Critic's review (identifies false positives)
3. Original diff report and API responses

Your responsibilities:
1. Weigh both opinions:
   - Primary Analyzer weight: 0.6 (thorough initial analysis)
   - Skeptic Critic weight: 0.4 (false positive filtering)
2. Calculate final risk score using weighted average
3assign final verdict:
   - PASS: risk_score < 0.3 (no significant issues)
   - NEEDS_REVIEW: 0.3 <= risk_score < 0.7 (some concerns, human review recommended)
   - FAIL: risk_score >= 0.7 (critical issues detected)
4. Provide actionable mitigation recommendations
5. Justify your decision with clear reasoning

Be balanced and decisive. Your verdict determines whether human intervention is needed.

Return your analysis in the following JSON structure:
{
  "analysis": "Your synthesis and reasoning",
  "final_verdict": "PASS" | "NEEDS_REVIEW" | "FAIL",
  "final_risk_score": 0.0 to 1.0,
  "confidence": 0.0 to 1.0,
  "mitigation_recommendation": "Specific actions to take",
  "key_issues": ["Critical issues that require attention"]
}
"""


async def consensus_judge_node(state: ShadowState) -> dict:
    """Consensus judge node that synthesizes council opinions into final verdict.
    
    Args:
        state: Current ShadowState from LangGraph
        
    Returns:
        State updates to merge into ShadowState
    """
    logger.info(f"Consensus Judge starting for test_id: {state['test_id']}")
    
    # Need at least 2 opinions (primary + skeptic)
    if len(state["council_opinions"]) < 2:
        logger.warning(f"Insufficient opinions ({len(state['council_opinions'])}), cannot reach consensus")
        return {
            "status": "failed",
            "error_message": "Insufficient council opinions for consensus",
        }
    
    primary_opinion = state["council_opinions"][0]
    skeptic_opinion = state["council_opinions"][1]
    
    # Prepare prompt
    human_prompt = f"""Synthesize the following council deliberation:

PRIMARY ANALYZER:
- Risk Score: {primary_opinion['risk_score']}
- Detected Issues: {primary_opinion['detected_issues']}
- Analysis: {primary_opinion['analysis']}

SKEPTIC CRITIC:
- Adjusted Risk Score: {skeptic_opinion['risk_score']}
- False Positives Identified: {skeptic_opinion.get('false_positives', [])}
- Genuine Issues: {skeptic_opinion['detected_issues']}
- Analysis: {skeptic_opinion['analysis']}

CONTEXT:
Merchant: {state['merchant_id']}
Test ID: {state['test_id']}

Provide your final consensus verdict following the weighted voting rules in your system prompt."""
    
    # Call LLM with failover
    @with_failover(test_id=state["test_id"])
    async def judge(provider: str) -> str:
        llm = llm_manager.get_llm(provider, temperature=0.1)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=human_prompt)
        ]
        response = await llm.ainvoke(messages)
        return response.content
    
    try:
        result = await judge()
        analysis_text, provider_used = result  # Unpack the tuple returned by with_failover
        
        # Parse response
        import json
        try:
            analysis_json = json.loads(analysis_text)
        except json.JSONDecodeError:
            # Fallback: calculate weighted average ourselves
            weighted_risk = (
                primary_opinion['risk_score'] * 0.6 + 
                skeptic_opinion['risk_score'] * 0.4
            )
            
            if weighted_risk < 0.3:
                verdict = "PASS"
            elif weighted_risk < 0.7:
                verdict = "NEEDS_REVIEW"
            else:
                verdict = "FAIL"
            
            analysis_json = {
                "analysis": analysis_text,
                "final_verdict": verdict,
                "final_risk_score": weighted_risk,
                "confidence": 0.6,
                "mitigation_recommendation": "Review flagged issues manually",
                "key_issues": skeptic_opinion['detected_issues'],
            }
        
        opinion = CouncilOpinion(
            agent="consensus_judge",
            provider=provider_used,
            timestamp=datetime.utcnow(),
            analysis=analysis_json.get("analysis", analysis_text),
            detected_issues=analysis_json.get("key_issues", []),
            false_positives=[],
            risk_score=analysis_json.get("final_risk_score", 0.5),
            confidence=analysis_json.get("confidence", 0.8),
        )
        
        final_verdict = analysis_json.get("final_verdict", "NEEDS_REVIEW")
        mitigation_rec = analysis_json.get("mitigation_recommendation", "No recommendation provided")
        
        logger.info(
            f"Consensus Judge reached verdict: {final_verdict} "
            f"(risk: {opinion.risk_score:.2f})"
        )
        
        return {
            "council_opinions": [opinion.model_dump()],
            "active_provider": provider_used,
            "providers_attempted": [provider_used],
            "final_verdict": final_verdict,
            "risk_score": opinion.risk_score,
            "mitigation_recommendation": mitigation_rec,
            "status": "complete",
            "is_mitigated": False,  # Requires human action if NEEDS_REVIEW or FAIL
        }
        
    except Exception as e:
        logger.error(f"Consensus Judge failed: {e}")
        return {
            "status": "failed",
            "error_message": f"Consensus Judge failed: {str(e)}",
        }
