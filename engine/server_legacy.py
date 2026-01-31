from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel

app = FastAPI()

class CheckoutPayload(BaseModel):
    item: str = "item"
    price: float = 100.0
    quantity: int = 1

@app.post("/checkout")
def checkout(payload: CheckoutPayload):
    # Simple success
    return {
        "status": "SUCCESS",
        "price": 100.0,
        "tax_total": 10.0,
        "order_id": "12345"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
