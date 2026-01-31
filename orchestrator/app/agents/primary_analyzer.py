"""Primary Analyzer Agent - Technical analysis of API differences."""
import logging
from typing import Dict, Any
from app.core.hf_manager import get_hf_manager

logger = logging.getLogger(__name__)

class PrimaryAnalyzer:
    """Agent responsible for technical analysis of API parity differences."""
    
    def __init__(self):
        self.hf_manager = get_hf_manager()
        self.agent_type = "primary_analyzer"
    
    async def analyze(self, test_id: str, merchant_id: str, diff_report: Dict[str, Any], 
                     legacy_response: Dict[str, Any], headless_response: Dict[str, Any]) -> Dict[str, Any]:
        """Perform technical analysis of the API differences."""
        
        # Create analysis prompt
        messages = [
            {
                "role": "system",
                "content": """You are a Senior API Engineer analyzing e-commerce migration parity issues. 
Your job is to identify technical problems that could break the frontend or cause business logic failures.

Focus on:
- Type mismatches that break parsing (float vs string)
- Missing required fields that cause null pointer exceptions  
- Schema changes that break client contracts
- Performance regressions that affect user experience

Respond in JSON format:
{
    "analysis": "detailed technical explanation",
    "detected_issues": ["list of specific issues"],
    "risk_score": 0.0-1.0,
    "confidence": 0.0-1.0,
    "business_impact": "explanation of business consequences"
}"""
            },
            {
                "role": "user", 
                "content": f"""Analyze this API parity test:

Test ID: {test_id}
Merchant: {merchant_id}

Legacy Response: {legacy_response}
Headless Response: {headless_response}

Detected Differences: {diff_report}

What technical issues do you see? What's the risk to the e-commerce platform?"""
            }
        ]
        
        # Get healthy model for this agent
        model_name = await self.hf_manager.get_healthy_model(self.agent_type)
        if not model_name:
            logger.error("No healthy models available for primary analyzer")
            return self._fallback_analysis(diff_report)
        
        # Call the model
        result = await self.hf_manager.call_model(
            model_name=model_name,
            messages=messages,
            max_tokens=512,
            temperature=0.3  # Lower temperature for more focused analysis
        )
        
        if not result:
            logger.warning("Primary analyzer model call failed, using fallback")
            return self._fallback_analysis(diff_report)
        
        # Parse the response
        try:
            # Try to extract JSON from the response
            response_text = result["content"]
            
            # Look for JSON in the response
            import json
            import re
            
            # Try to find JSON block
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group())
            else:
                # Fallback parsing
                analysis_data = self._parse_text_response(response_text, diff_report)
            
            return {
                "agent": "primary_analyzer",
                "model": model_name,
                "timestamp": result["timestamp"],
                "analysis": analysis_data.get("analysis", response_text),
                "detected_issues": analysis_data.get("detected_issues", []),
                "risk_score": float(analysis_data.get("risk_score", 0.5)),
                "confidence": float(analysis_data.get("confidence", 0.8)),
                "business_impact": analysis_data.get("business_impact", "Unknown impact"),
                "raw_response": response_text
            }
            
        except Exception as e:
            logger.error(f"Error parsing primary analyzer response: {e}")
            return self._fallback_analysis(diff_report, result.get("content", ""))
    
    def _fallback_analysis(self, diff_report: Dict[str, Any], raw_response: str = "") -> Dict[str, Any]:
        """Fallback analysis when LLM fails."""
        issues = []
        risk_score = 0.0
        
        if "type_changes" in diff_report:
            issues.append("Type mismatch detected - may break client parsing")
            risk_score += 0.4
        
        if "dictionary_item_removed" in diff_report:
            issues.append("Missing fields in headless response - potential null pointer exceptions")
            risk_score += 0.5
            
        if "values_changed" in diff_report:
            issues.append("Value differences found - may affect business logic")
            risk_score += 0.2
        
        return {
            "agent": "primary_analyzer",
            "model": "fallback_rules",
            "timestamp": "fallback",
            "analysis": f"Fallback analysis detected {len(issues)} issues. " + (raw_response[:200] if raw_response else ""),
            "detected_issues": issues,
            "risk_score": min(risk_score, 1.0),
            "confidence": 0.6,
            "business_impact": "Potential frontend breakage and user experience issues",
            "raw_response": raw_response
        }
    
    def _parse_text_response(self, text: str, diff_report: Dict[str, Any]) -> Dict[str, Any]:
        """Parse non-JSON text response."""
        # Simple text parsing fallback
        issues = []
        risk_score = 0.3  # Default moderate risk
        
        text_lower = text.lower()
        
        if "type" in text_lower and ("mismatch" in text_lower or "change" in text_lower):
            issues.append("Type mismatch identified by analyzer")
            risk_score += 0.3
        
        if "missing" in text_lower or "removed" in text_lower:
            issues.append("Missing field identified by analyzer")
            risk_score += 0.4
        
        if "critical" in text_lower or "high risk" in text_lower:
            risk_score += 0.3
        elif "low risk" in text_lower or "minor" in text_lower:
            risk_score = max(risk_score - 0.2, 0.1)
        
        return {
            "analysis": text[:300],  # First 300 chars
            "detected_issues": issues,
            "risk_score": min(risk_score, 1.0),
            "confidence": 0.7,
            "business_impact": "Analysis suggests potential impact on e-commerce operations"
        }