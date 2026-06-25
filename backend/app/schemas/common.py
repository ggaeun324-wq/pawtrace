"""공통 응답 스키마 (페이지네이션, 에러)."""
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    page: int
    size: int
    total: int


class ErrorResponse(BaseModel):
    code: str
    message: str
