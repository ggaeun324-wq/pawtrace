"""Trust Profile 비즈니스 로직.

- 사용자 본인: 프로필/체크리스트 작성·조회, 본인 Trust Profile 미리보기.
- 보호소/관리자: 특정 사용자의 Trust Profile 열람(점수 아님, 활동 요약).
"""
from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.integrations import ai
from app.models import User
from app.repositories import trust_repository as repo
from app.schemas.trust import (
    ChecklistOut,
    EducationBadge,
    ProfileOut,
    TrustProfile,
)

_PROFILE_FIELDS = ("housing_type", "household", "experience", "daily_hours", "intro")
_CHECKLIST_FIELDS = (
    "vet_info",
    "budget_ready",
    "space_ready",
    "family_agreed",
    "time_committed",
)


def _completeness(profile) -> int:
    if profile is None:
        return 0
    filled = sum(1 for f in _PROFILE_FIELDS if (getattr(profile, f) or "").strip())
    return round(filled / len(_PROFILE_FIELDS) * 100)


def _checklist_done(checklist) -> int:
    if checklist is None:
        return 0
    return sum(1 for f in _CHECKLIST_FIELDS if getattr(checklist, f))


def _has_life_record(db: Session, user_id: int) -> bool:
    """Family Journey 기록 여부. 모델이 아직 없으면 False(점진 도입)."""
    try:
        from app.models import JourneyEntry
    except ImportError:
        return False
    from sqlalchemy import select

    return (
        db.scalars(
            select(JourneyEntry).where(JourneyEntry.user_id == user_id).limit(1)
        ).first()
        is not None
    )


def get_profile(db: Session, user: User) -> ProfileOut:
    profile = repo.get_profile(db, user.id)
    out = ProfileOut.model_validate(profile) if profile else ProfileOut()
    out.completeness = _completeness(profile)
    return out


def save_profile(db: Session, user: User, data: dict) -> ProfileOut:
    profile = repo.upsert_profile(db, user.id, data)
    out = ProfileOut.model_validate(profile)
    out.completeness = _completeness(profile)
    return out


def get_checklist(db: Session, user: User) -> ChecklistOut:
    cl = repo.get_checklist(db, user.id)
    out = ChecklistOut.model_validate(cl) if cl else ChecklistOut()
    out.completed_count = _checklist_done(cl)
    return out


def save_checklist(db: Session, user: User, data: dict) -> ChecklistOut:
    cl = repo.upsert_checklist(db, user.id, data)
    out = ChecklistOut.model_validate(cl)
    out.completed_count = _checklist_done(cl)
    return out


def build_trust_profile(db: Session, target: User) -> TrustProfile:
    """대상 사용자의 준비 활동을 모아 Trust Profile 을 구성합니다(평가 아님)."""
    profile = repo.get_profile(db, target.id)
    checklist = repo.get_checklist(db, target.id)
    completions = repo.passed_completions(db, target.id)
    adopts = repo.adoptions(db, target.id)

    badges = [
        EducationBadge(
            course_id=c.course_id, course_title=c.course.title, emoji=c.course.emoji
        )
        for c in completions
    ]
    completeness = _completeness(profile)
    checklist_done = _checklist_done(checklist)
    has_record = _has_life_record(db, target.id)
    days = max((datetime.now(UTC).replace(tzinfo=None) - target.created_at).days, 0)

    ai_summary = ai.trust_summary(
        {
            "days_since_join": days,
            "education_count": len(badges),
            "checklist_completed": checklist_done,
            "checklist_total": len(_CHECKLIST_FIELDS),
            "profile_completeness": completeness,
            "has_life_record": has_record,
        }
    )

    return TrustProfile(
        user_id=target.id,
        display_name=target.display_name,
        joined_at=target.created_at,
        days_since_join=days,
        profile_completeness=completeness,
        checklist_completed=checklist_done,
        checklist_total=len(_CHECKLIST_FIELDS),
        education_badges=badges,
        has_life_record=has_record,
        adopted_count=len(adopts),
        ai_summary=ai_summary,
    )


def get_trust_profile_for_staff(db: Session, user_id: int) -> TrustProfile:
    """보호소/관리자용: user_id 로 대상 사용자를 찾아 Trust Profile 구성."""
    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없어요.")
    return build_trust_profile(db, target)
