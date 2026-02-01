"""Consensus Judge Agent - Makes final weighted decisions based on council input."""
import logging
from typing import Dict, Any, List
from datetime import datetime
from app.core.hf_manager import get_hf_manager

logger = logging.getLogger(__name__)

class ConsensusJudge:
    """Agent that makes final decisions by weighing primary analysis and skeptic critique."""
    
    def __init__(self):
        self.hf_manager = get_hf_manager()
        self.agent_type = "consensus_judge"
    
    async def judge(self, test_id: str, merchant_id: str, primary_analysis: Dict[str, Any], 
                   skeptic_critique: Dict[str, Any], diff_report: Dict[str, Any]) -> Dict[str, Any]:
        """Make final weighted decision based on council deliberation."""
        
        # Create judgment prompt
        messages = [
            {
                "role": "system",
                "content": """You are a Senior Engineering Manager making final deployment decisions for e-commerce API migrations.

You have two expert opinions:
1. PRIMARY ANALYST: Technical expert who identifies potential issues
2. SKEPTIC CRITIC: Experienced reviewer who challenges findings and spots false positives

Your job is to weigh both perspectives and make a final decision:
- PASS: Safe to deploy (risk < 0.3)
- NEEDS_REVIEW: Requires human oversight (risk 0.3-0.7)  
- FAIL: Do not deploy (risk > 0.7)

Consider:
- Business impact vs technical risk
- False positive likelihood
- Merchant experience impact
- Rollback complexity

Respond in JSON format:
{
    "final_analysis": "your weighted decision reasoning",
    "verdict": "PASS|NEEDS_REVIEW|FAIL",
    "final_risk_score": 0.0-1.0,
    "confidence": 0.0-1.0,
    "recommendation": "specific action to take",
    "key_factors": ["main decision factors"]
}"""
            },
            {
                "role": "user",
                "content": f"""Make final deployment decision for:

Test ID: {test_id}
Merchant: {merchant_id}

PRIMARY ANALYST SAYS:
- Risk Score: {primary_analysis.get('risk_score', 0)}
- Issues: {primary_analysis.get('detected_issues', [])}
- Analysis: {primary_analysis.get('analysis', '')}

SKEPTIC CRITIC SAYS:
- Risk Adjustment: {skeptic_critique.get('risk_adjustment', 0)}
- False Positives: {skeptic_critique.get('false_positives', [])}
- Genuine Concerns: {skeptic_critique.get('genuine_concerns', [])}
- Critique: {skeptic_critique.get('critique', '')}

Raw Differences: {diff_report}

What's your final verdict? Should we deploy this headless API version?"""
            }
        ]
        
        # Get healthy model for this agent
        model_name = await self.hf_manager.get_healthy_model(self.agent_type)
        if not model_name:
            logger.error("No healthy models available for consensus judge")
            return self._fallback_judgment(primary_analysis, skeptic_critique)
        
        # Call the model
        result = await self.hf_manager.call_model(
            model_name=model_name,
            messages=messages,
            max_tokens=512,
            temperature=0.2  # Low temperature for consistent decisions
        )
        
        if not result:
            logger.warning("Consensus judge model call failed, using fallback")
            return self._fallback_judgment(primary_analysis, skeptic_critique)
        
        # Parse the response
        try:
            response_text = result["content"]
            
            # Try to extract JSON
            import json
            import re
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                judgment_data = json.loads(json_match.group())
            else:
                judgment_data = self._parse_text_judgment(response_text, primary_analysis, skeptic_critique)
            
            # Validate verdict
            verdict = judgment_data.get("verdict", "NEEDS_REVIEW")
            if verdict not in ["PASS", "NEEDS_REVIEW", "FAIL"]:
                verdict = "NEEDS_REVIEW"
            
            return {
                "agent": "consensus_judge",
                "provider": "huggingface",
                "model": model_name,
                "timestamp": result["timestamp"],
                "analysis": judgment_data.get("final_analysis", response_text),
                "detected_issues": [],
                "false_positives": [],
                "verdict": verdict,
                "final_risk_score": float(judgment_data.get("final_risk_score", 0.5)),
                "risk_score": float(judgment_data.get("final_risk_score", 0.5)),
                "confidence": float(judgment_data.get("confidence", 0.8)),
                "recommendation": judgment_data.get("recommendation", "Proceed with caution"),
                "key_factors": judgment_data.get("key_factors", []),
                "raw_response": response_text
            }
            
        except Exception as e:
            logger.error(f"Error parsing consensus judge response: {e}")
            return self._fallback_judgment(primary_analysis, skeptic_critique, result.get("content", ""))
    
    def _fallback_judgment(self, primary_analysis: Dict[str, Any], skeptic_critique: Dict[str, Any], 
                          raw_response: str = "") -> Dict[str, Any]:
        """Fallback judgment when LLM fails."""
        
        # Calculate weighted risk score
        primary_risk = primary_analysis.get("risk_score", 0.5)
        skeptic_risk = skeptic_critique.get("risk_score", primary_risk)
        
        # Weight: Primary 60%, Skeptic 40%
        final_risk = (primary_risk * 0.6) + (skeptic_risk * 0.4)
        final_risk = max(0.0, min(1.0, final_risk))
        
        # Determine verdict based on risk thresholds
        if final_risk < 0.3:
            verdict = "PASS"
            recommendation = "Safe to deploy - low risk detected"
        elif final_risk < 0.7:
            verdict = "NEEDS_REVIEW"
            recommendation = "Manual review recommended - moderate risk"
        else:
            verdict = "FAIL"
            recommendation = "Do not deploy - high risk detected"
        
        # Key factors
        key_factors = []
        if primary_analysis.get("detected_issues"):
            key_factors.append(f"Primary found {len(primary_analysis['detected_issues'])} issues")
        if skeptic_critique.get("false_positives"):
            key_factors.append(f"Skeptic identified {len(skeptic_critique['false_positives'])} false positives")
        if skeptic_critique.get("genuine_concerns"):
            key_factors.append(f"Skeptic confirmed {len(skeptic_critique['genuine_concerns'])} genuine concerns")
        
        return {
            "agent": "consensus_judge",
            "provider": "huggingface_fallback",
            "model": "fallback_weighted",
            "timestamp": datetime.utcnow().isoformat(),
            "analysis": f"Weighted analysis: Primary risk {primary_risk:.2f}, Skeptic risk {skeptic_risk:.2f}, Final risk {final_risk:.2f}. " + (raw_response[:200] if raw_response else ""),
            "detected_issues": [],
            "false_positives": [],
            "verdict": verdict,
            "final_risk_score": final_risk,
            "risk_score": final_risk,
            "confidence": 0.75,
            "recommendation": recommendation,
            "key_factors": key_factors,
            "raw_response": raw_response
        }
    
    def _parse_text_judgment(self, text: str, primary_analysis: Dict[str, Any], 
                           skeptic_critique: Dict[str, Any]) -> Dict[str, Any]:
        """Parse non-JSON text response."""
        
        text_lower = text.lower()
        
        # Determine verdict from text
        if "pass" in text_lower and ("safe" in text_lower or "deploy" in text_lower):
            verdict = "PASS"
            risk_score = 0.2
        elif "fail" in text_lower or "do not deploy" in text_lower or "block" in text_lower:
            verdict = "FAIL"
            risk_score = 0.8
        else:
            verdict = "NEEDS_REVIEW"
            risk_score = 0.5
        
        # Extract key factors
        key_factors = []
        if "false positive" in text_lower:
            key_factors.append("False positives identified")
        if "genuine concern" in text_lower:
            key_factors.append("Genuine concerns remain")
        if "business impact" in text_lower:
            key_factors.append("Business impact considered")
        
        return {
            "final_analysis": text[:300],
            "verdict": verdict,
            "final_risk_score": risk_score,
            "confidence": 0.6,
            "recommendation": f"Based on text analysis: {verdict}",
            "key_factors": key_factors
        }