"""보호소 라우트.

- GET /shelters?region=서울   지역별 보호소 목록 (available_dog_count 포함)
- GET /shelters/{id}          보호소 상세
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.shelter import RegionCount, ShelterDetail, ShelterSummary
from app.services import shelter_service

router = APIRouter()


@router.get("", response_model=list[ShelterSummary])
def list_shelters(db: Annotated[Session, Depends(get_db)], region: str | None = None):
    return shelter_service.list_shelters(db, region)


@router.get("/region-counts", response_model=list[RegionCount])
def region_counts(db: Annotated[Session, Depends(get_db)]):
    """홈 지도용 시·도별 보호소/입양가능 강아지 집계."""
    return shelter_service.region_counts(db)


@router.get("/{shelter_id}", response_model=ShelterDetail)
def get_shelter(shelter_id: int, db: Annotated[Session, Depends(get_db)]):
    shelter = shelter_service.get_shelter(db, shelter_id)
    if not shelter:
        raise HTTPException(status_code=404, detail="보호소를 찾을 수 없어요")
    return shelter
