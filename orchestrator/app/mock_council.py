"""Mock council implementation for demo purposes when Ollama is unavailable."""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MockCouncil:
    """Mock council that provides realistic responses for demo."""
    
    async def analyze_diff(self, test_id: str, merchant_id: str, diff_report: Dict[str, Any], 
                          legacy_response: Dict[str, Any], headless_response: Dict[str, Any]) -> Dict[str, Any]:
        """Run mock council analysis with realistic responses."""
        try:
            logger.info(f"Starting mock council analysis for {test_id}")
            
            # Simulate processing time
            await asyncio.sleep(2)
            
            # Analyze the diff to provide realistic responses
            issues = []
            risk_score = 0.0
            
            if "type_changes" in diff_report:
                issues.append("Type mismatch detected")
                risk_score += 0.3
            
            if "dictionary_item_removed" in diff_report:
                issues.append("Missing fields in headless response")
                risk_score += 0.4
                
            if "values_changed" in diff_report:
                issues.append("Value differences found")
                risk_score += 0.2
            
            # Determine verdict based on risk
            if risk_score < 0.3:
                verdict = "PASS"
                recommendation = "No significant issues detected. Safe to proceed."
            elif risk_score < 0.7:
                verdict = "NEEDS_REVIEW"
                recommendation = "Some issues detected. Manual review recommended before deployment."
            else:
                verdict = "FAIL"
                recommendation = "Critical issues found. Do not deploy until resolved."
            
            # Create realistic council opinions
            primary_opinion = {
                "agent": "primary_analyzer",
                "provider": "deepseek-r1",
                "timestamp": datetime.utcnow().isoformat(),
                "analysis": f"Detected {len(issues)} potential issues in API parity. " + 
                           ("Type changes may break frontend parsing. " if "type_changes" in diff_report else "") +
                           ("Missing fields could cause null pointer exceptions. " if "dictionary_item_removed" in diff_report else "") +
                           ("Value changes need validation for business logic impact." if "values_changed" in diff_report else ""),
                "detected_issues": issues,
                "risk_score": min(risk_score + 0.1, 1.0),  # Primary is more pessimistic
                "confidence": 0.85
            }
            
            # Skeptic reduces some false positives
            skeptic_issues = []
            skeptic_false_positives = []
            
            for issue in issues:
                if "Type mismatch" in issue and self._is_semantic_equivalent(diff_report):
                    skeptic_false_positives.append(issue + " (semantic equivalence)")
                else:
                    skeptic_issues.append(issue)
            
            skeptic_risk = max(risk_score - 0.1, 0.0) if skeptic_false_positives else risk_score
            
            skeptic_opinion = {
                "agent": "skeptic_critic",
                "provider": "mistral",
                "timestamp": datetime.utcnow().isoformat(),
                "analysis": f"Reviewed {len(issues)} issues. Found {len(skeptic_false_positives)} false positives. " +
                           ("Some type changes are semantically equivalent (100 vs '100'). " if skeptic_false_positives else "") +
                           f"Remaining {len(skeptic_issues)} genuine concerns need attention.",
                "detected_issues": skeptic_issues,
                "false_positives": skeptic_false_positives,
                "risk_score": skeptic_risk,
                "confidence": 0.78
            }
            
            # Judge makes final weighted decision
            final_risk = (primary_opinion["risk_score"] * 0.6) + (skeptic_opinion["risk_score"] * 0.4)
            
            if final_risk < 0.3:
                final_verdict = "PASS"
            elif final_risk < 0.7:
                final_verdict = "NEEDS_REVIEW"
            else:
                final_verdict = "FAIL"
            
            judge_opinion = {
                "agent": "consensus_judge",
                "provider": "llama3.2",
                "timestamp": datetime.utcnow().isoformat(),
                "analysis": f"Weighted analysis (Primary: 60%, Skeptic: 40%) yields risk score {final_risk:.2f}. " +
                           f"Verdict: {final_verdict}. " +
                           ("Critical deployment blocker." if final_verdict == "FAIL" else
                            "Requires human oversight." if final_verdict == "NEEDS_REVIEW" else
                            "Safe for automated deployment."),
                "detected_issues": skeptic_issues,
                "risk_score": final_risk,
                "confidence": 0.92,
                "verdict": final_verdict,
                "recommendation": recommendation
            }
            
            return {
                "test_id": test_id,
                "merchant_id": merchant_id,
                "status": "complete",
                "council_opinions": [primary_opinion, skeptic_opinion, judge_opinion],
                "final_verdict": final_verdict,
                "risk_score": final_risk,
                "is_mitigated": False,
                "mitigation_recommendation": recommendation,
                "active_provider": "mock_council",
                "providers_attempted": ["deepseek-r1", "mistral", "llama3.2"]
            }
            
        except Exception as e:
            logger.error(f"Mock council analysis failed: {e}")
            return {
                "test_id": test_id,
                "merchant_id": merchant_id,
                "status": "failed",
                "error_message": str(e),
                "is_mitigated": False,
                "active_provider": "mock_council"
            }
    
    def _is_semantic_equivalent(self, diff_report):
        """Check if type changes are semantically equivalent."""
        if "type_changes" not in diff_report:
            return False
        
        for path, change in diff_report["type_changes"].items():
            old_val = change.get("old_value")
            new_val = change.get("new_value")
            
            # Check if numeric values are equivalent
            try:
                if float(old_val) == float(new_val):
                    return True
            except (ValueError, TypeError):
                pass
        
        return False


# Global instance
mock_council = MockCouncil()