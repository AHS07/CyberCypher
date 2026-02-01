import uuid
import time
import requests
import json
from deepdiff import DeepDiff
from config import LEGACY_URL, HEADLESS_URL, ORCHESTRATOR_URL, supabase
from utils import check_semantic_equivalence, log_to_supabase


def trigger_council_analysis(report: dict, merchant_id: str) -> dict | None:
    """Trigger council analysis on the orchestrator.
    
    Sends the shadow replay report to the orchestrator's /api/analyze endpoint
    to start multi-agent council deliberation.
    
    Args:
        report: Shadow replay report with diff and responses
        merchant_id: Merchant identifier
    
    Returns:
        API response dict or None if failed
    """
    try:
        # Map engine report to orchestrator AnalyzeRequest schema
        analyze_request = {
            "test_id": report["request_id"],
            "merchant_id": merchant_id,
            "legacy_response": report["legacy_response"] or {},
            "headless_response": report["headless_response"] or {},
            "diff_report": report["diff_summary"]
        }
        
        # Debug: Print the request payload
        print(f"Sending request: {json.dumps(analyze_request, indent=2)}")
        
        response = requests.post(
            f"{ORCHESTRATOR_URL}/api/analyze",
            json=analyze_request,
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        print(f"✓ Council analysis triggered: {result}")
        return result
        
    except requests.exceptions.ConnectionError:
        print(f"✗ Could not connect to orchestrator at {ORCHESTRATOR_URL}")
        print("  Make sure the orchestrator is running: uvicorn app.main:app --reload")
        return None
    except Exception as e:
        print(f"✗ Failed to trigger council analysis: {e}")
        return None


def run_shadow_replay(payload: dict, merchant_id: str = "default_merchant", retries: int = 3):
    """Run shadow replay comparing legacy vs headless API responses.
    
    Args:
        payload: Request payload to send to both APIs
        merchant_id: Merchant identifier for tracking
        retries: Number of retries for headless endpoint
    """
    start_time = time.time()
    legacy_resp, legacy_time, legacy_err = _send_request(LEGACY_URL, payload)
    
    headless_resps = []
    for attempt in range(retries):
        h_resp, h_time, h_err = _send_request(HEADLESS_URL, payload)
        headless_resps.append((h_resp, h_time, h_err))
        if h_resp and not h_err:
            break  # Success, no need to retry
    
    # Filter out failures from my list if I was doing multiple
    valid_headless = [r for r in headless_resps if r[0] is not None]
    
    if valid_headless:
        headless_resp, headless_time, _ = valid_headless[0]
        # Calculate average time if we had multiple
        headless_time_avg = sum(r[1] for r in valid_headless) / len(valid_headless)
    else:
        headless_resp = None
        headless_time_avg = 0

    diff = DeepDiff(legacy_resp, headless_resp, ignore_order=True) if legacy_resp and headless_resp else {}
    
    flags = []
    diff_str = str(diff)
    if "type_change" in diff_str: flags.append("type_mismatch")
    if "dictionary_item_removed" in diff_str: flags.append("missing_key")
    if headless_time_avg > legacy_time * 1.5: flags.append("performance_regression")
    
    # Semantic check - only remove truly safe equivalences
    if diff and "type_changes" in diff:
        type_changes = diff["type_changes"]
        keys_to_remove = []
        for path, change in type_changes.items():
            old_val = change.get("old_value") if isinstance(change, dict) else None
            new_val = change.get("new_value") if isinstance(change, dict) else None
            # Only remove if it's a very safe conversion (like int to float)
            # Keep string/number conversions for council analysis
            if old_val is not None and new_val is not None:
                if isinstance(old_val, int) and isinstance(new_val, float) and old_val == new_val:
                    keys_to_remove.append(path)
                elif isinstance(old_val, float) and isinstance(new_val, int) and old_val == new_val:
                    keys_to_remove.append(path)
        
        for k in keys_to_remove:
            del diff["type_changes"][k]
        
        if not diff["type_changes"]:
            del diff["type_changes"]

    # Convert diff to serializable format
    diff_dict = {}
    if diff:
        try:
            diff_dict = json.loads(diff.to_json())
        except (TypeError, ValueError):
            # Fallback: convert to string representation
            diff_dict = {"raw_diff": str(diff)}

    report = {
        "request_id": str(uuid.uuid4()),
        "merchant_id": merchant_id,  # Add merchant_id to report
        "legacy_response": legacy_resp,
        "headless_response": headless_resp,
        "diff_summary": diff_dict,  # Use the serializable diff_dict
        "flags": flags,
        "legacy_time": legacy_time,
        "headless_time": headless_time_avg,
        "retries_used": len(headless_resps)
    }
    
    # Don't log to Supabase here - let the orchestrator handle it
    # log_to_supabase("shadow_tests", report)
    
    # Trigger council analysis on orchestrator
    trigger_council_analysis(report, merchant_id)
    
    return report

def _send_request(url, payload):
    try:
        start = time.time()
        resp = requests.post(url, json=payload, timeout=3)  # 3 second timeout
        resp.raise_for_status()
        return resp.json(), time.time() - start, None
    except requests.exceptions.Timeout:
        return None, 0, "Request timeout"
    except requests.exceptions.ConnectionError:
        return None, 0, "Connection failed"
    except Exception as e:
        return None, 0, str(e)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload", type=str, default='{"item": "shirt", "price": 100}')
    args = parser.parse_args()
    try:
        payload = json.loads(args.payload)
    except json.JSONDecodeError:
         # Fallback for simple string checks or just eval if safe-ish (not safe in prod, but described in prompt)
         # Prompt said: "payload = eval(args.payload) # Unsafe for prod, fine for hack"
         # I'll use json.loads which is safer, user can provide proper json.
         print("Invalid JSON, using default")
         payload = {"item": "shirt", "price": 100}
         
    print(run_shadow_replay(payload))
