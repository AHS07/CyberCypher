import requests
import json

# Test with a simple payload
payload = {
    "test_id": "simple_test",
    "merchant_id": "test",
    "legacy_response": {"price": 100},
    "headless_response": {"price": "100"},
    "diff_report": {"type_changes": {"price": {"old_type": "int", "new_type": "str"}}}
}

try:
    response = requests.post(
        "http://localhost:8000/api/analyze",
        json=payload,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code != 200:
        print("Error details:", response.headers)
        
except Exception as e:
    print(f"Error: {e}")