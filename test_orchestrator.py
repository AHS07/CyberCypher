import requests
import json

# Test data
test_data = {
    "test_id": "test123",
    "merchant_id": "test_merchant",
    "legacy_response": {"status": "SUCCESS", "price": 100.0},
    "headless_response": {"status": "success", "price": "100"},
    "diff_report": {"type_changes": {"root['price']": {"old_type": "float", "new_type": "str"}}}
}

try:
    response = requests.post(
        "http://localhost:8003/api/analyze",
        json=test_data,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")