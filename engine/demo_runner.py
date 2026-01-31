"""
Demo Runner - Run shadow replay tests through the full pipeline.

This script sends synthetic checkout payloads through the shadow engine,
which will:
1. Call legacy and headless mock servers
2. Compare responses with DeepDiff
3. Log to Supabase
4. Trigger council analysis on orchestrator

Usage:
    cd engine
    python demo_runner.py
"""

import time
import json
from shadow_engine import run_shadow_replay

# Sample checkout payloads with various scenarios
DEMO_PAYLOADS = [
    {
        "name": "Basic Checkout",
        "merchant_id": "VIT_Vellore_Demo",
        "payload": {"item": "laptop", "price": 50000, "quantity": 1}
    },
    {
        "name": "High Value Order",
        "merchant_id": "VIT_Vellore_Demo",
        "payload": {"item": "gaming_pc", "price": 150000, "quantity": 1}
    },
    {
        "name": "Multi-Item Order",
        "merchant_id": "Mumbai_Store_Demo",
        "payload": {"item": "phone_case", "price": 999, "quantity": 5}
    },
]


def run_demo():
    """Run demo payloads through the shadow replay pipeline."""
    print("=" * 60)
    print("  Shadow-SHERPA Hybrid - Demo Runner")
    print("=" * 60)
    print()
    
    for i, scenario in enumerate(DEMO_PAYLOADS, 1):
        print(f"[{i}/{len(DEMO_PAYLOADS)}] Running: {scenario['name']}")
        print(f"    Merchant: {scenario['merchant_id']}")
        print(f"    Payload: {json.dumps(scenario['payload'])}")
        
        try:
            report = run_shadow_replay(
                payload=scenario["payload"],
                merchant_id=scenario["merchant_id"]
            )
            
            print(f"    ✓ Test ID: {report.get('request_id', 'N/A')}")
            print(f"    ✓ Flags: {report.get('flags', [])}")
            print(f"    ✓ Diff found: {bool(report.get('diff_summary'))}")
            print()
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            print()
        
        # Small delay between tests
        time.sleep(1)
    
    print("=" * 60)
    print("  Demo complete! Check the dashboard at http://localhost:3000")
    print("=" * 60)


if __name__ == "__main__":
    run_demo()
