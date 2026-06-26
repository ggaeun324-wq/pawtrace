"""보호소 저장소 (DB 백엔드).

지역 필터 + '입양 가능 강아지 수' 집계를 제공합니다.
반경검색(PostGIS ST_DWithin)은 Sprint 2 에서 location 컬럼으로 추가합니다.
"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain import AdoptionStatus
from app.models import Dog, Shelter


def count_available_dogs(db: Session, shelter_id: int) -> int:
    return db.scalar(
        select(func.count())
        .select_from(Dog)
        .where(Dog.shelter_id == shelter_id, Dog.adoption_status == AdoptionStatus.available)
    ) or 0


def list_shelters(db: Session, region: str | None = None) -> list[dict]:
    stmt = select(Shelter).order_by(Shelter.id)
    if region:
        stmt = stmt.where(Shelter.region == region)
    shelters = db.scalars(stmt).all()
    return [_to_dict(s, count_available_dogs(db, s.id)) for s in shelters]


def get_shelter(db: Session, shelter_id: int) -> dict | None:
    shelter = db.get(Shelter, shelter_id)
    if not shelter:
        return None
    return _to_dict(shelter, count_available_dogs(db, shelter_id))


def _to_dict(s: Shelter, available_dog_count: int) -> dict:
    """ORM 객체 → 스키마(ShelterDetail/Summary) 키 계약 dict."""
    return {
        "id": s.id,
        "name": s.name,
        "region": s.region,
        "address": s.address,
        "lat": s.lat,
        "lng": s.lng,
        "is_gov_registered": s.is_gov_registered,
        "transparency_level": s.transparency_level,
        "available_dog_count": available_dog_count,
        "description": s.description,
        "phone": s.phone,
        "gov_reg_no": s.gov_reg_no,
    }
