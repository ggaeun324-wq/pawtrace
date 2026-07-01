"""쇼핑몰 스키마 (요청/응답 형태 정의)."""
from pydantic import BaseModel, ConfigDict, Field

from app.domain import CouponStatus, OrderStatus


class ProductOut(BaseModel):
    """상품 진열 응답."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    price: int
    image_url: str | None = None
    description: str | None = None
    supports_shelter: bool = False
    stock: int = 0
    donation_rate: int = 0          # 판매액 중 보호소 후원 비율(%)
    seller_id: int | None = None
    seller_name: str | None = None  # 서비스에서 채움


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1, le=100)


class OrderCreateIn(BaseModel):
    """결제 요청 — 상품 목록 + (선택) 쿠폰 코드."""

    items: list[OrderItemIn] = Field(min_length=1)
    coupon_code: str | None = None


class OrderItemOut(BaseModel):
    product_id: int
    name: str
    quantity: int
    unit_price: int


class OrderOut(BaseModel):
    id: int
    status: OrderStatus
    total_amount: int
    discount_amount: int
    donation_amount: int
    items: list[OrderItemOut]


class CouponOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    amount: int
    status: CouponStatus
    source: str | None = None


class ImpactOut(BaseModel):
    """미션 지표 — 누적 판매/후원 적립(공개)."""

    total_orders: int = 0
    total_sales: int = 0     # 결제 완료 주문 총액(원)
    total_donation: int = 0  # 보호소 후원 누적 적립(원)
