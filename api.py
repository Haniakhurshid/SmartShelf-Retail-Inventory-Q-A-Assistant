from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

class PurchaseRequest(BaseModel):
    product_name: str
    quantity: int

def get_connection():
    return sqlite3.connect("inventory.db")

@app.get("/")
def root():
    return {"message": "SmartShelf Inventory API"}

@app.post("/purchase")
def simulate_purchase(request: PurchaseRequest):
    conn = get_connection()
    cursor = conn.cursor()

    # Check product availability
    cursor.execute("SELECT In_Stock FROM products WHERE Product = ?", (request.product_name,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")

    in_stock = result[0]

    if request.quantity > in_stock:
        conn.close()
        raise HTTPException(status_code=400, detail="Not enough stock available")

    # Update stock
    cursor.execute(
        "UPDATE products SET In_Stock = In_Stock - ? WHERE Product = ?",
        (request.quantity, request.product_name)
    )
    conn.commit()
    conn.close()

    return {"message": f"✅ Purchase successful! {request.quantity} units of '{request.product_name}' bought."}

