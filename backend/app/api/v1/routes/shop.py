"""쇼핑몰 라우트.

- GET /shop/products            상품 목록(공개). ?category= 로 분류 필터.

MVP 범위: 상품 진열만 제공합니다(장바구니/결제 없음).
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.shop import ProductOut
from app.services import shop_service

router = APIRouter()


@router.get("/products", response_model=list[ProductOut])
def list_products(
    db: Annotated[Session, Depends(get_db)], category: str | None = None
):
    return shop_service.list_products(db, category=category)
