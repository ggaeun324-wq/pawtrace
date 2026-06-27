"""Shelter Applicant Review 스키마 (보호소 직원이 보는 입양 신청자 목록).

원칙:
- 신청자의 '준비 활동'을 객관적으로 보여줄 뿐, 합격/불합격을 판단하지 않습니다.
- AI 는 추천/비추천 표현을 하지 않고 활동 요약만 제공합니다.
"""
from datetime import datetime

from pydantic import BaseModel

from app.domain import ApplicationStatus


class ApplicantSummary(BaseModel):
    """신청자 1명 + 신청 1건의 요약(Trust Profile 핵심값 포함)."""

    application_id: int
    status: ApplicationStatus
    message: str | None
    created_at: datetime
    dog_id: int
    dog_name: str
    user_id: int
    applicant_name: str
    profile_completeness: int
    checklist_completed: int
    checklist_total: int
    education_count: int
    ai_summary: str
