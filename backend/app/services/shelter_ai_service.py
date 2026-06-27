"""Shelter AI Assistant 비즈니스 로직.

흐름:
  1) 직원이 사진(+힌트) 업로드 → AI 초안 생성(저장 안 함).
  2) 직원이 초안을 확인/수정.
  3) 직원이 최종 저장 → Dog 레코드 + 입소 타임라인 이벤트 생성.
"""
from datetime import date

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain import AdoptionStatus, DataSource, PassportEventType
from app.integrations import ai, storage
from app.models import Dog, PassportEvent, User
from app.schemas.shelter_ai import DogCreateIn, DogDraft, DogOut


def generate_draft(
    hints: dict, photo_bytes: bytes | None, filename: str | None
) -> DogDraft:
    """사진(선택)과 힌트로 강아지 소개 초안을 생성합니다(저장 안 함)."""
    thumbnail_url = None
    if photo_bytes:
        safe_name = filename or "dog.jpg"
        key = f"dogs/drafts/{safe_name}"
        thumbnail_url = storage.upload_image(key, photo_bytes)

    draft = ai.dog_intro_draft(hints)
    draft["thumbnail_url"] = thumbnail_url
    return DogDraft(**draft)


def _resolve_shelter_id(staff: User, data: DogCreateIn) -> int:
    """저장할 보호소 결정: 직원은 담당 보호소, admin 은 입력값을 사용."""
    if staff.shelter_id is not None:
        return staff.shelter_id
    if data.shelter_id is not None:
        return data.shelter_id
    raise HTTPException(
        status_code=400,
        detail="담당 보호소가 없어요. shelter_id 를 지정해 주세요.",
    )


def create_dog(db: Session, staff: User, data: DogCreateIn) -> DogOut:
    """직원이 확인/수정한 강아지를 저장합니다(입양 가능 상태로 등록)."""
    shelter_id = _resolve_shelter_id(staff, data)

    dog = Dog(
        shelter_id=shelter_id,
        name=data.name,
        breed_label=data.breed_label,
        breed_is_estimate=data.breed_is_estimate,
        age_estimate=data.age_estimate,
        gender=data.gender,
        is_neutered=data.is_neutered,
        adoption_status=AdoptionStatus.available,
        source=DataSource.manual,
        thumbnail_url=data.thumbnail_url,
        story=data.story,
    )
    db.add(dog)
    db.flush()  # dog.id 확보

    # 입소 타임라인 이벤트(보호소 기록 출처)로 Pet Passport 가 비지 않도록 함.
    db.add(
        PassportEvent(
            dog_id=dog.id,
            event_type=PassportEventType.intake,
            event_date=date.today(),
            title="보호소 입소",
            memo="보호소 직원이 PawTrace에 등록했어요.",
            source=DataSource.manual,
        )
    )
    db.commit()
    db.refresh(dog)
    return DogOut.model_validate(dog)


def list_shelter_dogs(db: Session, staff: User, shelter_id: int | None) -> list[DogOut]:
    """직원 담당 보호소(또는 admin 이 지정한 보호소)의 강아지 목록."""
    target = staff.shelter_id if staff.shelter_id is not None else shelter_id
    if target is None:
        raise HTTPException(
            status_code=400,
            detail="조회할 보호소를 지정해 주세요(shelter_id).",
        )
    rows = db.scalars(
        select(Dog).where(Dog.shelter_id == target).order_by(Dog.id.desc())
    ).all()
    return [DogOut.model_validate(d) for d in rows]
