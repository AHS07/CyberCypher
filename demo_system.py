#!/usr/bin/env python3
"""
Shadow-SHERPA Hybrid System Demo
Demonstrates end-to-end functionality of the agentic AI system for e-commerce migration parity testing.
"""

import subprocess
import time
import json
import requests
from pathlib import Path

def run_shadow_test(description, config_changes=None):
    """Run a shadow test with optional configuration changes."""
    print(f"\n🔍 {description}")
    print("=" * 60)
    
    if config_changes:
        # Update config
        config_path = Path("engine/config.py")
        content = config_path.read_text()
        
        # Find and replace BUGS_ENABLED
        start = content.find("BUGS_ENABLED = {")
        end = content.find("}", start) + 1
        old_config = content[start:end]
        
        new_config = "BUGS_ENABLED = {\n"
        for key, value in config_changes.items():
            new_config += f'    "{key}": {str(value).lower()},\n'
        new_config += "}"
        
        new_content = content.replace(old_config, new_config)
        config_path.write_text(new_content)
        
        print(f"📝 Updated config: {config_changes}")
        
        # Restart headless server to pick up changes
        print("🔄 Restarting headless server...")
        subprocess.run(["taskkill", "/F", "/IM", "python.exe"], capture_output=True)
        time.sleep(2)
        
        # Start servers
        subprocess.Popen(["engine/venv/Scripts/python.exe", "server_legacy.py"], cwd="engine")
        subprocess.Popen(["engine/venv/Scripts/python.exe", "server_headless.py"], cwd="engine")
        time.sleep(3)
    
    # Run shadow engine test
    result = subprocess.run(
        ["engine/venv/Scripts/python.exe", "shadow_engine.py"],
        cwd="engine",
        capture_output=True,
        text=True
    )
    
    print("📊 Shadow Engine Output:")
    print(result.stdout)
    
    if result.stderr:
        print("⚠️  Errors:")
        print(result.stderr)
    
    return result.returncode == 0

def check_system_status():
    """Check if all system components are running."""
    print("\n🏥 System Health Check")
    print("=" * 40)
    
    # Check servers
    servers = [
        ("Legacy API", "http://localhost:8001/checkout"),
        ("Headless API", "http://localhost:8002/checkout"),
        ("Orchestrator", "http://localhost:8003/health")
    ]
    
    for name, url in servers:
        try:
            if "health" in url:
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, json={"item": "test", "price": 100}, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {name}: Running")
            else:
                print(f"❌ {name}: Error {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Not responding ({e})")

def main():
    """Run the complete system demonstration."""
    print("🚀 Shadow-SHERPA Hybrid System Demo")
    print("=" * 50)
    print("This demo showcases an agentic AI system for e-commerce migration parity testing.")
    print("The system compares legacy vs headless API responses and uses AI agents for analysis.")
    
    # Check system status
    check_system_status()
    
    # Test scenarios
    scenarios = [
        {
            "description": "Test 1: Critical Issues (Type + Missing Field + Case Mismatch)",
            "config": {
                "type_change": True,
                "missing_key": True,
                "case_mismatch": True,
                "performance_delay": False,
                "flaky": False
            }
        },
        {
            "description": "Test 2: Moderate Issues (Type + Case Mismatch Only)",
            "config": {
                "type_change": True,
                "missing_key": False,
                "case_mismatch": True,
                "performance_delay": False,
                "flaky": False
            }
        },
        {
            "description": "Test 3: Perfect Parity (No Issues)",
            "config": {
                "type_change": False,
                "missing_key": False,
                "case_mismatch": False,
                "performance_delay": False,
                "flaky": False
            }
        },
        {
            "description": "Test 4: Performance Regression",
            "config": {
                "type_change": False,
                "missing_key": False,
                "case_mismatch": False,
                "performance_delay": True,
                "flaky": False
            }
        }
    ]
    
    for scenario in scenarios:
        success = run_shadow_test(scenario["description"], scenario["config"])
        if success:
            print("✅ Test completed successfully")
        else:
            print("❌ Test failed")
        
        time.sleep(2)  # Brief pause between tests
    
    print("\n🎯 Demo Complete!")
    print("=" * 30)
    print("Key Features Demonstrated:")
    print("• Shadow replay testing with diff detection")
    print("• Multi-agent council analysis (mock implementation)")
    print("• Real-time database updates")
    print("• Risk scoring and verdict determination")
    print("• End-to-end agentic workflow")
    print("\nCheck the Supabase database to see all test results!")

if __name__ == "__main__":
    main()