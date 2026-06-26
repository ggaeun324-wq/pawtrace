"""Trust Profile 데이터 접근 (프로필/체크리스트 upsert + 집계용 조회)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    AcademyCompletion,
    Adoption,
    AdoptionChecklist,
    UserProfile,
)


def get_profile(db: Session, user_id: int) -> UserProfile | None:
    return db.scalars(
        select(UserProfile).where(UserProfile.user_id == user_id)
    ).first()


def upsert_profile(db: Session, user_id: int, data: dict) -> UserProfile:
    row = get_profile(db, user_id)
    if row is None:
        row = UserProfile(user_id=user_id)
        db.add(row)
    for key, value in data.items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row


def get_checklist(db: Session, user_id: int) -> AdoptionChecklist | None:
    return db.scalars(
        select(AdoptionChecklist).where(AdoptionChecklist.user_id == user_id)
    ).first()


def upsert_checklist(db: Session, user_id: int, data: dict) -> AdoptionChecklist:
    row = get_checklist(db, user_id)
    if row is None:
        row = AdoptionChecklist(user_id=user_id)
        db.add(row)
    for key, value in data.items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row


def passed_completions(db: Session, user_id: int) -> list[AcademyCompletion]:
    return list(
        db.scalars(
            select(AcademyCompletion).where(
                AcademyCompletion.user_id == user_id,
                AcademyCompletion.passed.is_(True),
            )
        ).all()
    )


def adoptions(db: Session, user_id: int) -> list[Adoption]:
    return list(
        db.scalars(select(Adoption).where(Adoption.user_id == user_id)).all()
    )
