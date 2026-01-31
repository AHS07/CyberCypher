import asyncio
from app.simple_council import simple_council

async def test_simple_council():
    try:
        print("Testing simple council...")
        
        result = await simple_council.analyze_diff(
            test_id="simple_test",
            merchant_id="test_merchant",
            diff_report={"type_changes": {"price": {"old_type": "float", "new_type": "str"}}},
            legacy_response={"price": 100.0, "status": "SUCCESS"},
            headless_response={"price": "100", "status": "success"}
        )
        
        print(f"Council result: {result['status']}")
        print(f"Final verdict: {result.get('final_verdict')}")
        print(f"Risk score: {result.get('risk_score')}")
        
        return result["status"] == "complete"
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_simple_council())
    print(f"Test {'PASSED' if success else 'FAILED'}")