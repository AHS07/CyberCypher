import asyncio
from app.mock_council import mock_council

async def test_mock_council():
    try:
        print("Testing mock council...")
        
        result = await mock_council.analyze_diff(
            test_id="mock_test",
            merchant_id="test_merchant",
            diff_report={
                "type_changes": {"root['price']": {"old_type": "float", "new_type": "str", "old_value": 100.0, "new_value": "100"}},
                "dictionary_item_removed": ["root['tax_total']"],
                "values_changed": {"root['status']": {"old_value": "SUCCESS", "new_value": "success"}}
            },
            legacy_response={"price": 100.0, "status": "SUCCESS", "tax_total": 10.0},
            headless_response={"price": "100", "status": "success"}
        )
        
        print(f"Council result: {result['status']}")
        print(f"Final verdict: {result.get('final_verdict')}")
        print(f"Risk score: {result.get('risk_score')}")
        print(f"Opinions: {len(result.get('council_opinions', []))}")
        
        return result["status"] == "complete"
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mock_council())
    print(f"Test {'PASSED' if success else 'FAILED'}")