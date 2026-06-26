"""보호소 라우트.

- GET /shelters?region=서울   지역별 보호소 목록 (available_dog_count 포함)
- GET /shelters/{id}          보호소 상세
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.shelter import ShelterDetail, ShelterSummary
from app.services import shelter_service

router = APIRouter()


@router.get("", response_model=list[ShelterSummary])
def list_shelters(db: Annotated[Session, Depends(get_db)], region: str | None = None):
    return shelter_service.list_shelters(db, region)


@router.get("/{shelter_id}", response_model=ShelterDetail)
def get_shelter(shelter_id: int, db: Annotated[Session, Depends(get_db)]):
    shelter = shelter_service.get_shelter(db, shelter_id)
    if not shelter:
        raise HTTPException(status_code=404, detail="보호소를 찾을 수 없어요")
    return shelter
