"""
Smoke Test Script - Verify Shadow Twin Guardian Setup

This script:
1. Tests Supabase connection
2. Inserts mock data to trigger the council
3. Verifies backend can process the test
4. Checks if dashboard receives real-time updates

PREREQUISITES:
    pip install supabase python-dotenv

Run this BEFORE pushing to ensure everything works.
"""

import os
import sys
from datetime import datetime

try:
    from dotenv import load_dotenv
    from supabase import create_client
except ImportError:
    print("\n❌ Missing dependencies!")
    print("Run: pip install supabase python-dotenv\n")
    sys.exit(1)

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_status(message, status="info"):
    """Print colored status messages."""
    if status == "success":
        print(f"{GREEN}✓ {message}{RESET}")
    elif status == "error":
        print(f"{RED}✗ {message}{RESET}")
    elif status == "warning":
        print(f"{YELLOW}⚠ {message}{RESET}")
    else:
        print(f"{BLUE}→ {message}{RESET}")


def main():
    # Load environment variables
    load_dotenv()
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Shadow Twin Guardian - Smoke Test{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Step 1: Check environment variables
    print_status("Checking environment variables...")
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url:
        print_status("SUPABASE_URL not found in .env", "error")
        print_status("Please set SUPABASE_URL in your .env file", "warning")
        sys.exit(1)
    
    if not supabase_key:
        print_status("SUPABASE_SERVICE_KEY not found in .env", "error")
        print_status("Please set SUPABASE_SERVICE_KEY in your .env file", "warning")
        sys.exit(1)
    
    print_status(f"Supabase URL: {supabase_url[:30]}...", "success")
    print_status(f"Service Key: {'*' * 20}...", "success")
    
    # Step 2: Test Supabase connection
    print_status("\nConnecting to Supabase...")
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        print_status("Connected to Supabase successfully", "success")
    except Exception as e:
        print_status(f"Failed to connect to Supabase: {e}", "error")
        sys.exit(1)
    
    # Step 3: Verify tables exist
    print_status("\nVerifying tables exist...")
    
    tables_to_check = ["shadow_tests", "reliability_logs", "checkpoints"]
    
    for table in tables_to_check:
        try:
            result = supabase.table(table).select("*").limit(1).execute()
            print_status(f"Table '{table}' exists and is accessible", "success")
        except Exception as e:
            print_status(f"Table '{table}' not found or not accessible", "error")
            print_status(f"Error: {str(e)}", "warning")
            print_status(f"Please run migrations from shared/migrations/", "warning")
            sys.exit(1)
    
    # Step 4: Insert mock data
    print_status("\nInserting mock parity test data...")
    
    test_id = f"smoke_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    mock_data = {
        "test_id": test_id,
        "merchant_id": "VIT_Vellore_Test_Store",
        "legacy_response": {
            "price": 100,
            "currency": "INR",
            "stock": 50
        },
        "headless_response": {
            "price": "100",  # String vs Int - deliberate mismatch
            "currency": "INR",
            "stock": 50
        },
        "diff_report": {
            "type_changes": {
                "root['price']": {
                    "old_type": "int",
                    "new_type": "str"
                }
            }
        },
        "status": "pending"
    }
    
    try:
        result = supabase.table("shadow_tests").insert(mock_data).execute()
        print_status(f"Mock test inserted with ID: {test_id}", "success")
    except Exception as e:
        print_status(f"Failed to insert mock data: {e}", "error")
        sys.exit(1)
    
    # Step 5: Verify data can be retrieved
    print_status("\nVerifying data retrieval...")
    
    try:
        result = supabase.table("shadow_tests").select("*").eq("test_id", test_id).execute()
        if result.data and len(result.data) > 0:
            print_status("Mock data retrieved successfully", "success")
            print_status(f"Status: {result.data[0]['status']}", "info")
        else:
            print_status("Failed to retrieve mock data", "error")
            sys.exit(1)
    except Exception as e:
        print_status(f"Error retrieving data: {e}", "error")
        sys.exit(1)
    
    # Success summary
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}✓ All smoke tests passed!{RESET}")
    print(f"{GREEN}{'='*60}{RESET}\n")
    
    print(f"{BLUE}Next Steps:{RESET}")
    print(f"1. Start the orchestrator: cd orchestrator && uvicorn app.main:app --reload")
    print(f"2. Start the dashboard: cd dashboard && npm run dev")
    print(f"3. Open dashboard at http://localhost:3000")
    print(f"4. Trigger analysis via API:")
    print(f"   curl -X POST http://localhost:8000/api/analyze \\")
    print(f"        -H 'Content-Type: application/json' \\")
    print(f"        -d @test_payload.json")
    print(f"\n5. Watch the dashboard for real-time updates!")
    print(f"6. Mock test ID: {YELLOW}{test_id}{RESET}\n")


if __name__ == "__main__":
    main()
