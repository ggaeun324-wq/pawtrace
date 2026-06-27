"""PawTrace Academy 라우트.

- GET  /academy/courses            교육 목록(공개)
- GET  /academy/courses/{id}       교육 상세 콘텐츠(공개)
- POST /academy/courses/{id}/complete 콘텐츠 수료 처리 + 배지 기록(로그인 필요)
- GET  /academy/me                 내 수료 배지 목록(로그인 필요)
- POST /academy/reflect            입양 전 자기 점검 보조(AI, 추천 아님)

퀴즈는 제공하지 않습니다(학습 피로도 완화). 콘텐츠를 끝까지 읽으면 수료로 인정합니다.
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import CurrentUser
from app.db.session import get_db
from app.schemas.academy import (
    CompletionOut,
    CourseDetail,
    CourseSummary,
    ReflectRequest,
    ReflectResponse,
)
from app.services import academy_service

router = APIRouter()


@router.get("/courses", response_model=list[CourseSummary])
def list_courses(db: Annotated[Session, Depends(get_db)]):
    return academy_service.list_courses(db)


@router.get("/me", response_model=list[CompletionOut])
def my_completions(current: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return academy_service.my_completions(db, current)


@router.post("/reflect", response_model=ReflectResponse)
def reflect(data: ReflectRequest):
    return academy_service.reflect(data.situation)


@router.get("/courses/{course_id}", response_model=CourseDetail)
def course_detail(course_id: int, db: Annotated[Session, Depends(get_db)]):
    return academy_service.get_course_detail(db, course_id)


@router.post("/courses/{course_id}/complete", response_model=CompletionOut)
def complete_course(
    course_id: int,
    current: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    """콘텐츠를 끝까지 읽은 사용자를 수료로 기록(시험 없음)."""
    return academy_service.complete_course(db, course_id, current)
