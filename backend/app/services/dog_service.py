"""강아지 / Pet Passport 유스케이스."""
from sqlalchemy.orm import Session

from app.repositories import dog_repository as repo
from app.schemas.dog import DogPassport, DogToday, HappyDog, PassportEvent


def get_today_dog(db: Session) -> DogToday | None:
    row = repo.get_today_dog(db)
    return DogToday(**row) if row else None


def get_happy_endings(db: Session) -> list[HappyDog]:
    return [HappyDog(**row) for row in repo.get_happy_endings(db)]


def get_passport(db: Session, dog_id: int) -> DogPassport | None:
    dog = repo.get_dog(db, dog_id)
    if not dog:
        return None
    events = [PassportEvent(**e) for e in repo.get_passport_events(db, dog_id)]
    return DogPassport(**dog, events=events)
