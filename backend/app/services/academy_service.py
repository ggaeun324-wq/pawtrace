"""Academy 비즈니스 로직 (교육 목록/상세, 콘텐츠 수료, AI 보조).

퀴즈는 제공하지 않습니다. 사용자가 콘텐츠를 끝까지 읽고 '수료하기'를 누르면
수료로 기록합니다(시험/점수 없음). 수료 기록은 Trust Profile 의 교육 배지로 쓰입니다.
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.integrations import ai
from app.models import User
from app.repositories import academy_repository as repo
from app.schemas.academy import (
    CompletionOut,
    CourseDetail,
    CourseSummary,
    ReflectResponse,
)


def list_courses(db: Session) -> list[CourseSummary]:
    out: list[CourseSummary] = []
    for c in repo.list_courses(db):
        out.append(
            CourseSummary(
                id=c.id,
                slug=c.slug,
                title=c.title,
                emoji=c.emoji,
                summary=c.summary,
                order_no=c.order_no,
            )
        )
    return out


def get_course_detail(db: Session, course_id: int) -> CourseDetail:
    c = repo.get_course(db, course_id)
    if c is None:
        raise HTTPException(status_code=404, detail="교육 과정을 찾을 수 없어요.")
    return CourseDetail(
        id=c.id,
        slug=c.slug,
        title=c.title,
        emoji=c.emoji,
        summary=c.summary,
        content=c.content,
        order_no=c.order_no,
    )


def complete_course(db: Session, course_id: int, user: User) -> CompletionOut:
    """콘텐츠를 끝까지 읽은 사용자를 수료로 기록(시험 없음)."""
    c = repo.get_course(db, course_id)
    if c is None:
        raise HTTPException(status_code=404, detail="교육 과정을 찾을 수 없어요.")
    # 점수 개념이 없으므로 score/total=0, passed=True 로 '수료' 상태만 저장합니다.
    comp = repo.upsert_completion(
        db, user_id=user.id, course_id=course_id, score=0, total=0, passed=True
    )
    return CompletionOut(
        course_id=comp.course_id,
        course_title=c.title,
        emoji=c.emoji,
        score=comp.score,
        total=comp.total,
        passed=comp.passed,
        completed_at=comp.completed_at,
    )


def my_completions(db: Session, user: User) -> list[CompletionOut]:
    out: list[CompletionOut] = []
    for comp in repo.list_completions(db, user.id):
        out.append(
            CompletionOut(
                course_id=comp.course_id,
                course_title=comp.course.title,
                emoji=comp.course.emoji,
                score=comp.score,
                total=comp.total,
                passed=comp.passed,
                completed_at=comp.completed_at,
            )
        )
    return out


def reflect(situation: str) -> ReflectResponse:
    """입양 전 자기 점검 보조(추천 아님). ai.adoption_reflection 사용."""
    data = ai.adoption_reflection(situation)
    return ReflectResponse(**data)
