"""PawTrace Academy 라우트.

- GET  /academy/courses            교육 목록(공개)
- GET  /academy/courses/{id}       교육 상세 + 퀴즈(정답 제외, 공개)
- POST /academy/courses/{id}/submit 퀴즈 제출/채점 + 수료 기록(로그인 필요)
- GET  /academy/me                 내 수료 배지 목록(로그인 필요)
- POST /academy/reflect            입양 전 자기 점검 보조(AI, 추천 아님)
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
    QuizResult,
    QuizSubmission,
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


@router.post("/courses/{course_id}/submit", response_model=QuizResult)
def submit_quiz(
    course_id: int,
    submission: QuizSubmission,
    current: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    return academy_service.grade_quiz(db, course_id, submission, current)
