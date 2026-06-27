"""Family Journey 비즈니스 로직.

- 작성: 해당 강아지를 입양한 사용자(Adoption 보유)만 가능.
- 조회: 본인 기록 / 특정 강아지의 공개 타임라인.
- 응원(cheer): 로그인 사용자가 누를 수 있음(댓글 기능 없음).
- AI: 사용자가 쓴 메모 정리(초안)만 보조.
"""
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations import ai
from app.models import Adoption, Dog, JourneyEntry, User
from app.schemas.journey import JourneyIn, JourneyOut


def _to_out(entry: JourneyEntry) -> JourneyOut:
    return JourneyOut(
        id=entry.id,
        user_id=entry.user_id,
        author_name=entry.user.display_name if entry.user else "익명",
        dog_id=entry.dog_id,
        dog_name=entry.dog.name if entry.dog else "강아지",
        quarter_label=entry.quarter_label,
        title=entry.title,
        body=entry.body,
        photo_url=entry.photo_url,
        cheers=entry.cheers,
        created_at=entry.created_at,
    )


def _owns_adoption(db: Session, user_id: int, dog_id: int) -> bool:
    return (
        db.scalars(
            select(Adoption)
            .where(Adoption.user_id == user_id, Adoption.dog_id == dog_id)
            .limit(1)
        ).first()
        is not None
    )


def my_adopted_dogs(db: Session, user: User) -> list[dict]:
    """내가 입양한 강아지 목록(기록 작성 대상 선택용)."""
    rows = db.scalars(
        select(Adoption).where(Adoption.user_id == user.id)
    ).all()
    out = []
    for a in rows:
        dog = db.get(Dog, a.dog_id)
        if dog:
            out.append({"dog_id": dog.id, "dog_name": dog.name})
    return out


def create_entry(db: Session, user: User, data: JourneyIn) -> JourneyOut:
    """입양자만 기록을 작성할 수 있습니다."""
    if db.get(Dog, data.dog_id) is None:
        raise HTTPException(status_code=404, detail="강아지를 찾을 수 없어요.")
    if not _owns_adoption(db, user.id, data.dog_id):
        raise HTTPException(
            status_code=403,
            detail="입양하신 강아지에 대해서만 반려생활 기록을 남길 수 있어요.",
        )
    entry = JourneyEntry(
        user_id=user.id,
        dog_id=data.dog_id,
        quarter_label=data.quarter_label,
        title=data.title,
        body=data.body,
        photo_url=data.photo_url,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _to_out(entry)


def list_my_entries(db: Session, user: User) -> list[JourneyOut]:
    rows = db.scalars(
        select(JourneyEntry)
        .where(JourneyEntry.user_id == user.id)
        .order_by(JourneyEntry.created_at.desc())
    ).all()
    return [_to_out(e) for e in rows]


def list_for_dog(db: Session, dog_id: int) -> list[JourneyOut]:
    """특정 강아지의 공개 타임라인(오래된 → 최신, 성장 흐름)."""
    rows = db.scalars(
        select(JourneyEntry)
        .where(JourneyEntry.dog_id == dog_id)
        .order_by(JourneyEntry.created_at.asc())
    ).all()
    return [_to_out(e) for e in rows]


def cheer(db: Session, entry_id: int) -> JourneyEntry:
    entry = db.get(JourneyEntry, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="기록을 찾을 수 없어요.")
    entry.cheers = (entry.cheers or 0) + 1
    db.commit()
    db.refresh(entry)
    return entry


def draft(memo: str, dog_name: str | None) -> dict:
    return ai.journey_draft(memo, dog_name)
