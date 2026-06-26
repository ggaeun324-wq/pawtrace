"""Trust Profile 테스트 (프로필/체크리스트/역할 기반 열람)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _token(email: str, password: str) -> str:
    return client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    ).json()["access_token"]


def _adopter_headers() -> dict:
    return {"Authorization": f"Bearer {_token('adopter@pawtrace.dev', 'adopter1234')}"}


def _staff_headers() -> dict:
    return {"Authorization": f"Bearer {_token('staff@pawtrace.dev', 'staff1234')}"}


def test_profile_requires_auth():
    assert client.get("/api/v1/trust/me/profile").status_code == 401


def test_save_and_get_profile_completeness():
    h = _adopter_headers()
    r = client.put(
        "/api/v1/trust/me/profile",
        json={
            "housing_type": "아파트",
            "household": "1인 가구",
            "experience": "처음이에요",
            "daily_hours": "하루 3시간",
            "intro": "책임감 있게 준비하고 있어요.",
        },
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["completeness"] == 100

    got = client.get("/api/v1/trust/me/profile", headers=h)
    assert got.status_code == 200
    assert got.json()["housing_type"] == "아파트"


def test_checklist_counts():
    h = _adopter_headers()
    r = client.put(
        "/api/v1/trust/me/checklist",
        json={
            "vet_info": True,
            "budget_ready": True,
            "space_ready": False,
            "family_agreed": True,
            "time_committed": False,
        },
        headers=h,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["completed_count"] == 3
    assert body["total"] == 5


def test_my_trust_profile_has_no_score_judgment():
    h = _adopter_headers()
    r = client.get("/api/v1/trust/me", headers=h)
    assert r.status_code == 200
    body = r.json()
    assert "ai_summary" in body
    assert "profile_completeness" in body
    # 객관 요약에 평가성 단어가 없어야 함(점수/판단 배제)
    assert "최종 판단은 보호소" in body["ai_summary"]


def test_staff_can_view_user_trust_profile():
    # 데모 입양자(adopter)의 user_id 를 본인 토큰으로 확인
    adopter_h = _adopter_headers()
    uid = client.get("/api/v1/trust/me", headers=adopter_h).json()["user_id"]

    staff_h = _staff_headers()
    r = client.get(f"/api/v1/trust/users/{uid}", headers=staff_h)
    assert r.status_code == 200
    assert r.json()["user_id"] == uid


def test_normal_user_cannot_view_others_trust_profile():
    h = _adopter_headers()
    # 일반 사용자는 staff 전용 엔드포인트 접근 불가(403)
    r = client.get("/api/v1/trust/users/1", headers=h)
    assert r.status_code == 403
