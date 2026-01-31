#!/usr/bin/env python3
"""Test the real Hugging Face council directly."""

import asyncio
import sys
import os

# Add the orchestrator app to the path
sys.path.append('orchestrator')

from orchestrator.app.graph.council_graph import run_council_analysis

async def test_council():
    """Test the real council with sample data."""
    
    print("🧪 Testing Real Multi-Agent Council with Hugging Face Models")
    print("=" * 60)
    
    # Sample test data
    test_data = {
        "test_id": "test_council_001",
        "merchant_id": "test_merchant",
        "diff_report": {
            "type_changes": {
                "root['price']": {
                    "old_type": "float",
                    "new_type": "str", 
                    "old_value": 100.0,
                    "new_value": "100"
                }
            },
            "dictionary_item_removed": ["root['tax_total']"],
            "values_changed": {
                "root['status']": {
                    "new_value": "success",
                    "old_value": "SUCCESS"
                }
            }
        },
        "legacy_response": {
            "status": "SUCCESS",
            "price": 100.0,
            "tax_total": 10.0,
            "order_id": "12345"
        },
        "headless_response": {
            "status": "success", 
            "price": "100",
            "order_id": "12345"
        }
    }
    
    print("📊 Test Data:")
    print(f"- Type mismatch: price {test_data['legacy_response']['price']} → {test_data['headless_response']['price']}")
    print(f"- Missing field: tax_total removed")
    print(f"- Case change: {test_data['legacy_response']['status']} → {test_data['headless_response']['status']}")
    
    print("\n🤖 Starting Multi-Agent Council Analysis...")
    
    try:
        result = await run_council_analysis(
            test_id=test_data["test_id"],
            merchant_id=test_data["merchant_id"],
            diff_report=test_data["diff_report"],
            legacy_response=test_data["legacy_response"],
            headless_response=test_data["headless_response"]
        )
        
        print("\n✅ Council Analysis Complete!")
        print("=" * 40)
        
        print(f"🎯 Final Verdict: {result.get('final_verdict', 'UNKNOWN')}")
        print(f"📊 Risk Score: {result.get('risk_score', 0):.2f}")
        print(f"💡 Recommendation: {result.get('mitigation_recommendation', 'N/A')}")
        
        if result.get('council_opinions'):
            print(f"\n👥 Council Opinions ({len(result['council_opinions'])} agents):")
            for i, opinion in enumerate(result['council_opinions'], 1):
                agent = opinion.get('agent', 'unknown')
                model = opinion.get('model', 'unknown')
                print(f"  {i}. {agent} ({model})")
                if 'analysis' in opinion:
                    analysis = opinion['analysis'][:100] + "..." if len(opinion['analysis']) > 100 else opinion['analysis']
                    print(f"     Analysis: {analysis}")
        
        if result.get('analysis_summary'):
            print(f"\n📋 Summary: {result['analysis_summary']}")
        
        print(f"\n🔧 Models Used: {result.get('providers_attempted', [])}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Council Analysis Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_council())
    if success:
        print("\n🎉 Real Multi-Agent Council is working!")
    else:
        print("\n💥 Council test failed - check the logs above")