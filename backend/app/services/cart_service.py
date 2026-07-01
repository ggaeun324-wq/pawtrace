"""장바구니 서비스 (PostgreSQL 영속 장바구니).

- 사용자당 활성 장바구니 1개(Cart). 항목은 (cart, product) 유일.
- 결제(checkout)는 기존 shop_service.create_order 를 재사용해 재고 차감·후원 계산·
  쿠폰 적용을 '하나의 트랜잭션'으로 처리하고, 성공하면 장바구니를 비웁니다.
"""
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Cart, CartItem, Product
from app.schemas.shop import (
    CartItemOut,
    CartOut,
    OrderCreateIn,
    OrderItemIn,
    OrderOut,
)
from app.services import shop_service


def _get_or_create_cart(db: Session, user) -> Cart:
    cart = db.scalar(select(Cart).where(Cart.user_id == user.id))
    if cart is None:
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def _to_out(db: Session, cart: Cart) -> CartOut:
    items: list[CartItemOut] = []
    subtotal = 0
    donation = 0
    for it in sorted(cart.items, key=lambda x: x.product_id):
        p = it.product
        if p is None:
            continue
        line = p.price * it.quantity
        subtotal += line
        donation += line * p.donation_rate // 100
        items.append(
            CartItemOut(
                product_id=p.id,
                name=p.name,
                unit_price=p.price,
                quantity=it.quantity,
                line_total=line,
                image_url=p.image_url,
                donation_rate=p.donation_rate,
            )
        )
    return CartOut(
        items=items,
        count=len(items),
        subtotal=subtotal,
        estimated_donation=donation,
    )


def get_cart(db: Session, user) -> CartOut:
    return _to_out(db, _get_or_create_cart(db, user))


def add_item(db: Session, user, product_id: int, quantity: int) -> CartOut:
    product = db.get(Product, product_id)
    if product is None or not product.is_active:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없어요.")
    cart = _get_or_create_cart(db, user)
    item = db.scalar(
        select(CartItem).where(
            CartItem.cart_id == cart.id, CartItem.product_id == product_id
        )
    )
    new_qty = (item.quantity if item else 0) + quantity
    # 담을 수 있는 최대 수량은 현재 재고까지로 안내(재고 초과 담기 방지)
    if product.stock <= 0:
        raise HTTPException(status_code=409, detail=f"'{product.name}' 은 지금 품절이에요.")
    new_qty = min(new_qty, product.stock)
    if item:
        item.quantity = new_qty
    else:
        db.add(CartItem(cart_id=cart.id, product_id=product_id, quantity=new_qty))
    db.commit()
    db.refresh(cart)
    return _to_out(db, cart)


def update_item(db: Session, user, product_id: int, quantity: int) -> CartOut:
    cart = _get_or_create_cart(db, user)
    item = db.scalar(
        select(CartItem).where(
            CartItem.cart_id == cart.id, CartItem.product_id == product_id
        )
    )
    if item is None:
        raise HTTPException(status_code=404, detail="장바구니에 없는 상품이에요.")
    if quantity <= 0:
        db.delete(item)
    else:
        product = db.get(Product, product_id)
        item.quantity = min(quantity, product.stock) if product else quantity
    db.commit()
    db.refresh(cart)
    return _to_out(db, cart)


def remove_item(db: Session, user, product_id: int) -> CartOut:
    cart = _get_or_create_cart(db, user)
    item = db.scalar(
        select(CartItem).where(
            CartItem.cart_id == cart.id, CartItem.product_id == product_id
        )
    )
    if item is not None:
        db.delete(item)
        db.commit()
    db.refresh(cart)
    return _to_out(db, cart)


def clear_cart(db: Session, user) -> CartOut:
    cart = _get_or_create_cart(db, user)
    for it in list(cart.items):
        db.delete(it)
    db.commit()
    db.refresh(cart)
    return _to_out(db, cart)


def checkout(db: Session, user, coupon_code: str | None) -> OrderOut:
    """장바구니 전체를 결제합니다(재고/후원/쿠폰은 create_order 로직 재사용)."""
    cart = _get_or_create_cart(db, user)
    if not cart.items:
        raise HTTPException(status_code=400, detail="장바구니가 비어 있어요.")
    order_in = OrderCreateIn(
        items=[
            OrderItemIn(product_id=it.product_id, quantity=it.quantity)
            for it in cart.items
        ],
        coupon_code=coupon_code,
    )
    order = shop_service.create_order(db, user, order_in)
    # 결제 성공 → 장바구니 비우기
    for it in list(cart.items):
        db.delete(it)
    db.commit()
    return order
