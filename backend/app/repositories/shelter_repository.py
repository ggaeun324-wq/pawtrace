"""보호소 저장소.

현재는 시드 데이터를 사용. 실제로는 PostGIS ST_DWithin 으로 반경 검색합니다.
"""
from app.repositories import seed


def count_available_dogs(shelter_id: int) -> int:
    from app.domain import AdoptionStatus
    return sum(
        1 for d in seed.DOGS
        if d["shelter_id"] == shelter_id and d["adoption_status"] == AdoptionStatus.available
    )


def list_shelters(region: str | None = None) -> list[dict]:
    rows = seed.SHELTERS
    if region:
        rows = [s for s in rows if s["region"] == region]
    return [dict(s, available_dog_count=count_available_dogs(s["id"])) for s in rows]


def get_shelter(shelter_id: int) -> dict | None:
    for s in seed.SHELTERS:
        if s["id"] == shelter_id:
            return dict(s, available_dog_count=count_available_dogs(shelter_id))
    return None
