from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class NotificationLog(Base):
    __tablename__ = "notification_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str]
    recipient: Mapped[str]
    order_id: Mapped[int | None]
    sent_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
