import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./shop.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    # make sure every model is registered before create_all
    from app.inventory import models as _inventory  # noqa: F401
    from app.notifications import models as _notifications  # noqa: F401
    from app.orders import models as _orders  # noqa: F401

    Base.metadata.create_all(engine)
