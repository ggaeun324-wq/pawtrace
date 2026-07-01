"""장바구니(Cart) 테스트 — 담기/수량변경/삭제/결제/빈 장바구니.

결제는 기존 주문 로직을 재사용하므로 재고 차감·장바구니 비우기까지 확인합니다.
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _token(email: str, password: str) -> str:
    return client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    ).json()["access_token"]


def _headers() -> dict:
    return {"Authorization": f"Bearer {_token('adopter@pawtrace.dev', 'adopter1234')}"}


def _first_product() -> dict:
    return client.get("/api/v1/shop/products").json()[0]


def test_cart_requires_auth():
    assert client.get("/api/v1/shop/cart").status_code == 401


def test_add_update_remove_cart_flow():
    h = _headers()
    client.delete("/api/v1/shop/cart", headers=h)  # 초기화
    p = _first_product()

    # 담기
    r = client.post(
        "/api/v1/shop/cart/items",
        json={"product_id": p["id"], "quantity": 2},
        headers=h,
    )
    assert r.status_code == 200, r.text
    cart = r.json()
    assert cart["count"] == 1
    assert cart["subtotal"] == p["price"] * 2
    assert cart["items"][0]["quantity"] == 2

    # 수량 변경
    r = client.put(
        f"/api/v1/shop/cart/items/{p['id']}",
        json={"quantity": 3},
        headers=h,
    )
    assert r.json()["items"][0]["quantity"] == 3

    # 삭제(수량 0)
    r = client.put(
        f"/api/v1/shop/cart/items/{p['id']}",
        json={"quantity": 0},
        headers=h,
    )
    assert r.json()["count"] == 0


def test_checkout_creates_order_and_clears_cart():
    h = _headers()
    client.delete("/api/v1/shop/cart", headers=h)
    p = _first_product()
    before_stock = p["stock"]

    client.post(
        "/api/v1/shop/cart/items",
        json={"product_id": p["id"], "quantity": 2},
        headers=h,
    )
    r = client.post("/api/v1/shop/cart/checkout", json={}, headers=h)
    assert r.status_code == 200, r.text
    order = r.json()
    assert order["status"] == "paid"
    assert order["total_amount"] == p["price"] * 2

    # 장바구니가 비워졌는지
    cart = client.get("/api/v1/shop/cart", headers=h).json()
    assert cart["count"] == 0

    # 재고가 줄었는지
    after = next(
        x for x in client.get("/api/v1/shop/products").json() if x["id"] == p["id"]
    )
    assert after["stock"] == before_stock - 2


def test_checkout_empty_cart_rejected():
    h = _headers()
    client.delete("/api/v1/shop/cart", headers=h)
    r = client.post("/api/v1/shop/cart/checkout", json={}, headers=h)
    assert r.status_code == 400
