"""보호소 유스케이스."""
from app.repositories import shelter_repository as repo
from app.schemas.shelter import ShelterDetail, ShelterSummary


def list_shelters(region: str | None = None) -> list[ShelterSummary]:
    return [ShelterSummary(**s) for s in repo.list_shelters(region)]


def get_shelter(shelter_id: int) -> ShelterDetail | None:
    row = repo.get_shelter(shelter_id)
    return ShelterDetail(**row) if row else None
