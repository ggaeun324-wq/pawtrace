"""시드 로더 — 데모 데이터를 실제 DB(PostgreSQL/PostGIS)에 적재합니다.

설계 포인트:
- **멱등(idempotent)**: 이미 데이터가 있으면 아무것도 하지 않습니다.
  → docker-compose / CI 에서 매번 호출해도 중복 INSERT 가 발생하지 않습니다.
- 데이터 원본은 기존 `app/repositories/seed.py`(데모 값)를 그대로 재사용합니다.
- 위치(location, PostGIS) 컬럼은 이번 단계에서 NULL 로 두고, 반경검색을 구현하는
  Sprint 2 에서 lat/lng 로부터 채웁니다.

실행: `python -m scripts.seed_db`
"""
from datetime import date

from sqlalchemy import text

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.domain import ApplicationStatus, UserRole
from app.models import (
    Adoption,
    AdoptionApplication,
    AdoptionChecklist,
    Course,
    Dog,
    PassportEvent,
    QuizQuestion,
    Shelter,
    User,
    UserProfile,
)
from app.repositories import seed as seed_src


def _to_date(value: str | None) -> date | None:
    """'2026-01-08' 같은 문자열을 date 로 변환. None 은 그대로."""
    return date.fromisoformat(value) if value else None


def _fix_sequences(db) -> None:
    """명시적 id 로 시드한 뒤 시퀀스를 MAX(id)로 맞춥니다.

    이유: PK 를 직접 지정해 INSERT 하면 SERIAL 시퀀스가 올라가지 않아,
    이후 id 없이 INSERT(예: 공공데이터 동기화) 할 때 PK 충돌이 납니다.
    """
    for table in (
        "shelters", "dogs", "passport_events", "reports", "users",
        "adoptions", "adoption_applications",
        "user_profiles", "adoption_checklists",
    ):
        db.execute(
            text(
                "SELECT setval(pg_get_serial_sequence(:t, 'id'), "
                "COALESCE((SELECT MAX(id) FROM " + table + "), 1))"
            ),
            {"t": table},
        )
    db.commit()


