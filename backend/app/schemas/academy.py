"""PawTrace Academy 스키마 (교육/퀴즈/수료/AI 보조).

원칙:
- 정답(answer_index)은 과정 조회 응답에 절대 포함하지 않습니다(채점 결과에서만 공개).
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
    question_count: int = 0


class QuizQuestionPublic(BaseModel):
    """퀴즈 문항(정답 비공개)."""

    id: int
    question: str
    options: list[str]


class CourseDetail(BaseModel):
    """교육 상세 + 퀴즈 문항(정답 제외)."""

    id: int
    slug: str
    title: str
    emoji: str | None = None
    summary: str
    content: str
    order_no: int
    questions: list[QuizQuestionPublic]


class QuizSubmission(BaseModel):
    """퀴즈 제출. answers[i] = i번째 문항에서 고른 보기 인덱스."""

    answers: list[int] = Field(min_length=1)


class QuizResultItem(BaseModel):
    question_id: int
    correct: bool
    answer_index: int        # 정답(채점 후 공개)
    explanation: str | None = None


class QuizResult(BaseModel):
    course_id: int
    score: int
    total: int
    passed: bool
    results: list[QuizResultItem]


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
