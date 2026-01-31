"""Skeptic Critic Agent - Challenges findings and identifies false positives."""
import logging
from typing import Dict, Any, List
from app.core.hf_manager import get_hf_manager

logger = logging.getLogger(__name__)

class SkepticCritic:
    """Agent that challenges primary analysis and identifies false positives."""
    
    def __init__(self):
        self.hf_manager = get_hf_manager()
        self.agent_type = "skeptic_critic"
    
    async def critique(self, test_id: str, primary_analysis: Dict[str, Any], 
                      diff_report: Dict[str, Any], legacy_response: Dict[str, Any], 
                      headless_response: Dict[str, Any]) -> Dict[str, Any]:
        """Challenge the primary analysis and identify false positives."""
        
        # Create critique prompt
        messages = [
            {
                "role": "system",
                "content": """You are a Skeptical Code Reviewer specializing in API compatibility analysis.
Your job is to challenge findings and identify FALSE POSITIVES - differences that look scary but are actually safe.

Look for:
- Semantic equivalence (100 vs "100" - same value, different type but safe)
- Cosmetic changes (case differences that don't break functionality)
- Non-breaking schema evolution (optional fields, backwards compatible changes)
- Over-conservative risk assessments

Be critical but fair. If something is genuinely risky, acknowledge it. If it's a false alarm, call it out.

Respond in JSON format:
{
    "critique": "your skeptical analysis",
    "false_positives": ["list of issues that are actually safe"],
    "genuine_concerns": ["list of real issues that remain"],
    "risk_adjustment": -0.3 to +0.2,
    "confidence": 0.0-1.0,
    "recommendation": "your final recommendation"
}"""
            },
            {
                "role": "user",
                "content": f"""Review this primary analysis for false positives:

Test ID: {test_id}

Primary Analyst found:
- Issues: {primary_analysis.get('detected_issues', [])}
- Risk Score: {primary_analysis.get('risk_score', 0)}
- Analysis: {primary_analysis.get('analysis', '')}

Raw Data:
- Legacy: {legacy_response}
- Headless: {headless_response}
- Diffs: {diff_report}

Are any of these "issues" actually false positives? What's your skeptical take?"""
            }
        ]
        
        # Get healthy model for this agent
        model_name = await self.hf_manager.get_healthy_model(self.agent_type)
        if not model_name:
            logger.error("No healthy models available for skeptic critic")
            return self._fallback_critique(primary_analysis, diff_report)
        
        # Call the model
        result = await self.hf_manager.call_model(
            model_name=model_name,
            messages=messages,
            max_tokens=512,
            temperature=0.4  # Slightly higher temperature for creative skepticism
        )
        
        if not result:
            logger.warning("Skeptic critic model call failed, using fallback")
            return self._fallback_critique(primary_analysis, diff_report)
        
        # Parse the response
        try:
            response_text = result["content"]
            
            # Try to extract JSON
            import json
            import re
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                critique_data = json.loads(json_match.group())
            else:
                critique_data = self._parse_text_critique(response_text, primary_analysis, diff_report)
            
            return {
                "agent": "skeptic_critic",
                "model": model_name,
                "timestamp": result["timestamp"],
                "critique": critique_data.get("critique", response_text),
                "false_positives": critique_data.get("false_positives", []),
                "genuine_concerns": critique_data.get("genuine_concerns", []),
                "risk_adjustment": float(critique_data.get("risk_adjustment", 0.0)),
                "confidence": float(critique_data.get("confidence", 0.75)),
                "recommendation": critique_data.get("recommendation", "Proceed with caution"),
                "raw_response": response_text
            }
            
        except Exception as e:
            logger.error(f"Error parsing skeptic critic response: {e}")
            return self._fallback_critique(primary_analysis, diff_report, result.get("content", ""))
    
    def _fallback_critique(self, primary_analysis: Dict[str, Any], diff_report: Dict[str, Any], 
                          raw_response: str = "") -> Dict[str, Any]:
        """Fallback critique when LLM fails."""
        false_positives = []
        genuine_concerns = []
        risk_adjustment = 0.0
        
        primary_issues = primary_analysis.get("detected_issues", [])
        
        # Check for semantic equivalence in type changes
        if "type_changes" in diff_report:
            type_changes = diff_report["type_changes"]
            for path, change in type_changes.items():
                old_val = change.get("old_value")
                new_val = change.get("new_value")
                
                # Check if values are semantically equivalent
                if self._is_semantically_equivalent(old_val, new_val):
                    false_positives.append(f"Type change at {path} is semantically equivalent ({old_val} ≈ {new_val})")
                    risk_adjustment -= 0.2
                else:
                    genuine_concerns.append(f"Type change at {path} may break parsing")
        
        # Check for case-only changes (often safe)
        if "values_changed" in diff_report:
            values_changed = diff_report["values_changed"]
            for path, change in values_changed.items():
                old_val = change.get("old_value", "")
                new_val = change.get("new_value", "")
                
                if isinstance(old_val, str) and isinstance(new_val, str):
                    if old_val.lower() == new_val.lower():
                        false_positives.append(f"Case-only change at {path} is likely safe")
                        risk_adjustment -= 0.1
                    else:
                        genuine_concerns.append(f"Value change at {path} may affect business logic")
        
        # Missing fields are usually genuine concerns
        if "dictionary_item_removed" in diff_report:
            for item in diff_report["dictionary_item_removed"]:
                genuine_concerns.append(f"Missing field {item} is a genuine concern")
        
        return {
            "agent": "skeptic_critic",
            "model": "fallback_rules",
            "timestamp": "fallback",
            "critique": f"Fallback critique identified {len(false_positives)} false positives and {len(genuine_concerns)} genuine concerns. " + (raw_response[:200] if raw_response else ""),
            "false_positives": false_positives,
            "genuine_concerns": genuine_concerns,
            "risk_adjustment": risk_adjustment,
            "confidence": 0.7,
            "recommendation": "Manual review recommended due to mixed findings",
            "raw_response": raw_response
        }
    
    def _parse_text_critique(self, text: str, primary_analysis: Dict[str, Any], 
                           diff_report: Dict[str, Any]) -> Dict[str, Any]:
        """Parse non-JSON text response."""
        false_positives = []
        genuine_concerns = []
        risk_adjustment = 0.0
        
        text_lower = text.lower()
        
        # Look for skeptical language
        if "false positive" in text_lower or "not a real issue" in text_lower:
            false_positives.append("Analyst identified potential false positive")
            risk_adjustment -= 0.2
        
        if "semantic" in text_lower and "equivalent" in text_lower:
            false_positives.append("Semantic equivalence noted")
            risk_adjustment -= 0.15
        
        if "genuine" in text_lower or "real concern" in text_lower:
            genuine_concerns.append("Genuine concern identified")
        
        if "overreact" in text_lower or "too conservative" in text_lower:
            risk_adjustment -= 0.1
        
        return {
            "critique": text[:300],
            "false_positives": false_positives,
            "genuine_concerns": genuine_concerns,
            "risk_adjustment": risk_adjustment,
            "confidence": 0.6,
            "recommendation": "Mixed assessment - requires human judgment"
        }
    
    def _is_semantically_equivalent(self, old_val: Any, new_val: Any) -> bool:
        """Check if two values are semantically equivalent."""
        try:
            # Numeric equivalence
            if isinstance(old_val, (int, float)) and isinstance(new_val, str):
                return abs(float(old_val) - float(new_val)) < 0.001
            if isinstance(old_val, str) and isinstance(new_val, (int, float)):
                return abs(float(old_val) - float(new_val)) < 0.001
            
            # String case equivalence
            if isinstance(old_val, str) and isinstance(new_val, str):
                return old_val.lower().strip() == new_val.lower().strip()
            
            return False
        except (ValueError, TypeError):
            return False