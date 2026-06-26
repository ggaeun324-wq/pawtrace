"""강아지 저장소 (DB 백엔드).

Repository 패턴: 데이터 접근을 한 곳에 가둡니다. 상위(service/schema)는
여기서 돌려주는 dict 의 '키 계약'만 알면 되고, 내부가 seed 든 DB 든 신경쓰지 않습니다.
→ 그래서 seed.py 에서 SQLAlchemy 로 바꿔도 service/schema 는 수정이 없습니다.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain import AdoptionStatus
from app.models import Dog, PassportEvent


def get_today_dog(db: Session) -> dict | None:
    """홈 '오늘의 친구'. MVP 는 첫 입양가능 강아지를 반환.
    날짜 시드 기반 회전 로직(#110)은 Sprint 2 에서 service 레이어로 옮깁니다.
    """
    dog = db.scalars(
        select(Dog).where(Dog.adoption_status == AdoptionStatus.available).order_by(Dog.id)
    ).first()
    return _to_dict(dog) if dog else None


def get_happy_endings(db: Session, limit: int = 12) -> list[dict]:
    """해피엔딩: 입양 완료(adopted) 강아지 목록. 최근 입양순(id 역순)."""
    dogs = db.scalars(
        select(Dog)
        .where(Dog.adoption_status == AdoptionStatus.adopted)
        .order_by(Dog.id.desc())
        .limit(limit)
    ).all()
    return [_to_dict(d) for d in dogs]


def get_urgent_dogs(db: Session, limit: int = 12) -> list[dict]:
    """보호 마감일이 임박한 입양가능 강아지. 마감 빠른 순으로."""
    dogs = db.scalars(
        select(Dog)
        .where(
            Dog.adoption_status == AdoptionStatus.available,
            Dog.protect_end_date.is_not(None),
        )
        .order_by(Dog.protect_end_date, Dog.id)
        .limit(limit)
    ).all()
    return [_to_dict(d) for d in dogs]


def get_dog(db: Session, dog_id: int) -> dict | None:
    dog = db.get(Dog, dog_id)
    return _to_dict(dog) if dog else None


def get_passport_events(db: Session, dog_id: int) -> list[dict]:
    """타임라인. 날짜 오름차순, 날짜가 없는 항목(예: '입양 가능')은 맨 뒤로."""
    events = db.scalars(
        select(PassportEvent)
        .where(PassportEvent.dog_id == dog_id)
        .order_by(PassportEvent.event_date.is_(None), PassportEvent.event_date, PassportEvent.id)
    ).all()
    return [
        {
            "event_type": e.event_type,
            "event_date": e.event_date,
            "title": e.title,
            "memo": e.memo,
            "source": e.source,
        }
        for e in events
    ]


def _to_dict(dog: Dog) -> dict:
    """ORM 객체 → 스키마가 기대하는 dict (키 계약 유지)."""
    return {
        "id": dog.id,
        "name": dog.name,
        "breed_label": dog.breed_label,
        "breed_is_estimate": dog.breed_is_estimate,
        "age_estimate": dog.age_estimate,
        "gender": dog.gender,
        "is_neutered": dog.is_neutered,
        "adoption_status": dog.adoption_status,
        "shelter_id": dog.shelter_id,
        "shelter_name": dog.shelter.name if dog.shelter else "",
        "thumbnail_url": dog.thumbnail_url,
        "story": dog.story or "",
        "protect_end_date": dog.protect_end_date,
    }
