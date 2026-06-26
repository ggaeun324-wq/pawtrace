"""Academy 데이터 접근 (교육/퀴즈/수료).

수료(AcademyCompletion)는 (user, course) 당 1건으로 유지(재응시 시 갱신)합니다.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AcademyCompletion, Course


def list_courses(db: Session) -> list[Course]:
    return list(
        db.scalars(select(Course).order_by(Course.order_no, Course.id)).all()
    )


def get_course(db: Session, course_id: int) -> Course | None:
    return db.get(Course, course_id)


def list_completions(db: Session, user_id: int) -> list[AcademyCompletion]:
    return list(
        db.scalars(
            select(AcademyCompletion).where(AcademyCompletion.user_id == user_id)
        ).all()
    )


def upsert_completion(
    db: Session, *, user_id: int, course_id: int, score: int, total: int, passed: bool
) -> AcademyCompletion:
    """(user, course) 수료 기록 upsert. 더 좋은 결과로만 갱신하지 않고 최신 결과를 반영."""
    row = db.scalars(
        select(AcademyCompletion).where(
            AcademyCompletion.user_id == user_id,
            AcademyCompletion.course_id == course_id,
        )
    ).first()
    if row is None:
        row = AcademyCompletion(user_id=user_id, course_id=course_id)
        db.add(row)
    row.score = score
    row.total = total
    row.passed = passed
    db.commit()
    db.refresh(row)
    return row
