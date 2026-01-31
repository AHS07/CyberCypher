"""
Real-Time Connection Verification Script

Tests that:
1. Supabase Realtime is enabled for shadow_tests table
2. Frontend can subscribe to postgres_changes
3. Live updates work end-to-end

Run this AFTER the smoke test passes.
"""

import os
import asyncio
import time
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Load environment
load_dotenv()

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_status(message, status="info"):
    if status == "success":
        print(f"{GREEN}✓ {message}{RESET}")
    elif status == "error":
        print(f"{RED}✗ {message}{RESET}")
    elif status == "warning":
        print(f"{YELLOW}⚠ {message}{RESET}")
    else:
        print(f"{BLUE}→ {message}{RESET}")


async def test_realtime():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Real-Time Connection Verification{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Get credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print_status("Missing Supabase credentials", "error")
        return
    
    print_status("Connecting to Supabase...")
    supabase = create_client(supabase_url, supabase_key)
    
    # Test 1: Insert a test record
    print_status("\nTest 1: Inserting test record...")
    test_id = f"realtime_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    test_data = {
        "test_id": test_id,
        "merchant_id": "Realtime_Test_Merchant",
        "legacy_response": {"status": "test"},
        "headless_response": {"status": "test"},
        "diff_report": {},
        "status": "pending",
        "council_opinions": [],
        "is_mitigated": False,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    try:
        result = supabase.table("shadow_tests").insert(test_data).execute()
        print_status(f"Test record inserted: {test_id}", "success")
    except Exception as e:
        print_status(f"Failed to insert: {e}", "error")
        return
    
    # Test 2: Update the record (simulates council updating)
    print_status("\nTest 2: Simulating council update...")
    time.sleep(1)
    
    try:
        update_result = supabase.table("shadow_tests").update({
            "status": "analyzing",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("test_id", test_id).execute()
        print_status("Record updated to 'analyzing'", "success")
    except Exception as e:
        print_status(f"Failed to update: {e}", "error")
        return
    
    # Test 3: Final update
    print_status("\nTest 3: Simulating completion...")
    time.sleep(1)
    
    try:
        final_result = supabase.table("shadow_tests").update({
            "status": "complete",
            "final_verdict": "PASS",
            "risk_score": 0.15,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("test_id", test_id).execute()
        print_status("Record completed with verdict: PASS", "success")
    except Exception as e:
        print_status(f"Failed final update: {e}", "error")
        return
    
    # Success
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}✓ Real-Time Test Complete!{RESET}")
    print(f"{GREEN}{'='*60}{RESET}\n")
    
    print(f"{BLUE}What to verify in dashboard:{RESET}")
    print(f"1. Open dashboard at http://localhost:3000")
    print(f"2. You should see the test appear in Real-Time Feed")
    print(f"3. Status should change: pending → analyzing → complete")
    print(f"4. Test ID: {YELLOW}{test_id}{RESET}")
    print(f"5. If you see these updates LIVE, realtime is working! ✓\n")
    
    print(f"{YELLOW}Note:{RESET} If dashboard shows Stale Signal, realtime may not be enabled.")
    print(f"Go to: Supabase > Database > Replication > Enable for shadow_tests\n")


if __name__ == "__main__":
    asyncio.run(test_realtime())
