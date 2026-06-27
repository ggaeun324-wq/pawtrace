"""Family Journey 라우트.

- GET  /journey/me              내 반려생활 기록(타임라인, 로그인 필요)
- GET  /journey/my-dogs         내가 입양한 강아지 목록(작성 대상, 로그인 필요)
- POST /journey                 기록 작성(입양자만)
- POST /journey/draft           AI 글쓰기 초안(메모 정리, 추천/판단 아님)
- GET  /journey/dog/{dog_id}    특정 강아지의 공개 타임라인
- POST /journey/{entry_id}/cheer 응원 누르기(로그인 필요, 댓글 없음)
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import CurrentUser
from app.db.session import get_db
from app.schemas.journey import (
    CheerOut,
    JourneyDraftIn,
    JourneyDraftOut,
    JourneyIn,
    JourneyOut,
)
from app.services import journey_service

router = APIRouter()


@router.get("/me", response_model=list[JourneyOut])
def my_journey(current: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return journey_service.list_my_entries(db, current)


@router.get("/my-dogs")
def my_dogs(current: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return journey_service.my_adopted_dogs(db, current)


@router.post("/draft", response_model=JourneyDraftOut)
def journey_draft(data: JourneyDraftIn, _current: CurrentUser):
    return journey_service.draft(data.memo, data.dog_name)


@router.post("", response_model=JourneyOut, status_code=201)
def create_journey(
    data: JourneyIn, current: CurrentUser, db: Annotated[Session, Depends(get_db)]
):
    return journey_service.create_entry(db, current, data)


@router.get("/dog/{dog_id}", response_model=list[JourneyOut])
def dog_journey(dog_id: int, db: Annotated[Session, Depends(get_db)]):
    return journey_service.list_for_dog(db, dog_id)


@router.post("/{entry_id}/cheer", response_model=CheerOut)
def cheer(
    entry_id: int, _current: CurrentUser, db: Annotated[Session, Depends(get_db)]
):
    entry = journey_service.cheer(db, entry_id)
    return CheerOut(id=entry.id, cheers=entry.cheers)