def seed() -> None:
    db = SessionLocal()
    try:
        # 멱등 가드: 이미 보호소가 있으면 시드 생략.
        if db.query(Shelter).count() > 0:
            print("[seed] 이미 데이터가 존재하여 시드를 건너뜁니다.")
            _fix_sequences(db)  # 재기동 시에도 시퀀스 정합성 보장
            return

        for s in seed_data_shelters():
            db.add(s)
        for d in seed_data_dogs():
            db.add(d)
        for e in seed_data_events():
            db.add(e)

        db.commit()
        _fix_sequences(db)
        print(
            f"[seed] 완료: 보호소 {len(seed_src.SHELTERS)} · "
            f"강아지 {len(seed_src.DOGS)} · "
            f"타임라인 이벤트 {sum(len(v) for v in seed_src.PASSPORT_EVENTS.values())}"
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def seed_users() -> None:
    """데모 계정 시드(멱등). 이메일 기준으로 없을 때만 생성합니다.
    - 플랫폼 관리자(admin): config 의 ADMIN_EMAIL/ADMIN_PASSWORD.
    - 보호소 직원(shelter_staff): 1번 보호소 담당 데모 계정.
    """
    db = SessionLocal()
    try:
        demo_accounts = [
            {
                "email": settings.ADMIN_EMAIL,
                "password": settings.ADMIN_PASSWORD,
                "display_name": "플랫폼 관리자",
                "role": UserRole.admin,
                "shelter_id": None,
            },
            {
                "email": "staff@pawtrace.dev",
                "password": "staff1234",
                "display_name": "행복 보호소 직원",
                "role": UserRole.shelter_staff,
                "shelter_id": 1,
            },
            {
                "email": "adopter@pawtrace.dev",
                "password": "adopter1234",
                "display_name": "보리 가족",
                "role": UserRole.user,
                "shelter_id": None,
            },
        ]
        created = 0
        for acc in demo_accounts:
            exists = db.query(User).filter(User.email == acc["email"]).first()
            if exists:
                continue
            # shelter_staff 데모는 해당 보호소가 있을 때만 연결.
            shelter_id = acc["shelter_id"]
            if shelter_id is not None and db.get(Shelter, shelter_id) is None:
                shelter_id = None
            db.add(
                User(
                    email=acc["email"],
                    hashed_password=hash_password(acc["password"]),
                    display_name=acc["display_name"],
                    role=acc["role"],
                    shelter_id=shelter_id,
                )
            )
            created += 1
        db.commit()
        print(f"[seed] 데모 계정 {created}개 생성(이미 있으면 건너뜀).")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def seed_data_shelters() -> list[Shelter]:
    return [
        Shelter(
            id=s["id"],
            name=s["name"],
            region=s["region"],
            address=s.get("address"),
            description=s.get("description"),
            is_gov_registered=s.get("is_gov_registered", False),
            gov_reg_no=s.get("gov_reg_no"),
            transparency_level=s["transparency_level"],
            phone=s.get("phone"),
            lat=s.get("lat"),
            lng=s.get("lng"),
        )
        for s in seed_src.SHELTERS
    ]


def seed_data_dogs() -> list[Dog]:
    return [
        Dog(
            id=d["id"],
            shelter_id=d["shelter_id"],
            name=d["name"],
            breed_label=d.get("breed_label"),
            breed_is_estimate=d.get("breed_is_estimate", True),
            age_estimate=d.get("age_estimate"),
            gender=d.get("gender"),
            is_neutered=d.get("is_neutered"),
            adoption_status=d["adoption_status"],
            thumbnail_url=d.get("thumbnail_url"),
            story=d.get("story"),
            protect_end_date=_to_date(d.get("protect_end_date")),
        )
        for d in seed_src.DOGS
    ]


def seed_data_events() -> list[PassportEvent]:
    events: list[PassportEvent] = []
    for dog_id, items in seed_src.PASSPORT_EVENTS.items():
        for e in items:
            events.append(
                PassportEvent(
                    dog_id=dog_id,
                    event_type=e["event_type"],
                    event_date=_to_date(e.get("event_date")),
                    title=e["title"],
                    memo=e.get("memo"),
                    source=e.get("source", seed_src.DataSource.manual),
                )
            )
    return events


def seed_relations() -> None:
    """입양 관계/신청 데모 시드(멱등).

    - 입양 완료(adopted) 강아지(초코=2)를 데모 입양자(adopter)와 연결 → Family Journey 토대.
    - 입양 가능 강아지 몇 마리에 신청을 남겨 Shelter Applicant Review 화면에 데이터 제공.
    이미 입양 레코드가 있으면 건너뜁니다.
    """
    db = SessionLocal()
    try:
        if db.query(Adoption).count() > 0:
            return
        adopter = db.query(User).filter(User.email == "adopter@pawtrace.dev").first()
        if adopter is None:
            return  # 데모 입양자 계정이 아직 없으면 생략(seed_users 선행 필요)

        # 입양 관계: 초코(2)를 데모 입양자가 입양
        if db.get(Dog, 2) is not None:
            db.add(
                Adoption(user_id=adopter.id, dog_id=2, adopted_at=date(2026, 3, 15))
            )

        # 입양 신청: 입양 가능 강아지(봄이=1, 두유=5)에 신청 데모
        for dog_id, msg, st in (
            (1, "마당이 있는 집에서 봄이와 함께 살고 싶어요.", ApplicationStatus.submitted),
            (5, "이전에 반려견을 키운 경험이 있어요. 두유를 만나보고 싶어요.",
             ApplicationStatus.reviewing),
        ):
            if db.get(Dog, dog_id) is not None:
                db.add(
                    AdoptionApplication(
                        user_id=adopter.id, dog_id=dog_id, message=msg, status=st
                    )
                )
        db.commit()
        _fix_sequences(db)
        print("[seed] 입양 관계/신청 데모 생성 완료.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def seed_academy() -> None:
    """PawTrace Academy 교육/퀴즈 시드(멱등). 이미 과정이 있으면 건너뜁니다."""
    db = SessionLocal()
    try:
        if db.query(Course).count() > 0:
            return
        for c in seed_src.ACADEMY_COURSES:
            course = Course(
                slug=c["slug"],
                title=c["title"],
                emoji=c.get("emoji"),
                summary=c["summary"],
                content=c["content"],
                order_no=c.get("order_no", 0),
            )
            db.add(course)
            db.flush()  # course.id 확보
            for i, q in enumerate(c["questions"]):
                db.add(
                    QuizQuestion(
                        course_id=course.id,
                        order_no=i,
                        question=q["question"],
                        options=q["options"],
                        answer_index=q["answer_index"],
                        explanation=q.get("explanation"),
                    )
                )
        db.commit()
        print(f"[seed] Academy 교육 {len(seed_src.ACADEMY_COURSES)}개 생성.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def seed_profiles() -> None:
    """Trust Profile 데모 시드(멱등).

    데모 입양자(adopter)에게 '부분 작성' 프로필과 체크리스트 일부 완료 상태를 부여해
    보호소/관리자 화면에서 Trust Profile 이 의미 있게 보이도록 합니다.
    이미 프로필이 있으면 건너뜁니다.
    """
    db = SessionLocal()
    try:
        if db.query(UserProfile).count() > 0:
            return
        adopter = db.query(User).filter(User.email == "adopter@pawtrace.dev").first()
        if adopter is None:
            return
        db.add(
            UserProfile(
                user_id=adopter.id,
                housing_type="아파트",
                household="배우자와 둘이 거주",
                experience="어릴 때 강아지를 키운 경험이 있어요.",
                daily_hours="하루 4시간 이상",
                intro=None,  # 일부 미작성 → 작성률 80%
            )
        )
        db.add(
            AdoptionChecklist(
                user_id=adopter.id,
                vet_info=True,
                budget_ready=True,
                space_ready=True,
                family_agreed=True,
                time_committed=False,  # 4/5 완료
            )
        )
        db.commit()
        _fix_sequences(db)
        print("[seed] Trust Profile 데모(프로필+체크리스트) 생성 완료.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    seed_users()
    seed_relations()
    seed_academy()
    seed_profiles()

