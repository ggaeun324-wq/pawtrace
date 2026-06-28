"""강아지 / Pet Passport 유스케이스."""
from datetime import date

from sqlalchemy.orm import Session

from app.core import cache
from app.repositories import dog_repository as repo
from app.schemas.dog import DogPassport, DogToday, HappyDog, PassportEvent, UrgentDog


def get_today_dog(db: Session) -> DogToday | None:
    row = repo.get_today_dog(db)
    return DogToday(**row) if row else None


def get_happy_endings(db: Session) -> list[HappyDog]:
    return [HappyDog(**row) for row in repo.get_happy_endings(db)]


def get_urgent_dogs(db: Session) -> list[UrgentDog]:
    """보호 마감 임박 강아지 + 남은 일수(days_left) 계산.

    cache-aside 패턴: 먼저 Redis 를 조회하고(히트 시 DB 생략),
    미스면 DB 에서 계산한 뒤 짧은 TTL 로 캐시에 저장합니다.
    Redis 장애 시에도 캐시 모듈이 fail-open 으로 동작하여 DB 폴백됩니다.
    """
    cached = cache.get_json(cache.URGENT_DOGS_KEY)
    if cached is not None:
        return [UrgentDog(**item) for item in cached]

    today = date.today()
    result: list[UrgentDog] = []
    for row in repo.get_urgent_dogs(db):
        end = row.get("protect_end_date")
        days_left = (end - today).days if end else None
        result.append(UrgentDog(**row, days_left=days_left))

    # JSON 직렬화 가능한 형태(date→문자열)로 저장
    cache.set_json(
        cache.URGENT_DOGS_KEY,
        [d.model_dump(mode="json") for d in result],
        cache.URGENT_DOGS_TTL,
    )
    return result


def get_passport(db: Session, dog_id: int) -> DogPassport | None:
    dog = repo.get_dog(db, dog_id)
    if not dog:
        return None
    events = [PassportEvent(**e) for e in repo.get_passport_events(db, dog_id)]
    return DogPassport(**dog, events=events)
