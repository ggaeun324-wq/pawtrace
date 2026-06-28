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
    shelters = db.scalars(stmt).all()
    if region:
        # 시·도 단축명(예: "서울")으로 들어오면 "서울특별시 마포구" 등도 포함되도록
        # 정규화 비교로 필터링합니다(홈 지도 집계와 상세 목록의 수가 일치).
        key = _normalize_region(region) or region
        shelters = [s for s in shelters if (_normalize_region(s.region) or s.region) == key]
    return [_to_dict(s, count_available_dogs(db, s.id)) for s in shelters]


def get_shelter(db: Session, shelter_id: int) -> dict | None:
    shelter = db.get(Shelter, shelter_id)
    if not shelter:
        return None
    return _to_dict(shelter, count_available_dogs(db, shelter_id))


# 시·도 식별용 접두사 → 단축명. 긴 형태("충청북도")를 짧은 형태("충북") 앞에 둬
# startswith 매칭이 더 구체적인 것부터 잡히도록 정렬합니다.
_REGION_PREFIXES = [
    ("서울", "서울"), ("부산", "부산"), ("대구", "대구"), ("인천", "인천"),
    ("광주", "광주"), ("대전", "대전"), ("울산", "울산"), ("세종", "세종"),
    ("경기", "경기"), ("강원", "강원"),
    ("충청북", "충북"), ("충북", "충북"), ("충청남", "충남"), ("충남", "충남"),
    ("전라북", "전북"), ("전북", "전북"), ("전라남", "전남"), ("전남", "전남"),
    ("경상북", "경북"), ("경북", "경북"), ("경상남", "경남"), ("경남", "경남"),
    ("제주", "제주"),
]


def _normalize_region(region: str | None) -> str | None:
    """'서울특별시 마포구' / '경기도 성남시' → '서울' / '경기' 같은 시·도 단축명."""
    if not region:
        return None
    token = region.split()[0]
    for prefix, short in _REGION_PREFIXES:
        if token.startswith(prefix):
            return short
    return None


def region_counts(db: Session) -> list[dict]:
    """시·도별 보호소 수 + 입양가능 강아지 수 집계(홈 지도용)."""
    avail = (
        select(Dog.shelter_id, func.count(Dog.id).label("c"))
        .where(Dog.adoption_status == AdoptionStatus.available)
        .group_by(Dog.shelter_id)
        .subquery()
    )
    rows = db.execute(
        select(Shelter.region, func.coalesce(avail.c.c, 0))
        .outerjoin(avail, avail.c.shelter_id == Shelter.id)
    ).all()

    agg: dict[str, dict] = {}
    for region, dog_count in rows:
        key = _normalize_region(region)
        if key is None:
            continue
        item = agg.setdefault(
            key, {"region": key, "shelter_count": 0, "available_dog_count": 0}
        )
        item["shelter_count"] += 1
        item["available_dog_count"] += int(dog_count or 0)
    return list(agg.values())


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
