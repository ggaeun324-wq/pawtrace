"""강아지 / Pet Passport 유스케이스."""
from app.repositories import dog_repository as repo
from app.schemas.dog import DogPassport, DogToday, PassportEvent


def get_today_dog() -> DogToday | None:
    row = repo.get_today_dog()
    return DogToday(**row) if row else None


def get_passport(dog_id: int) -> DogPassport | None:
    dog = repo.get_dog(dog_id)
    if not dog:
        return None
    events = [PassportEvent(**e) for e in repo.get_passport_events(dog_id)]
    return DogPassport(**dog, events=events)
