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
from app.domain import UserRole
from app.models import Dog, PassportEvent, Shelter, User
from app.repositories import seed as seed_src


def _to_date(value: str | None) -> date | None:
    """'2026-01-08' 같은 문자열을 date 로 변환. None 은 그대로."""
    return date.fromisoformat(value) if value else None


def _fix_sequences(db) -> None:
    """명시적 id 로 시드한 뒤 시퀀스를 MAX(id)로 맞춥니다.

    이유: PK 를 직접 지정해 INSERT 하면 SERIAL 시퀀스가 올라가지 않아,
    이후 id 없이 INSERT(예: 공공데이터 동기화) 할 때 PK 충돌이 납니다.
    """
    for table in ("shelters", "dogs", "passport_events", "reports", "users"):
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


if __name__ == "__main__":
    seed()
    seed_users()

