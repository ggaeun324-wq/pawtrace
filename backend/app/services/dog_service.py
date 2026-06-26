"""강아지 / Pet Passport 유스케이스."""
from datetime import date

from sqlalchemy.orm import Session

from app.repositories import dog_repository as repo
from app.schemas.dog import DogPassport, DogToday, HappyDog, PassportEvent, UrgentDog


def get_today_dog(db: Session) -> DogToday | None:
    row = repo.get_today_dog(db)
    return DogToday(**row) if row else None


def get_happy_endings(db: Session) -> list[HappyDog]:
    return [HappyDog(**row) for row in repo.get_happy_endings(db)]


def get_urgent_dogs(db: Session) -> list[UrgentDog]:
    """보호 마감 임박 강아지 + 남은 일수(days_left) 계산."""
    today = date.today()
    result: list[UrgentDog] = []
    for row in repo.get_urgent_dogs(db):
        end = row.get("protect_end_date")
        days_left = (end - today).days if end else None
        result.append(UrgentDog(**row, days_left=days_left))
    return result


def get_passport(db: Session, dog_id: int) -> DogPassport | None:
    dog = repo.get_dog(db, dog_id)
    if not dog:
        return None
    events = [PassportEvent(**e) for e in repo.get_passport_events(db, dog_id)]
    return DogPassport(**dog, events=events)
