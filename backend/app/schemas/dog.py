"""강아지 / Pet Passport 응답 스키마.

프론트 화면(오늘의 친구, Pet Passport)이 필요로 하는 필드와 1:1 매칭됩니다.
추정값은 항상 estimate 플래그로 표기 → UX에서 '추정' 배지 노출.
"""
from datetime import date

from pydantic import BaseModel

from app.domain import AdoptionStatus, DataSource, PassportEventType


class DogBase(BaseModel):
    id: int
    name: str
    breed_label: str | None = None       # 예: "믹스(추정)"
    breed_is_estimate: bool = True
    age_estimate: str | None = None      # 예: "추정 2살"
    gender: str | None = None            # male / female / unknown
    is_neutered: bool | None = None
    adoption_status: AdoptionStatus
    shelter_id: int
    shelter_name: str
    thumbnail_url: str | None = None


class DogToday(DogBase):
    """홈 '오늘의 친구' 카드용. 짧은 스토리 포함."""
    story: str


class HappyDog(DogBase):
    """해피엔딩(입양 완료) 카드용. 따뜻한 스토리 포함."""
    story: str


class UrgentDog(DogBase):
    """'지금 가족이 필요한 아이들' 카드용.
    보호 공고 마감일이 가까운 순으로 노출합니다(days_left = 마감까지 남은 일수).
    """
    story: str
    protect_end_date: date | None = None
    days_left: int | None = None


class PassportEvent(BaseModel):
    event_type: PassportEventType
    event_date: date | None = None
    title: str
    memo: str | None = None
    source: DataSource                   # 출처 표기("보호소 기록" 등)


class DogPassport(DogBase):
    story: str
    events: list[PassportEvent]
