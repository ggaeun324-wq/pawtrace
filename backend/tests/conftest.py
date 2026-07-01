"""pytest 공용 픽스처.

읽기 경로 테스트는 실제 DB(PostgreSQL/PostGIS)를 사용합니다.
- DB 에 연결되지 않으면(로컬에서 DB 미기동) 테스트를 'skip' 해 개발 편의를 보장합니다.
- 연결되면 테이블 생성 + 시드를 보장(멱등)한 뒤 테스트를 실행합니다.
  CI 에서는 워크플로가 미리 alembic upgrade + seed 를 수행하므로 여기서도 안전하게 재실행됩니다.
"""
import pytest
from sqlalchemy import text

import app.models  # noqa: F401  (메타데이터 등록)
from app.db.session import Base, engine
from scripts.seed_db import (
    seed,
    seed_academy,
    seed_journey,
    seed_products,
    seed_profiles,
    seed_relations,
    seed_users,
)


@pytest.fixture(scope="session", autouse=True)
def _ensure_db():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        pytest.skip("DB 에 연결할 수 없어 테스트를 건너뜁니다(로컬 DB 미기동).")
        return

    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    Base.metadata.create_all(engine)
    seed()
    seed_users()
    seed_relations()
    seed_academy()
    seed_profiles()
    seed_journey()
    seed_products()
    yield
