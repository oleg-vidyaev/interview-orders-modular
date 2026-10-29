from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.infra.email import send_email
from app.inventory.models import StockItem, StockMovement

router = APIRouter(prefix="/inventory", tags=["inventory"])

WAREHOUSE_EMAIL = "warehouse@shop.example"


class StockIn(BaseModel):
    name: str
    price: int
    available: int


@router.put("/{sku}")
def put_stock(sku: str, body: StockIn, db: Session = Depends(get_db)):
    stock = db.get(StockItem, sku)
    old_available = stock.available if stock else 0
    if stock is None:
        stock = StockItem(sku=sku, name=body.name, price=body.price, available=body.available)
        db.add(stock)
    else:
        stock.name, stock.price, stock.available = body.name, body.price, body.available
    db.commit()

    delta = body.available - old_available
    db.add(StockMovement(sku=sku, delta=delta, reason="manual"))
    db.flush()
    send_email(WAREHOUSE_EMAIL, f"Stock updated: {sku}", f"{body.name}: {old_available} -> {body.available}")
    db.commit()

    return {"sku": stock.sku, "name": stock.name, "price": stock.price, "available": stock.available}


@router.get("/{sku}")
def get_stock(sku: str, db: Session = Depends(get_db)):
    stock = db.get(StockItem, sku)
    if stock is None:
        raise HTTPException(404, "unknown sku")
    return {"sku": stock.sku, "name": stock.name, "price": stock.price, "available": stock.available}
