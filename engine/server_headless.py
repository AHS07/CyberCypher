from fastapi import FastAPI
from config import BUGS_ENABLED
import time
import random
import uvicorn
from pydantic import BaseModel

app = FastAPI()

class CheckoutPayload(BaseModel):
    item: str = "item"
    price: float = 100.0
    quantity: int = 1

@app.post("/checkout")
def checkout(payload: CheckoutPayload):
    resp = {
        "status": "SUCCESS",
        "price": 100.0,
        "tax_total": 10.0,
        "order_id": "12345"
    }
    if BUGS_ENABLED["type_change"]:
        resp["price"] = "100"  # String instead of float
    if BUGS_ENABLED["missing_key"]:
        if "tax_total" in resp:
            del resp["tax_total"]
    if BUGS_ENABLED["case_mismatch"]:
        resp["status"] = "success"
    if BUGS_ENABLED["performance_delay"]:
        time.sleep(2)  # Simulate slow API
    if BUGS_ENABLED["flaky"] and random.random() < 0.2:
        raise ValueError("Flaky failure")
    return resp

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
