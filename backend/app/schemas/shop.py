"""쇼핑몰 스키마 (요청/응답 형태 정의)."""
from pydantic import BaseModel, ConfigDict


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
