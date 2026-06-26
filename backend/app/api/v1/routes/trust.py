"""Trust Profile 라우트.

- 본인용(로그인 필요):
  GET  /trust/me/profile      내 프로필 조회
  PUT  /trust/me/profile      내 프로필 저장
  GET  /trust/me/checklist    내 체크리스트 조회
  PUT  /trust/me/checklist    내 체크리스트 저장
  GET  /trust/me              내 Trust Profile 미리보기

- 보호소/관리자용(역할 제한):
  GET  /trust/users/{user_id} 특정 사용자의 Trust Profile 열람

원칙: 일반 사용자는 타인의 Trust Profile 을 볼 수 없습니다.
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, require_role
from app.db.session import get_db
from app.domain import UserRole
from app.models import User
from app.schemas.trust import (
    ChecklistIn,
    ChecklistOut,
    ProfileIn,
    ProfileOut,
    TrustProfile,
)
from app.services import trust_service

router = APIRouter()

StaffUser = Annotated[User, Depends(require_role(UserRole.shelter_staff, UserRole.admin))]


@router.get("/me/profile", response_model=ProfileOut)
def get_my_profile(current: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return trust_service.get_profile(db, current)


@router.put("/me/profile", response_model=ProfileOut)
def save_my_profile(
    data: ProfileIn, current: CurrentUser, db: Annotated[Session, Depends(get_db)]
):
    return trust_service.save_profile(db, current, data.model_dump())


@router.get("/me/checklist", response_model=ChecklistOut)
def get_my_checklist(current: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return trust_service.get_checklist(db, current)


@router.put("/me/checklist", response_model=ChecklistOut)
def save_my_checklist(
    data: ChecklistIn, current: CurrentUser, db: Annotated[Session, Depends(get_db)]
):
    return trust_service.save_checklist(db, current, data.model_dump())


@router.get("/me", response_model=TrustProfile)
def my_trust_profile(current: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return trust_service.build_trust_profile(db, current)


@router.get("/users/{user_id}", response_model=TrustProfile)
def trust_profile_for_staff(
    user_id: int, staff: StaffUser, db: Annotated[Session, Depends(get_db)]
):
    return trust_service.get_trust_profile_for_staff(db, user_id)
