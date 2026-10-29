import logging

from app.db import SessionLocal
from app.infra.email import EmailError, send_email
from app.inventory.models import StockItem
from app.notifications.models import NotificationLog
from app.orders.models import Order, OrderLine
from app.worker import celery_app

log = logging.getLogger(__name__)


@celery_app.task(autoretry_for=(EmailError,), retry_backoff=True, max_retries=3)
def send_email_task(to: str, subject: str, body: str, kind: str) -> None:
    db = SessionLocal()
    db.add(NotificationLog(kind=kind, recipient=to, order_id=None))
    db.commit()

    send_email(to, subject, body)
    db.close()


@celery_app.task(autoretry_for=(EmailError,), retry_backoff=True, max_retries=3)
def send_order_email(order_id: int, kind: str) -> None:
    db = SessionLocal()
    order = db.get(Order, order_id)
    if order is None:
        log.warning("order %s not found, skipping %s email", order_id, kind)
        return

    if kind == "confirmed":
        lines = db.query(OrderLine).filter_by(order_id=order.id).all()
        names = {s.sku: s.name for s in db.query(StockItem).filter(StockItem.sku.in_([l.sku for l in lines]))}
        subject, body = f"Order #{order.id} confirmed", "\n".join(f"{names[l.sku]} x{l.qty}" for l in lines)
    else:
        if order.status != "cancelled":
            log.warning("order %s is %s, skipping cancellation email", order_id, order.status)
            return
        subject, body = f"Order #{order.id} cancelled", "Your order was cancelled."

    db.add(NotificationLog(kind=f"order_{kind}", recipient=order.customer_email, order_id=order.id))
    db.commit()

    send_email(order.customer_email, subject, body)

    order.notified = True
    db.commit()
    db.close()
