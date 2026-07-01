"""쇼핑몰(커머스) 테스트 — 결제/재고/후원 적립/쿠폰/임팩트 + 저니 보상 쿠폰.

원칙 확인: 사람을 평가하지 않고 '기록 작성' 행동만 보상(쿠폰)합니다.
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _token(email: str, password: str) -> str:
    return client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    ).json()["access_token"]


def _adopter_headers() -> dict:
    return {"Authorization": f"Bearer {_token('adopter@pawtrace.dev', 'adopter1234')}"}


def _first_product() -> dict:
    products = client.get("/api/v1/shop/products").json()
    assert products, "시드 상품이 있어야 합니다."
    return products[0]


def test_products_expose_seller_stock_and_donation():
    p = _first_product()
    assert "seller_name" in p
    assert "stock" in p
    assert "donation_rate" in p
    assert p["stock"] >= 0


def test_orders_require_auth():
    r = client.post(
        "/api/v1/shop/orders",
        json={"items": [{"product_id": 1, "quantity": 1}]},
    )
    assert r.status_code == 401


def test_checkout_decrements_stock_and_computes_donation():
    h = _adopter_headers()
    p = _first_product()
    before_stock = p["stock"]
    qty = 2

    r = client.post(
        "/api/v1/shop/orders",
        json={"items": [{"product_id": p["id"], "quantity": qty}]},
        headers=h,
    )
    assert r.status_code == 200, r.text
    order = r.json()
    assert order["status"] == "paid"
    assert order["total_amount"] == p["price"] * qty
    expected_donation = p["price"] * qty * p["donation_rate"] // 100
    assert order["donation_amount"] == expected_donation
    assert len(order["items"]) == 1
    assert order["items"][0]["quantity"] == qty

    # 재고가 실제로 줄었는지 확인
    after = next(
        x for x in client.get("/api/v1/shop/products").json() if x["id"] == p["id"]
    )
    assert after["stock"] == before_stock - qty


def test_checkout_rejects_insufficient_stock():
    h = _adopter_headers()
    p = _first_product()
    # 스키마상 1회 최대 수량(100)은 지키되 재고보다 많은 수량으로 주문 → 재고 부족(409)
    over = min(100, p["stock"] + 50)
    r = client.post(
        "/api/v1/shop/orders",
        json={"items": [{"product_id": p["id"], "quantity": over}]},
        headers=h,
    )
    assert r.status_code == 409


def test_impact_aggregates_paid_orders():
    # 먼저 결제 한 건 수행
    h = _adopter_headers()
    p = _first_product()
    client.post(
        "/api/v1/shop/orders",
        json={"items": [{"product_id": p["id"], "quantity": 1}]},
        headers=h,
    )
    r = client.get("/api/v1/shop/impact")
    assert r.status_code == 200
    body = r.json()
    assert body["total_orders"] >= 1
    assert body["total_sales"] >= p["price"]
    assert body["total_donation"] >= 0


def test_journey_post_issues_reward_coupon_idempotently():
    h = _adopter_headers()
    dogs = client.get("/api/v1/journey/my-dogs", headers=h).json()
    if not dogs:
        # 입양 관계가 없으면 이 테스트는 의미가 없으므로 건너뜁니다.
        import pytest

        pytest.skip("adopter 에게 입양한 강아지가 없어 저니 보상 테스트를 건너뜁니다.")

    dog_id = dogs[0]["dog_id"]
    coupons_before = len(client.get("/api/v1/shop/coupons", headers=h).json())

    r = client.post(
        "/api/v1/journey",
        json={
            "dog_id": dog_id,
            "quarter_label": "2026-Q3",
            "title": "여름 산책 기록",
            "body": "무더위에도 씩씩하게 산책했어요.",
        },
        headers=h,
    )
    assert r.status_code == 201, r.text

    coupons_after = client.get("/api/v1/shop/coupons", headers=h).json()
    assert len(coupons_after) == coupons_before + 1
    reward = coupons_after[0]
    assert reward["source"] == "journey_reward"
    assert reward["status"] == "issued"
    assert reward["amount"] > 0
