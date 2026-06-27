"""Shelter AI Assistant 라우트 (보호소 직원/관리자 전용).

- POST /shelter/dogs/ai-draft  사진(+힌트) → 소개 초안 생성(저장 안 함)
- POST /shelter/dogs           직원이 확인/수정한 강아지 저장
- GET  /shelter/dogs           담당 보호소 강아지 목록

권한: shelter_staff, admin 만 접근할 수 있습니다.
AI 초안을 그대로 자동 게시하지 않고, 반드시 직원이 저장 단계를 거칩니다.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.security import require_role
from app.db.session import get_db
from app.domain import UserRole
from app.models import User
from app.schemas.shelter_ai import DogCreateIn, DogDraft, DogOut
from app.services import shelter_ai_service

router = APIRouter()

StaffUser = Annotated[User, Depends(require_role(UserRole.shelter_staff, UserRole.admin))]


@router.post("/dogs/ai-draft", response_model=DogDraft)
async def ai_draft(
    staff: StaffUser,
    photo: Annotated[UploadFile | None, File()] = None,
    name: Annotated[str | None, Form()] = None,
    breed_hint: Annotated[str | None, Form()] = None,
    color_hint: Annotated[str | None, Form()] = None,
    temperament_hint: Annotated[str | None, Form()] = None,
):
    """사진과 힌트로 소개 초안을 생성합니다. 저장하지 않습니다(미리보기)."""
    photo_bytes = await photo.read() if photo is not None else None
    filename = photo.filename if photo is not None else None
    hints = {
        "name": name,
        "breed_hint": breed_hint,
        "color_hint": color_hint,
        "temperament_hint": temperament_hint,
    }
    return shelter_ai_service.generate_draft(hints, photo_bytes, filename)


@router.post("/dogs", response_model=DogOut, status_code=201)
def create_dog(
    data: DogCreateIn, staff: StaffUser, db: Annotated[Session, Depends(get_db)]
):
    """직원이 확인/수정한 강아지를 입양 가능 상태로 저장합니다."""
    return shelter_ai_service.create_dog(db, staff, data)


@router.get("/dogs", response_model=list[DogOut])
def list_dogs(
    staff: StaffUser,
    db: Annotated[Session, Depends(get_db)],
    shelter_id: int | None = None,
):
    """담당 보호소(또는 admin 이 지정한 보호소)의 강아지 목록."""
    return shelter_ai_service.list_shelter_dogs(db, staff, shelter_id)
