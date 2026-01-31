import asyncio
from app.graph.council_graph import run_council_analysis

async def test_council():
    try:
        result = await run_council_analysis(
            test_id="test_council",
            merchant_id="test_merchant",
            legacy_response={"price": 100.0},
            headless_response={"price": "100"},
            diff_report={"type_changes": {"price": {"old_type": "float", "new_type": "str"}}}
        )
        print("Council analysis completed:", result.get("status"))
        return True
    except Exception as e:
        print(f"Council analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_council())
    print(f"Test {'PASSED' if success else 'FAILED'}")