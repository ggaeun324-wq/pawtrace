"""보호소 응답 스키마.

지도 화면이 필요로 하는 transparency_level, available_dog_count 포함.
"""
from pydantic import BaseModel

from app.domain import TransparencyLevel


class ShelterSummary(BaseModel):
    id: int
    name: str
    region: str                       # 시·도 (예: "서울")
    address: str | None = None
    lat: float | None = None
    lng: float | None = None
    is_gov_registered: bool = False
    transparency_level: TransparencyLevel
    available_dog_count: int = 0      # 지도 카드의 "입양 가능 N마리"


class ShelterDetail(ShelterSummary):
    description: str | None = None
    phone: str | None = None
    gov_reg_no: str | None = None
