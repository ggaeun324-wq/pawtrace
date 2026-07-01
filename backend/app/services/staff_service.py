"""보호소 직원(shelter_staff) 마이페이지 서비스.

역할: 직원 계정 + 담당 보호소 정보 + 운영 통계를 모아 대시보드 데이터를 만들고,
직원이 수정한 보호소 정보를 DB 에 저장합니다.

원칙: 사람을 점수화하지 않습니다. 통계는 '운영 현황' 숫자입니다.
"""
from sqlalchemy.orm import Session

from app.models import Shelter, User
from app.repositories import shelter_repository as repo
from app.schemas.staff import (
    ShelterEditIn,
    StaffAccount,
    StaffShelter,
    StaffStats,
    StaffSummary,
)


def _to_staff_shelter(shelter: Shelter) -> StaffShelter:
    return StaffShelter(
        id=shelter.id,
        name=shelter.name,
        region=shelter.region,
        address=shelter.address,
        phone=shelter.phone,
        description=shelter.description,
        is_gov_registered=bool(shelter.is_gov_registered),
        gov_reg_no=shelter.gov_reg_no,
        transparency_level=shelter.transparency_level,
    )


def _account(user: User) -> StaffAccount:
    return StaffAccount(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=user.role,
    )


def resolve_shelter_id(user: User, shelter_id: int | None) -> int | None:
    """직원은 본인 담당 보호소, admin 은 ?shelter_id= 로 대상 지정 가능."""
    if user.shelter_id is not None:
        return user.shelter_id
    return shelter_id


def build_summary(db: Session, user: User, shelter_id: int | None) -> StaffSummary:
    sid = resolve_shelter_id(user, shelter_id)
    shelter_out: StaffShelter | None = None
    stats = StaffStats()
    if sid is not None:
        shelter = db.get(Shelter, sid)
        if shelter is not None:
            shelter_out = _to_staff_shelter(shelter)
            stats = StaffStats(**repo.shelter_stats(db, sid))
    return StaffSummary(account=_account(user), shelter=shelter_out, stats=stats)


def get_my_shelter(db: Session, user: User, shelter_id: int | None) -> StaffShelter | None:
    sid = resolve_shelter_id(user, shelter_id)
    if sid is None:
        return None
    shelter = db.get(Shelter, sid)
    return _to_staff_shelter(shelter) if shelter is not None else None


def update_my_shelter(
    db: Session, user: User, payload: ShelterEditIn, shelter_id: int | None
) -> StaffShelter | None:
    sid = resolve_shelter_id(user, shelter_id)
    if sid is None:
        return None
    shelter = repo.update_shelter(db, sid, payload.model_dump(exclude_unset=True))
    return _to_staff_shelter(shelter) if shelter is not None else None
