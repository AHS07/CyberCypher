"""Simple council implementation without LangGraph for debugging."""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any

import ollama

logger = logging.getLogger(__name__)


class SimpleCouncil:
    """Simplified council that calls Ollama directly."""
    
    def __init__(self):
        self.models = {
            "primary": "deepseek-r1:latest",
            "skeptic": "mistral:latest", 
            "judge": "llama3.2:3b"
        }
    
    async def analyze_diff(self, test_id: str, merchant_id: str, diff_report: Dict[str, Any], 
                          legacy_response: Dict[str, Any], headless_response: Dict[str, Any]) -> Dict[str, Any]:
        """Run simplified council analysis."""
        try:
            logger.info(f"Starting simple council analysis for {test_id}")
            
            # Step 1: Primary Analysis
            primary_result = await self._call_primary_analyzer(diff_report, legacy_response, headless_response)
            
            # Step 2: Skeptic Review
            skeptic_result = await self._call_skeptic_critic(primary_result, diff_report)
            
            # Step 3: Final Judgment
            final_result = await self._call_consensus_judge(primary_result, skeptic_result)
            
            return {
                "test_id": test_id,
                "merchant_id": merchant_id,
                "status": "complete",
                "council_opinions": [primary_result, skeptic_result, final_result],
                "final_verdict": final_result.get("verdict", "NEEDS_REVIEW"),
                "risk_score": final_result.get("risk_score", 0.5),
                "is_mitigated": False,
                "mitigation_recommendation": final_result.get("recommendation", "Review manually"),
                "active_provider": "ollama_direct"
            }
            
        except Exception as e:
            logger.error(f"Simple council analysis failed: {e}")
            return {
                "test_id": test_id,
                "status": "failed",
                "error_message": str(e),
                "is_mitigated": False
            }
    
    async def _call_primary_analyzer(self, diff_report, legacy_response, headless_response):
        """Call primary analyzer."""
        prompt = f"""You are analyzing API differences for e-commerce migration.

DIFF REPORT: {json.dumps(diff_report, indent=2)}
LEGACY: {json.dumps(legacy_response, indent=2)}
HEADLESS: {json.dumps(headless_response, indent=2)}

Analyze the differences and respond with JSON:
{{"analysis": "your analysis", "issues": ["list of issues"], "risk_score": 0.0-1.0}}"""

        try:
            response = await asyncio.to_thread(
                ollama.generate,
                model=self.models["primary"],
                prompt=prompt,
                options={"temperature": 0.0}
            )
            
            # Try to parse JSON, fallback to simple response
            try:
                result = json.loads(response["response"])
            except:
                result = {
                    "analysis": response["response"][:200],
                    "issues": ["Failed to parse structured response"],
                    "risk_score": 0.5
                }
            
            return {
                "agent": "primary_analyzer",
                "provider": "deepseek-r1",
                "timestamp": datetime.utcnow().isoformat(),
                "analysis": result.get("analysis", ""),
                "detected_issues": result.get("issues", []),
                "risk_score": result.get("risk_score", 0.5),
                "confidence": 0.8
            }
            
        except Exception as e:
            logger.error(f"Primary analyzer failed: {e}")
            return {
                "agent": "primary_analyzer",
                "provider": "deepseek-r1",
                "analysis": f"Analysis failed: {e}",
                "detected_issues": ["LLM call failed"],
                "risk_score": 0.5,
                "confidence": 0.1
            }
    
    async def _call_skeptic_critic(self, primary_result, diff_report):
        """Call skeptic critic."""
        prompt = f"""Review this primary analysis for false positives:

PRIMARY ANALYSIS: {primary_result['analysis']}
DETECTED ISSUES: {primary_result['detected_issues']}
ORIGINAL DIFF: {json.dumps(diff_report, indent=2)}

Are any of these issues actually acceptable? Respond with JSON:
{{"analysis": "your review", "false_positives": ["list"], "real_issues": ["list"], "adjusted_risk": 0.0-1.0}}"""

        try:
            response = await asyncio.to_thread(
                ollama.generate,
                model=self.models["skeptic"],
                prompt=prompt,
                options={"temperature": 0.2}
            )
            
            try:
                result = json.loads(response["response"])
            except:
                result = {
                    "analysis": response["response"][:200],
                    "false_positives": [],
                    "real_issues": primary_result["detected_issues"],
                    "adjusted_risk": primary_result["risk_score"]
                }
            
            return {
                "agent": "skeptic_critic",
                "provider": "mistral",
                "timestamp": datetime.utcnow().isoformat(),
                "analysis": result.get("analysis", ""),
                "detected_issues": result.get("real_issues", []),
                "false_positives": result.get("false_positives", []),
                "risk_score": result.get("adjusted_risk", primary_result["risk_score"]),
                "confidence": 0.7
            }
            
        except Exception as e:
            logger.error(f"Skeptic critic failed: {e}")
            return {
                "agent": "skeptic_critic",
                "provider": "mistral",
                "analysis": f"Review failed: {e}",
                "detected_issues": primary_result["detected_issues"],
                "risk_score": primary_result["risk_score"],
                "confidence": 0.1
            }
    
    async def _call_consensus_judge(self, primary_result, skeptic_result):
        """Call consensus judge."""
        prompt = f"""Make final verdict based on these analyses:

PRIMARY (weight 0.6): Risk {primary_result['risk_score']}, Issues: {primary_result['detected_issues']}
SKEPTIC (weight 0.4): Risk {skeptic_result['risk_score']}, Issues: {skeptic_result['detected_issues']}

Calculate weighted risk and assign verdict:
- PASS: risk < 0.3
- NEEDS_REVIEW: 0.3 <= risk < 0.7  
- FAIL: risk >= 0.7

Respond with JSON:
{{"verdict": "PASS/NEEDS_REVIEW/FAIL", "risk_score": 0.0-1.0, "recommendation": "action to take"}}"""

        try:
            response = await asyncio.to_thread(
                ollama.generate,
                model=self.models["judge"],
                prompt=prompt,
                options={"temperature": 0.1}
            )
            
            try:
                result = json.loads(response["response"])
            except:
                # Fallback calculation
                weighted_risk = (primary_result["risk_score"] * 0.6) + (skeptic_result["risk_score"] * 0.4)
                if weighted_risk < 0.3:
                    verdict = "PASS"
                elif weighted_risk < 0.7:
                    verdict = "NEEDS_REVIEW"
                else:
                    verdict = "FAIL"
                
                result = {
                    "verdict": verdict,
                    "risk_score": weighted_risk,
                    "recommendation": f"Weighted risk: {weighted_risk:.2f}"
                }
            
            return {
                "agent": "consensus_judge",
                "provider": "llama3.2",
                "timestamp": datetime.utcnow().isoformat(),
                "analysis": f"Final verdict: {result.get('verdict')}",
                "detected_issues": skeptic_result["detected_issues"],
                "risk_score": result.get("risk_score", 0.5),
                "confidence": 0.9,
                "verdict": result.get("verdict", "NEEDS_REVIEW"),
                "recommendation": result.get("recommendation", "Manual review required")
            }
            
        except Exception as e:
            logger.error(f"Consensus judge failed: {e}")
            weighted_risk = (primary_result["risk_score"] * 0.6) + (skeptic_result["risk_score"] * 0.4)
            return {
                "agent": "consensus_judge",
                "provider": "llama3.2",
                "analysis": f"Judgment failed: {e}",
                "detected_issues": skeptic_result["detected_issues"],
                "risk_score": weighted_risk,
                "confidence": 0.1,
                "verdict": "NEEDS_REVIEW",
                "recommendation": "Manual review due to system error"
            }


# Global instance
simple_council = SimpleCouncil()