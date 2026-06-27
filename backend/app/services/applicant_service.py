"""Shelter Applicant Review 서비스 (보호소 직원이 입양 신청자를 검토).

설계 원칙:
- 신청자의 객관적 준비 활동(프로필/체크리스트/교육/AI 요약)만 보여줍니다.
- 사람을 점수화하거나 합격/불합격으로 판단하지 않습니다.
- 최종 결정은 보호소 직원이 직접 내립니다(UI 에 명시).
"""
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AdoptionApplication, Dog, User
from app.schemas.applicant import ApplicantSummary
from app.services import trust_service


def list_applicants(
    db: Session, staff: User, shelter_id: int | None
) -> list[ApplicantSummary]:
    """담당 보호소(또는 admin 이 지정한 보호소)의 입양 신청자 목록을 반환합니다."""
    target = staff.shelter_id if staff.shelter_id is not None else shelter_id
    if target is None:
        raise HTTPException(
            status_code=400,
            detail="조회할 보호소를 지정해 주세요(shelter_id).",
        )

    stmt = (
        select(AdoptionApplication, Dog)
        .join(Dog, AdoptionApplication.dog_id == Dog.id)
        .where(Dog.shelter_id == target)
        .order_by(AdoptionApplication.created_at.desc())
    )
    rows = db.execute(stmt).all()

    out: list[ApplicantSummary] = []
    for application, dog in rows:
        applicant = db.get(User, application.user_id)
        if applicant is None:
            continue
        # Trust Profile 핵심값을 재사용합니다(별도 평가 로직 없음).
        tp = trust_service.build_trust_profile(db, applicant)
        out.append(
            ApplicantSummary(
                application_id=application.id,
                status=application.status,
                message=application.message,
                created_at=application.created_at,
                dog_id=dog.id,
                dog_name=dog.name,
                user_id=applicant.id,
                applicant_name=tp.display_name,
                profile_completeness=tp.profile_completeness,
                checklist_completed=tp.checklist_completed,
                checklist_total=tp.checklist_total,
                education_count=len(tp.education_badges),
                ai_summary=tp.ai_summary,
            )
        )
    return out
