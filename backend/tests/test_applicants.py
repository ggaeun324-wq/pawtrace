"""Shelter Applicant Review 테스트 (신청자 목록 / 권한 / Trust 재사용)."""
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


def test_applicants_requires_staff_role():
    # 일반 사용자는 신청자 검토 화면에 접근할 수 없음(403)
    r = client.get("/api/v1/shelter/applicants", headers=_adopter_headers())
    assert r.status_code == 403


def test_applicants_requires_auth():
    r = client.get("/api/v1/shelter/applicants")
    assert r.status_code == 401


def test_staff_sees_applicants_with_objective_summary():
    h = _staff_headers()
    r = client.get("/api/v1/shelter/applicants", headers=h)
    assert r.status_code == 200
    items = r.json()
    # 시드: adopter 가 1번 보호소 강아지에 신청한 건이 있어야 함
    assert len(items) >= 1
    item = items[0]
    # 객관적 준비 활동 필드가 채워져야 함(점수/판단 아님)
    assert "profile_completeness" in item
    assert "checklist_completed" in item
    assert "checklist_total" in item
    assert "education_count" in item
    assert item["applicant_name"]
    assert item["dog_name"]
    # AI 요약은 추천/비추천 표현을 담지 않음
    assert "추천" not in item["ai_summary"]
    assert "비추천" not in item["ai_summary"]
