"""쇼핑몰 라우트.

- GET  /shop/products   상품 목록(공개). ?category= 로 분류 필터.
- POST /shop/orders     결제(로그인). 재고 차감 + 후원 적립 + (선택) 쿠폰 사용.
- GET  /shop/orders     내 주문 내역(로그인).
- GET  /shop/coupons    내 쿠폰(로그인).
- GET  /shop/impact     누적 판매/후원 적립(공개, 미션 지표).
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import CurrentUser
from app.db.session import get_db
from app.schemas.shop import (
    CartItemIn,
    CartItemUpdateIn,
    CartOut,
    CheckoutIn,
    CouponOut,
    ImpactOut,
    OrderCreateIn,
    OrderOut,
    ProductOut,
)
from app.services import cart_service, coupon_service, shop_service

router = APIRouter()


@router.get("/products", response_model=list[ProductOut])
def list_products(
    db: Annotated[Session, Depends(get_db)], category: str | None = None
):
    return shop_service.list_products(db, category=category)


@router.get("/impact", response_model=ImpactOut)
def impact(db: Annotated[Session, Depends(get_db)]):
    return shop_service.impact(db)


@router.post("/orders", response_model=OrderOut)
def create_order(
    data: OrderCreateIn,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    return shop_service.create_order(db, user, data)


@router.get("/orders", response_model=list[OrderOut])
def list_orders(
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    return shop_service.list_my_orders(db, user)


@router.get("/coupons", response_model=list[CouponOut])
def list_coupons(
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    return coupon_service.list_my_coupons(db, user)


# ── 장바구니(Cart) ──
@router.get("/cart", response_model=CartOut)
def get_cart(user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return cart_service.get_cart(db, user)


@router.post("/cart/items", response_model=CartOut)
def add_cart_item(
    data: CartItemIn,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    return cart_service.add_item(db, user, data.product_id, data.quantity)


@router.put("/cart/items/{product_id}", response_model=CartOut)
def update_cart_item(
    product_id: int,
    data: CartItemUpdateIn,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    return cart_service.update_item(db, user, product_id, data.quantity)


@router.delete("/cart/items/{product_id}", response_model=CartOut)
def remove_cart_item(
    product_id: int,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    return cart_service.remove_item(db, user, product_id)


@router.delete("/cart", response_model=CartOut)
def clear_cart(user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return cart_service.clear_cart(db, user)


@router.post("/cart/checkout", response_model=OrderOut)
def checkout_cart(
    data: CheckoutIn,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    return cart_service.checkout(db, user, data.coupon_code)
