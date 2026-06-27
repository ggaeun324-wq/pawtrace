"""PawTrace Academy 스키마 (교육 콘텐츠/수료/AI 보조).

원칙:
- 퀴즈는 두지 않습니다. 사용자의 학습 피로도를 낮추기 위해 '콘텐츠를 끝까지 읽으면
  수료'하는 가벼운 방식만 사용합니다(점수/시험 없음).
- AI 보조(reflection)는 강아지를 추천하지 않고, 입양 전 '생각해볼 질문/준비사항'만 정리합니다.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CourseSummary(BaseModel):
    """교육 목록 카드용."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    emoji: str | None = None
    summary: str
    order_no: int


class CourseDetail(BaseModel):
    """교육 상세(읽기 콘텐츠). 퀴즈 없음."""

    id: int
    slug: str
    title: str
    emoji: str | None = None
    summary: str
    content: str
    order_no: int


class CompletionOut(BaseModel):
    """수료 배지(사용자별 수료 상태)."""

    model_config = ConfigDict(from_attributes=True)

    course_id: int
    course_title: str
    emoji: str | None = None
    score: int
    total: int
    passed: bool
    completed_at: datetime


class ReflectRequest(BaseModel):
    """입양 전 자기 점검을 위한 자유 서술(주거/생활/계획 등)."""

    situation: str = Field(min_length=1, max_length=1000)


class ReflectResponse(BaseModel):
    """AI 보조 결과 — 추천이 아니라 '생각해볼 질문 + 준비사항'."""

    questions: list[str]
    checklist: list[str]
    note: str
