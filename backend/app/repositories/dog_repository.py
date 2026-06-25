"""강아지 저장소.

현재는 시드 데이터를 사용. 실제로는 RDS 쿼리로 교체합니다.
"""
from app.repositories import seed


def get_today_dog() -> dict | None:
    """홈 '오늘의 친구'. MVP는 첫 입양가능 강아지를 반환.
    추후 날짜 시드 기반 회전 로직으로 확장합니다.
    """
    for d in seed.DOGS:
        return _with_shelter(d)
    return None


def get_dog(dog_id: int) -> dict | None:
    for d in seed.DOGS:
        if d["id"] == dog_id:
            return _with_shelter(d)
    return None


def get_passport_events(dog_id: int) -> list[dict]:
    return seed.PASSPORT_EVENTS.get(dog_id, [])


def _with_shelter(dog: dict) -> dict:
    shelter = next((s for s in seed.SHELTERS if s["id"] == dog["shelter_id"]), None)
    return dict(dog, shelter_name=shelter["name"] if shelter else "")
