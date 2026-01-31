"""LangGraph workflow for multi-agent council deliberation."""
import logging
from typing import Dict, Any, TypedDict
from datetime import datetime

from app.agents.primary_analyzer import PrimaryAnalyzer
from app.agents.skeptic_critic import SkepticCritic
from app.agents.consensus_judge import ConsensusJudge

logger = logging.getLogger(__name__)

class CouncilState(TypedDict):
    """State object for the council workflow."""
    test_id: str
    merchant_id: str
    diff_report: Dict[str, Any]
    legacy_response: Dict[str, Any]
    headless_response: Dict[str, Any]
    
    # Agent outputs
    primary_analysis: Dict[str, Any]
    skeptic_critique: Dict[str, Any]
    final_judgment: Dict[str, Any]
    
    # Workflow state
    status: str
    error_message: str
    council_opinions: list

class CouncilWorkflow:
    """Orchestrates the multi-agent council deliberation."""
    
    def __init__(self):
        self.primary_analyzer = PrimaryAnalyzer()
        self.skeptic_critic = SkepticCritic()
        self.consensus_judge = ConsensusJudge()
    
    async def run_council_analysis(self, test_id: str, merchant_id: str, 
                                  diff_report: Dict[str, Any], legacy_response: Dict[str, Any], 
                                  headless_response: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete council analysis workflow."""
        
        logger.info(f"Starting council analysis for test {test_id}")
        
        # Initialize state
        state = CouncilState(
            test_id=test_id,
            merchant_id=merchant_id,
            diff_report=diff_report,
            legacy_response=legacy_response,
            headless_response=headless_response,
            primary_analysis={},
            skeptic_critique={},
            final_judgment={},
            status="analyzing",
            error_message="",
            council_opinions=[]
        )
        
        try:
            # Step 1: Primary Analysis
            logger.info(f"Running primary analysis for {test_id}")
            state["primary_analysis"] = await self.primary_analyzer.analyze(
                test_id, merchant_id, diff_report, legacy_response, headless_response
            )
            state["council_opinions"].append(state["primary_analysis"])
            
            # Step 2: Skeptic Critique
            logger.info(f"Running skeptic critique for {test_id}")
            state["skeptic_critique"] = await self.skeptic_critic.critique(
                test_id, state["primary_analysis"], diff_report, legacy_response, headless_response
            )
            state["council_opinions"].append(state["skeptic_critique"])
            
            # Step 3: Consensus Judgment
            logger.info(f"Running consensus judgment for {test_id}")
            state["final_judgment"] = await self.consensus_judge.judge(
                test_id, merchant_id, state["primary_analysis"], state["skeptic_critique"], diff_report
            )
            state["council_opinions"].append(state["final_judgment"])
            
            # Finalize state
            state["status"] = "complete"
            
            logger.info(f"Council analysis completed for {test_id}")
            
            return self._format_final_result(state)
            
        except Exception as e:
            logger.error(f"Council analysis failed for {test_id}: {e}")
            state["status"] = "failed"
            state["error_message"] = str(e)
            
            return self._format_error_result(state)
    
    def _format_final_result(self, state: CouncilState) -> Dict[str, Any]:
        """Format the final council result."""
        
        final_judgment = state["final_judgment"]
        
        return {
            "test_id": state["test_id"],
            "merchant_id": state["merchant_id"],
            "status": "complete",
            "council_opinions": state["council_opinions"],
            "final_verdict": final_judgment.get("verdict", "NEEDS_REVIEW"),
            "risk_score": final_judgment.get("final_risk_score", 0.5),
            "is_mitigated": False,
            "mitigation_recommendation": final_judgment.get("recommendation", "Manual review required"),
            "active_provider": "huggingface_council",
            "providers_attempted": self._get_providers_attempted(state),
            "analysis_summary": self._create_analysis_summary(state),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _format_error_result(self, state: CouncilState) -> Dict[str, Any]:
        """Format error result when council fails."""
        
        return {
            "test_id": state["test_id"],
            "merchant_id": state["merchant_id"],
            "status": "failed",
            "error_message": state["error_message"],
            "council_opinions": state["council_opinions"],  # Partial results
            "is_mitigated": False,
            "active_provider": "huggingface_council",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_providers_attempted(self, state: CouncilState) -> list:
        """Get list of providers attempted during analysis."""
        providers = []
        
        if state["primary_analysis"].get("model"):
            providers.append(state["primary_analysis"]["model"])
        if state["skeptic_critique"].get("model"):
            providers.append(state["skeptic_critique"]["model"])
        if state["final_judgment"].get("model"):
            providers.append(state["final_judgment"]["model"])
        
        return list(set(providers))  # Remove duplicates
    
    def _create_analysis_summary(self, state: CouncilState) -> str:
        """Create a human-readable summary of the analysis."""
        
        primary = state["primary_analysis"]
        skeptic = state["skeptic_critique"]
        judge = state["final_judgment"]
        
        summary_parts = []
        
        # Primary findings
        if primary.get("detected_issues"):
            summary_parts.append(f"Primary Analyzer detected {len(primary['detected_issues'])} issues")
        
        # Skeptic findings
        if skeptic.get("false_positives"):
            summary_parts.append(f"Skeptic identified {len(skeptic['false_positives'])} false positives")
        if skeptic.get("genuine_concerns"):
            summary_parts.append(f"Skeptic confirmed {len(skeptic['genuine_concerns'])} genuine concerns")
        
        # Final decision
        verdict = judge.get("verdict", "UNKNOWN")
        risk_score = judge.get("final_risk_score", 0)
        summary_parts.append(f"Final verdict: {verdict} (risk: {risk_score:.2f})")
        
        return ". ".join(summary_parts) + "."


# Global workflow instance
council_workflow = CouncilWorkflow()

async def run_council_analysis(test_id: str, merchant_id: str, diff_report: Dict[str, Any], 
                              legacy_response: Dict[str, Any], headless_response: Dict[str, Any]) -> Dict[str, Any]:
    """Run council analysis - main entry point."""
    return await council_workflow.run_council_analysis(
        test_id, merchant_id, diff_report, legacy_response, headless_response
    )