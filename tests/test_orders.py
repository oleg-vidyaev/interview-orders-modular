from app.infra.email import mailer


def test_create_order_reserves_stock_and_sends_confirmation(client, stock):
    stock("BOOK", available=10, price=1500)

    r = client.post("/orders", json={"customer_email": "a@example.com", "items": [{"sku": "BOOK", "qty": 2}]})

    assert r.status_code == 201
    assert r.json()["status"] == "reserved"
    assert r.json()["lines"] == [{"sku": "BOOK", "qty": 2, "price": 1500}]
    assert client.get("/inventory/BOOK").json()["available"] == 8
    assert len([m for m in mailer.sent if m["to"] == "a@example.com"]) == 1


def test_out_of_stock_returns_409(client, stock):
    stock("BOOK", available=1)

    r = client.post("/orders", json={"customer_email": "a@example.com", "items": [{"sku": "BOOK", "qty": 2}]})

    assert r.status_code == 409


def test_cancel_returns_stock(client, stock):
    stock("BOOK", available=10)
    order_id = client.post(
        "/orders", json={"customer_email": "a@example.com", "items": [{"sku": "BOOK", "qty": 2}]}
    ).json()["id"]

    r = client.post(f"/orders/{order_id}/cancel")

    assert r.status_code == 200
    assert r.json()["status"] == "cancelled"
    assert client.get("/inventory/BOOK").json()["available"] == 10


def test_cannot_cancel_twice(client, stock):
    stock("BOOK", available=10)
    order_id = client.post(
        "/orders", json={"customer_email": "a@example.com", "items": [{"sku": "BOOK", "qty": 1}]}
    ).json()["id"]
    client.post(f"/orders/{order_id}/cancel")

    r = client.post(f"/orders/{order_id}/cancel")

    assert r.status_code == 409
