"""쇼핑몰 서비스 (상품 조회 + 결제/후원 적립 + 임팩트 집계).

설계 포인트(부하테스트 관점):
- 결제(create_order)는 '읽기 위주'인 오늘의 공고와 대비되는 '쓰기·동시성' 워크로드입니다.
- 재고 정합성을 위해 상품 행을 SELECT ... FOR UPDATE 로 잠급니다(동시 결제 경합 처리).
- 미션(수익 일부 후원)을 donation_rate 로 계산해 주문에 적립액을 기록합니다.
"""
from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain import CouponStatus, OrderStatus
from app.models import Coupon, Order, OrderItem, Product
from app.schemas.shop import (
    ImpactOut,
    OrderCreateIn,
    OrderItemOut,
    OrderOut,
    ProductOut,
)


def list_products(db: Session, category: str | None = None) -> list[ProductOut]:
    """활성 상품 목록. category 가 주어지면 해당 분류만 필터링."""
    stmt = select(Product).where(Product.is_active.is_(True))
    if category:
        stmt = stmt.where(Product.category == category)
    stmt = stmt.order_by(Product.id)
    products = db.scalars(stmt).all()
    result: list[ProductOut] = []
    for p in products:
        out = ProductOut.model_validate(p)
        out.seller_name = p.seller.name if p.seller is not None else None
        result.append(out)
    return result


def _order_to_out(order: Order) -> OrderOut:
    return OrderOut(
        id=order.id,
        status=order.status,
        total_amount=order.total_amount,
        discount_amount=order.discount_amount,
        donation_amount=order.donation_amount,
        items=[
            OrderItemOut(
                product_id=it.product_id,
                name=it.product.name,
                quantity=it.quantity,
                unit_price=it.unit_price,
            )
            for it in order.items
        ],
    )


def create_order(db: Session, user, data: OrderCreateIn) -> OrderOut:
    """결제 처리 — 재고 차감 + 후원액 계산 + (선택) 쿠폰 사용을 한 트랜잭션으로.

    동시성: 대상 상품 행을 with_for_update() 로 잠가 재고 초과 판매를 막습니다.
    """
    # 같은 상품이 여러 줄로 오면 합산(중복 방지)
    qty_by_product: dict[int, int] = {}
    for item in data.items:
        qty_by_product[item.product_id] = qty_by_product.get(item.product_id, 0) + item.quantity

    product_ids = list(qty_by_product.keys())
    # 재고 정합성을 위해 행 잠금(FOR UPDATE)
    products = db.scalars(
        select(Product).where(Product.id.in_(product_ids)).with_for_update()
    ).all()
    product_map = {p.id: p for p in products}

    subtotal = 0
    donation_total = 0
    order_items: list[OrderItem] = []
    for pid, qty in qty_by_product.items():
        product = product_map.get(pid)
        if product is None or not product.is_active:
            raise HTTPException(status_code=404, detail=f"상품을 찾을 수 없어요(id={pid}).")
        if product.stock < qty:
            raise HTTPException(
                status_code=409,
                detail=f"'{product.name}' 재고가 부족해요(남은 수량 {product.stock}).",
            )
        product.stock -= qty
        line_total = product.price * qty
        subtotal += line_total
        donation_total += line_total * product.donation_rate // 100
        order_items.append(
            OrderItem(product_id=pid, quantity=qty, unit_price=product.price)
        )

    # 쿠폰 적용(선택) — 본인 소유의 사용 가능한 쿠폰만
    discount = 0
    coupon: Coupon | None = None
    if data.coupon_code:
        coupon = db.scalar(
            select(Coupon)
            .where(
                Coupon.code == data.coupon_code,
                Coupon.user_id == user.id,
                Coupon.status == CouponStatus.issued,
            )
            .with_for_update()
        )
        if coupon is None:
            raise HTTPException(status_code=400, detail="사용할 수 없는 쿠폰이에요.")
        discount = min(coupon.amount, subtotal)

    total = subtotal - discount
    order = Order(
        user_id=user.id,
        status=OrderStatus.paid,
        total_amount=total,
        discount_amount=discount,
        donation_amount=donation_total,
        coupon_id=coupon.id if coupon else None,
        items=order_items,
    )
    if coupon is not None:
        coupon.status = CouponStatus.used
        coupon.used_at = datetime.now(UTC)

    db.add(order)
    db.commit()
    db.refresh(order)
    return _order_to_out(order)


def list_my_orders(db: Session, user) -> list[OrderOut]:
    orders = db.scalars(
        select(Order).where(Order.user_id == user.id).order_by(Order.id.desc())
    ).all()
    return [_order_to_out(o) for o in orders]


def impact(db: Session) -> ImpactOut:
    """누적 판매/후원 적립(결제 완료 기준) — 미션 지표(공개)."""
    row = db.execute(
        select(
            func.count(Order.id),
            func.coalesce(func.sum(Order.total_amount), 0),
            func.coalesce(func.sum(Order.donation_amount), 0),
        ).where(Order.status == OrderStatus.paid)
    ).one()
    return ImpactOut(
        total_orders=int(row[0]), total_sales=int(row[1]), total_donation=int(row[2])
    )
