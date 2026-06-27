"""Shelter AI Assistant 스키마 (보호소 직원의 강아지 등록 보조).

원칙:
- AI 결과는 '초안'이며, 직원이 확인/수정 후에만 저장됩니다.
- 외형/품종/성격은 추정(estimate)으로 표기합니다.
"""
from pydantic import BaseModel, ConfigDict, Field

from app.domain import AdoptionStatus


class DogDraft(BaseModel):
    """AI가 생성한 강아지 소개 '초안'(저장 전 미리보기)."""

    breed_label: str
    breed_is_estimate: bool = True
    color: str | None = None
    appearance: str
    intro: str
    personality_keywords: list[str]
    thumbnail_url: str | None = None
    note: str


class DogCreateIn(BaseModel):
    """보호소 직원이 초안을 수정/확인한 뒤 저장하는 입력."""

    name: str = Field(min_length=1, max_length=80)
    breed_label: str | None = Field(default=None, max_length=80)
    breed_is_estimate: bool = True
    age_estimate: str | None = Field(default=None, max_length=40)
    gender: str | None = Field(default=None, max_length=10)  # male/female/unknown
    is_neutered: bool | None = None
    story: str | None = None
    thumbnail_url: str | None = Field(default=None, max_length=300)
    # admin 계정은 담당 보호소가 없을 수 있어 직접 지정할 수 있게 허용(직원은 무시).
    shelter_id: int | None = None


class DogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    breed_label: str | None
    breed_is_estimate: bool
    age_estimate: str | None
    gender: str | None
    is_neutered: bool | None
    adoption_status: AdoptionStatus
    shelter_id: int
    thumbnail_url: str | None
    story: str | None
