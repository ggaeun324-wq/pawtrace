"""공공데이터 동기화 서비스.

흐름: fetch_animals(공공 API) → upsert_records(DB 멱등 반영).
- 보호소: (source=public_api, external_id=보호소명) 기준 upsert.
- 강아지: (source=public_api, external_id=유기번호) 기준 upsert.
멱등이므로 같은 데이터를 여러 번 동기화해도 중복이 생기지 않습니다.
"""
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import cache
from app.domain import DataSource, TransparencyLevel
from app.integrations import geocoding, public_data
from app.models import Dog, Shelter


def _to_date(value: str | None) -> date | None:
    """ISO 'YYYY-MM-DD' 문자열 → date. 비거나 형식 오류면 None."""
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _upsert_shelter(db: Session, data: dict) -> Shelter:
    ext = data["external_id"]
    shelter = db.scalars(
        select(Shelter).where(
            Shelter.source == DataSource.public_api, Shelter.external_id == ext
        )
    ).first()
    if shelter is None:
        shelter = Shelter(
            source=DataSource.public_api,
            external_id=ext,
            transparency_level=TransparencyLevel.unverified,
        )
        db.add(shelter)
    shelter.name = data["name"]
    shelter.region = data["region"]
    shelter.address = data.get("address")
    shelter.phone = data.get("phone")
    # 좌표가 아직 없고 주소가 있으면 카카오 지오코딩으로 위경도를 채웁니다.
    # (키 없음/실패 시 None → 지도에는 안 찍히지만 동기화는 계속 진행)
    if shelter.lat is None and shelter.address:
        coord = geocoding.geocode(shelter.address)
        if coord is not None:
            shelter.lat, shelter.lng = coord
            # PostGIS POINT(경도 위도) — 향후 반경검색(ST_DWithin)에 사용
            shelter.location = f"SRID=4326;POINT({shelter.lng} {shelter.lat})"
    db.flush()  # id 확보
    return shelter


def _upsert_dog(db: Session, shelter_id: int, data: dict) -> bool:
    """반환: 신규 생성이면 True."""
    ext = data.get("external_id")
    dog = None
    if ext:
        dog = db.scalars(
            select(Dog).where(
                Dog.source == DataSource.public_api, Dog.external_id == ext
            )
        ).first()
    created = dog is None
    if dog is None:
        dog = Dog(source=DataSource.public_api, external_id=ext)
        db.add(dog)
    dog.shelter_id = shelter_id
    dog.name = data["name"]
    dog.breed_label = data.get("breed_label")
    dog.breed_is_estimate = True  # 공공데이터 품종은 추정으로 표기
    dog.gender = data.get("gender")
    dog.is_neutered = data.get("is_neutered")
    dog.adoption_status = data["adoption_status"]
    dog.thumbnail_url = data.get("thumbnail_url")
    dog.story = data.get("story")
    dog.protect_end_date = _to_date(data.get("protect_end_date"))
    return created


def upsert_records(db: Session, records: list[dict]) -> dict:
    """파싱된 레코드 목록을 DB 에 멱등 반영하고 집계를 반환."""
    shelters_seen: set[str] = set()
    dogs_created = 0
    dogs_total = 0
    try:
        for rec in records:
            shelter = _upsert_shelter(db, rec["shelter"])
            shelters_seen.add(rec["shelter"]["external_id"])
            if _upsert_dog(db, shelter.id, rec["dog"]):
                dogs_created += 1
            dogs_total += 1
        db.commit()
    except Exception:
        db.rollback()
        raise
    # 강아지 데이터가 바뀌었으니 '오늘의 공고' 캐시를 무효화합니다.
    cache.delete(cache.URGENT_DOGS_KEY)
    return {
        "shelters_upserted": len(shelters_seen),
        "dogs_total": dogs_total,
        "dogs_created": dogs_created,
        "dogs_updated": dogs_total - dogs_created,
    }


def sync_public_data(
    db: Session,
    *,
    begin: str | None = None,
    end: str | None = None,
    rows: int = 50,
    page: int = 1,
) -> dict:
    """공공 API 에서 가져와 DB 에 반영. 결과 집계 + 연동 가능 여부 포함."""
    records = public_data.fetch_animals(begin=begin, end=end, rows=rows, page=page)
    result = upsert_records(db, records)
    result["source_enabled"] = public_data.is_enabled()
    return result
