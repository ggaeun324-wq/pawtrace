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
    CouponOut,
    ImpactOut,
    OrderCreateIn,
    OrderOut,
    ProductOut,
)
from app.services import coupon_service, shop_service

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
