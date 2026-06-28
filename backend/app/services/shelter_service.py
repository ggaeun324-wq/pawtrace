"""보호소 유스케이스."""
from sqlalchemy.orm import Session

from app.repositories import shelter_repository as repo
from app.schemas.shelter import RegionCount, ShelterDetail, ShelterSummary


def list_shelters(db: Session, region: str | None = None) -> list[ShelterSummary]:
    return [ShelterSummary(**s) for s in repo.list_shelters(db, region)]


def get_shelter(db: Session, shelter_id: int) -> ShelterDetail | None:
    row = repo.get_shelter(db, shelter_id)
    return ShelterDetail(**row) if row else None


def region_counts(db: Session) -> list[RegionCount]:
    return [RegionCount(**r) for r in repo.region_counts(db)]
