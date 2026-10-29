from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.inventory.models import Reservation, StockItem
from app.notifications.tasks import send_email_task, send_order_email
from app.orders.models import Order, OrderLine

router = APIRouter(prefix="/orders", tags=["orders"])

LOW_STOCK_THRESHOLD = 3
WAREHOUSE_EMAIL = "warehouse@shop.example"


class Item(BaseModel):
    sku: str
    qty: int = Field(gt=0)


class OrderIn(BaseModel):
    customer_email: str
    items: list[Item] = Field(min_length=1)


def _to_dict(order: Order) -> dict:
    return {
        "id": order.id,
        "customer_email": order.customer_email,
        "status": order.status,
        "lines": [{"sku": l.sku, "qty": l.qty, "price": l.price} for l in order.lines],
    }


@router.post("", status_code=201)
def create_order(body: OrderIn, db: Session = Depends(get_db)):
    order = Order(customer_email=body.customer_email, status="new")
    db.add(order)
    db.commit()
    db.refresh(order)

    for item in body.items:
        stock = db.get(StockItem, item.sku)
        if stock is None:
            raise HTTPException(422, f"unknown sku: {item.sku}")
        db.add(OrderLine(order_id=order.id, sku=item.sku, qty=item.qty, price=stock.price))
    db.commit()

    # reserve stock
    for line in db.query(OrderLine).filter_by(order_id=order.id).all():
        stock = db.get(StockItem, line.sku)
        if stock.available < line.qty:
            order.status = "rejected"
            db.commit()
            raise HTTPException(409, f"out of stock: {line.sku}")

        stock.available -= line.qty
        db.add(Reservation(order_id=order.id, sku=line.sku, qty=line.qty))

        if stock.available < LOW_STOCK_THRESHOLD:
            send_email_task.delay(
                WAREHOUSE_EMAIL, f"Low stock: {stock.sku}", f"{stock.name}: {stock.available} left", "low_stock"
            )

    order.status = "reserved"
    db.commit()

    send_order_email.delay(order.id, "confirmed")

    db.refresh(order)
    return _to_dict(order)


@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(404, "order not found")
    return _to_dict(order)


@router.post("/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(404, "order not found")
    if order.status != "reserved":
        raise HTTPException(409, f"cannot cancel order in status {order.status}")

    order.status = "cancelled"
    for reservation in db.query(Reservation).filter_by(order_id=order.id).all():
        stock = db.get(StockItem, reservation.sku)
        stock.available += reservation.qty
        db.delete(reservation)

    send_order_email.delay(order.id, "cancelled")
    db.commit()
    return _to_dict(order)
