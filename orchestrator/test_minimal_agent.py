import asyncio
from app.models.state import ShadowState
from app.core.llm_manager import llm_manager
from langchain_core.messages import SystemMessage, HumanMessage

async def minimal_primary_analyzer(state: ShadowState):
    """Minimal version of primary analyzer without failover."""
    try:
        print("Starting minimal primary analyzer...")
        
        # Simple LLM call without failover
        llm = llm_manager.get_llm("deepseek", temperature=0.0)
        
        messages = [
            SystemMessage(content="You are analyzing API differences. Respond with just 'ANALYSIS_COMPLETE'."),
            HumanMessage(content=f"Analyze this diff: {state['diff_report']}")
        ]
        
        print("Calling LLM...")
        result = await llm.ainvoke(messages)
        print(f"LLM response: {result.content[:50]}")
        
        return {
            "council_opinions": [{
                "agent": "primary_analyzer",
                "provider": "deepseek",
                "analysis": "Test analysis",
                "detected_issues": [],
                "risk_score": 0.1,
                "confidence": 0.9,
            }],
            "status": "complete"
        }
        
    except Exception as e:
        print(f"Error in minimal analyzer: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "failed", "error_message": str(e)}

async def test_minimal():
    state = {
        "test_id": "minimal_test",
        "merchant_id": "test",
        "diff_report": {"type_changes": {"price": {"old_type": "float", "new_type": "str"}}},
        "legacy_response": {"price": 100.0},
        "headless_response": {"price": "100"},
        "council_opinions": [],
        "status": "pending"
    }
    
    result = await minimal_primary_analyzer(state)
    print("Result:", result)
    return result.get("status") == "complete"

if __name__ == "__main__":
    success = asyncio.run(test_minimal())
    print(f"Test {'PASSED' if success else 'FAILED'}")