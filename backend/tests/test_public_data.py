"""공공데이터 연동 테스트 (파싱·멱등 upsert·관리자 권한)."""
import json
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import SessionLocal
from app.domain import AdoptionStatus, DataSource
from app.integrations import public_data
from app.main import app
from app.models import Dog
from app.services import sync_service

client = TestClient(app)

SAMPLE = json.loads(
    (Path(__file__).parent / "fixtures" / "public_data_sample.json").read_text(encoding="utf-8")
)


def test_parse_maps_fields():
    records = public_data.parse_animals(SAMPLE)
    assert len(records) == 2

    first = records[0]
    assert first["shelter"]["name"] == "행복보호소"
    assert first["shelter"]["region"] == "서울특별시 마포구"
    assert first["dog"]["breed_label"] == "믹스견"        # '[개] ' 머리표 제거
    assert first["dog"]["gender"] == "female"
    assert first["dog"]["is_neutered"] is True
    assert first["dog"]["adoption_status"] == AdoptionStatus.available  # 보호중

    second = records[1]
    assert second["dog"]["adoption_status"] == AdoptionStatus.adopted   # 종료(입양)
    assert second["dog"]["is_neutered"] is False


def test_upsert_is_idempotent():
    records = public_data.parse_animals(SAMPLE)
    db = SessionLocal()
    try:
        r1 = sync_service.upsert_records(db, records)
        assert r1["dogs_created"] == 2
        # 같은 데이터 재동기화 → 신규 0, 업데이트만
        r2 = sync_service.upsert_records(db, records)
        assert r2["dogs_created"] == 0
        assert r2["dogs_updated"] == 2
        # 공공데이터 출처 강아지가 중복 없이 2마리만 존재
        count = len(
            db.scalars(select(Dog).where(Dog.source == DataSource.public_api)).all()
        )
        assert count == 2
    finally:
        db.close()


def test_sync_requires_admin():
    # 토큰 없음 → 401
    assert client.post("/api/v1/admin/sync/public-data").status_code == 401

    # 일반 사용자 토큰 → 403
    import uuid

    email = f"u_{uuid.uuid4().hex[:8]}@test.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "display_name": "u", "role": "user"},
    )
    tok = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "password123"}
    ).json()["access_token"]
    r = client.post(
        "/api/v1/admin/sync/public-data", headers={"Authorization": f"Bearer {tok}"}
    )
    assert r.status_code == 403


def test_sync_admin_no_key_returns_message():
    tok = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@pawtrace.dev", "password": "admin1234"},
    ).json()["access_token"]
    r = client.post(
        "/api/v1/admin/sync/public-data", headers={"Authorization": f"Bearer {tok}"}
    )
    assert r.status_code == 200
    body = r.json()
    # 키가 없으면 실연동은 비활성, 메시지로 안내
    assert body["source_enabled"] is False
    assert "PUBLIC_DATA_API_KEY" in body["message"]
