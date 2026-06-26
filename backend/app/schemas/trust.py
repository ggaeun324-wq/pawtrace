"""Trust Profile 스키마.

원칙:
- 사람을 합격/불합격으로 판단하거나 점수화하지 않습니다.
- Trust Profile 은 '객관적인 준비 활동'의 모음일 뿐입니다.
- 일반 사용자에게는 타인의 Trust Profile 을 공개하지 않습니다(보호소/관리자 전용).
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProfileIn(BaseModel):
    """사용자 본인이 작성/수정하는 입양 준비 프로필."""

    housing_type: str | None = Field(default=None, max_length=40)
    household: str | None = Field(default=None, max_length=120)
    experience: str | None = Field(default=None, max_length=300)
    daily_hours: str | None = Field(default=None, max_length=40)
    intro: str | None = Field(default=None, max_length=1000)


class ProfileOut(ProfileIn):
    model_config = ConfigDict(from_attributes=True)

    completeness: int = 0  # 작성률(0~100)


class ChecklistIn(BaseModel):
    """입양 준비 체크리스트(본인 체크)."""

    vet_info: bool = False
    budget_ready: bool = False
    space_ready: bool = False
    family_agreed: bool = False
    time_committed: bool = False


class ChecklistOut(ChecklistIn):
    model_config = ConfigDict(from_attributes=True)

    completed_count: int = 0
    total: int = 5


class EducationBadge(BaseModel):
    course_id: int
    course_title: str
    emoji: str | None = None


class TrustProfile(BaseModel):
    """보호소/관리자가 열람하는 통합 준비 현황(점수 아님)."""

    user_id: int
    display_name: str
    joined_at: datetime
    days_since_join: int
    profile_completeness: int
    checklist_completed: int
    checklist_total: int
    education_badges: list[EducationBadge]
    has_life_record: bool          # 반려생활(Family Journey) 기록 여부
    adopted_count: int             # 입양 진행/완료한 강아지 수
    ai_summary: str                # 객관적 활동 요약(평가 아님)
