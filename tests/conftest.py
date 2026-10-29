import os
import tempfile

_db_dir = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_db_dir}/test.db"
os.environ["FAKE_SMTP_LATENCY"] = "0"
os.environ["FAKE_HTTP_LATENCY"] = "0"
os.environ["CELERY_EAGER"] = "1"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db import Base, engine  # noqa: E402
from app.infra.email import mailer  # noqa: E402
from app.infra.http import http_client  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app) as c:  # runs lifespan -> init_db
        yield c
    Base.metadata.drop_all(engine)
    mailer.reset()
    http_client.reset()


@pytest.fixture
def stock(client):
    def _stock(sku: str, available: int, price: int = 1000, name: str | None = None):
        r = client.put(f"/inventory/{sku}", json={"name": name or sku, "price": price, "available": available})
        assert r.status_code == 200
    return _stock
