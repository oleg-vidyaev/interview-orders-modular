from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_db
from app.inventory.api import router as inventory_router
from app.orders.api import router as orders_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="shop", lifespan=lifespan)
app.include_router(orders_router)
app.include_router(inventory_router)
