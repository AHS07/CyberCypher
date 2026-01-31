import requests
import json

# Test legacy server
try:
    response = requests.post("http://localhost:8001/checkout", json={"item": "test", "price": 100})
    print(f"Legacy server - Status: {response.status_code}, Response: {response.json()}")
except Exception as e:
    print(f"Legacy server error: {e}")

# Test headless server
try:
    response = requests.post("http://localhost:8002/checkout", json={"item": "test", "price": 100})
    print(f"Headless server - Status: {response.status_code}, Response: {response.json()}")
except Exception as e:
    print(f"Headless server error: {e}")