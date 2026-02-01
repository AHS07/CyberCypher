#!/usr/bin/env python3
"""
Complete Shadow-SHERPA Hybrid System Demo

This script demonstrates the full end-to-end functionality:
1. Shadow replay testing with API differences
2. Multi-agent council analysis using HuggingFace models
3. Real-time dashboard integration
4. Human-in-the-loop mitigation controls
"""

import requests
import json
import time
import subprocess
import sys
from pathlib import Path

# Configuration
ENGINE_DIR = Path("engine")
ORCHESTRATOR_URL = "http://localhost:8005"
DASHBOARD_URL = "http://localhost:3000"

def run_shadow_test(payload, description):
    """Run a shadow test and return the test_id."""
    print(f"\n🔍 Running Shadow Test: {description}")
    print(f"Payload: {json.dumps(payload)}")
    
    # Run shadow engine
    result = subprocess.run([
        sys.executable, "shadow_engine.py", 
        "--payload", json.dumps(payload)
    ], cwd=ENGINE_DIR, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Shadow test failed: {result.stderr}")
        return None
    
    # Extract test_id from output
    output_lines = result.stdout.split('\n')
    for line in output_lines:
        if "Council analysis triggered" in line and "test_id" in line:
            # Parse the JSON response
            try:
                start = line.find('{')
                end = line.rfind('}') + 1
                response = json.loads(line[start:end])
                return response.get('test_id')
            except:
                pass
    
    print("❌ Could not extract test_id from output")
    return None

def wait_for_analysis(test_id, timeout=30):
    """Wait for council analysis to complete."""
    print(f"⏳ Waiting for council analysis to complete...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{ORCHESTRATOR_URL}/api/status/{test_id}")
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                
                if status == 'complete':
                    print(f"✅ Analysis complete!")
                    return data
                elif status == 'failed':
                    print(f"❌ Analysis failed: {data.get('error_message', 'Unknown error')}")
                    return data
                else:
                    print(f"   Status: {status}")
            
            time.sleep(2)
        except Exception as e:
            print(f"   Error checking status: {e}")
            time.sleep(2)
    
    print(f"⏰ Timeout waiting for analysis")
    return None

def display_council_analysis(data):
    """Display the council analysis results."""
    print(f"\n📊 Council Analysis Results")
    print(f"=" * 50)
    print(f"Test ID: {data['test_id']}")
    print(f"Merchant: {data['merchant_id']}")
    print(f"Final Verdict: {data['final_verdict']}")
    print(f"Risk Score: {data['risk_score']:.2f}")
    print(f"Recommendation: {data['mitigation_recommendation']}")
    
    print(f"\n🤖 Agent Opinions:")
    for i, opinion in enumerate(data['council_opinions'], 1):
        agent = opinion['agent'].replace('_', ' ').title()
        print(f"  {i}. {agent} ({opinion['provider']})")
        print(f"     Risk Score: {opinion['risk_score']:.2f}")
        print(f"     Confidence: {opinion['confidence']:.2f}")
        print(f"     Analysis: {opinion['analysis'][:100]}...")
        if opinion.get('detected_issues'):
            print(f"     Issues: {', '.join(opinion['detected_issues'])}")
        if opinion.get('false_positives'):
            print(f"     False Positives: {', '.join(opinion['false_positives'])}")

def test_mitigation_controls(test_id):
    """Test the mitigation controls."""
    print(f"\n🛡️ Testing Mitigation Controls")
    
    try:
        response = requests.post(f"{ORCHESTRATOR_URL}/api/mitigate/{test_id}")
        if response.status_code == 200:
            print(f"✅ Mitigation successful: {response.json()['message']}")
        else:
            print(f"❌ Mitigation failed: {response.text}")
    except Exception as e:
        print(f"❌ Mitigation error: {e}")

def main():
    """Run the complete system demo."""
    print("🚀 Shadow-SHERPA Hybrid System Demo")
    print("=" * 50)
    
    # Check system health
    print("\n🏥 Checking System Health...")
    try:
        health = requests.get(f"{ORCHESTRATOR_URL}/api/health/providers")
        if health.status_code == 200:
            providers = health.json()
            print(f"✅ Orchestrator online with {len(providers)} providers")
        else:
            print(f"❌ Orchestrator health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to orchestrator: {e}")
        return
    
    # Test 1: No differences (should pass)
    test_id_1 = run_shadow_test(
        {"item": "laptop", "price": 1000},
        "Identical responses (should PASS)"
    )
    
    if test_id_1:
        result_1 = wait_for_analysis(test_id_1)
        if result_1:
            display_council_analysis(result_1)
    
    # Test 2: Type mismatch (should need review)
    test_id_2 = run_shadow_test(
        {"item": "gaming_laptop", "price": 2500},
        "Type mismatch: float vs string (should NEED REVIEW)"
    )
    
    if test_id_2:
        result_2 = wait_for_analysis(test_id_2)
        if result_2:
            display_council_analysis(result_2)
            
            # Test mitigation
            test_mitigation_controls(test_id_2)
    
    print(f"\n🎯 Demo Complete!")
    print(f"Dashboard: {DASHBOARD_URL}")
    print(f"API Docs: {ORCHESTRATOR_URL}/docs")
    print(f"\nThe system is now running and ready for interactive testing!")

if __name__ == "__main__":
    main()