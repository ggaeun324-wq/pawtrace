"""보호소 직원 마이페이지 테스트 (요약 대시보드 / 정보 조회·수정 / 권한)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _token(email: str, password: str) -> str:
    return client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    ).json()["access_token"]


def _staff_headers() -> dict:
    return {"Authorization": f"Bearer {_token('staff@pawtrace.dev', 'staff1234')}"}


def _adopter_headers() -> dict:
    return {"Authorization": f"Bearer {_token('adopter@pawtrace.dev', 'adopter1234')}"}


def test_summary_requires_staff_role():
    r = client.get("/api/v1/shelter/me/summary", headers=_adopter_headers())
    assert r.status_code == 403


def test_summary_returns_account_shelter_and_stats():
    r = client.get("/api/v1/shelter/me/summary", headers=_staff_headers())
    assert r.status_code == 200
    body = r.json()
    assert body["account"]["role"] == "shelter_staff"
    assert body["shelter"]["id"] == 1
    stats = body["stats"]
    # 통계 키가 모두 존재하고 음수가 아니어야 함
    for key in ("dog_count", "available_count", "adopted_count", "pending_applicants"):
        assert key in stats
        assert stats[key] >= 0
    assert stats["dog_count"] >= stats["available_count"]


def test_staff_can_read_and_update_shelter_info():
    h = _staff_headers()
    before = client.get("/api/v1/shelter/me", headers=h)
    assert before.status_code == 200

    new_phone = "010-7777-8888"
    new_desc = "직원이 직접 수정한 보호소 소개입니다."
    r = client.put(
        "/api/v1/shelter/me",
        json={"phone": new_phone, "description": new_desc, "is_gov_registered": True},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["phone"] == new_phone

    # 저장이 실제로 DB 에 반영되어 다시 조회해도 유지되어야 함
    again = client.get("/api/v1/shelter/me", headers=h).json()
    assert again["phone"] == new_phone
    assert again["description"] == new_desc
    assert again["is_gov_registered"] is True


def test_update_requires_auth():
    r = client.put("/api/v1/shelter/me", json={"phone": "010-0000-0000"})
    assert r.status_code == 401
