import requests
import json

# Test the analyze endpoint
payload = {
    "test_id": "test123",
    "merchant_id": "test_merchant",
    "legacy_response": {"status": "SUCCESS", "price": 100.0},
    "headless_response": {"status": "success", "price": "100"},
    "diff_report": {"type_changes": {"price": {"old_type": "float", "new_type": "str"}}}
}

try:
    response = requests.post(
        "http://localhost:8000/api/analyze",
        json=payload,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")