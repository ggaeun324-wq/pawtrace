"""쇼핑몰 서비스 (상품 조회).

MVP 범위: 활성 상품 진열만 합니다(장바구니/결제 없음).
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Product


def list_products(db: Session, category: str | None = None) -> list[Product]:
    """활성 상품 목록. category 가 주어지면 해당 분류만 필터링."""
    stmt = select(Product).where(Product.is_active.is_(True))
    if category:
        stmt = stmt.where(Product.category == category)
    stmt = stmt.order_by(Product.id)
    return list(db.scalars(stmt).all())
