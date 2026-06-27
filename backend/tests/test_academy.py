"""PawTrace Academy 테스트 (교육 콘텐츠/수료/AI 보조). 퀴즈 없음."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _adopter_token() -> str:
    return client.post(
        "/api/v1/auth/login",
        json={"email": "adopter@pawtrace.dev", "password": "adopter1234"},
    ).json()["access_token"]


def test_list_courses():
    r = client.get("/api/v1/academy/courses")
    assert r.status_code == 200
    courses = r.json()
    assert len(courses) >= 3
    # 퀴즈를 제거했으므로 question_count 필드는 더 이상 노출되지 않음
    assert all("question_count" not in c for c in courses)
    assert all(c["title"] and c["summary"] for c in courses)


def test_course_detail_is_reading_content_without_quiz():
    r = client.get("/api/v1/academy/courses/1")
    assert r.status_code == 200
    body = r.json()
    assert body["content"]
    # 퀴즈/정답 관련 필드가 응답에 없어야 함
    assert "questions" not in body
    assert "answer_index" not in body


def test_reflect_returns_questions_without_recommendation():
    r = client.post(
        "/api/v1/academy/reflect",
        json={"situation": "아파트에 혼자 살고 직장에 다녀요. 강아지는 처음이에요."},
    )
    assert r.status_code == 200
    body = r.json()
    assert len(body["questions"]) >= 5
    assert len(body["checklist"]) >= 1
    # 추천이 아니라는 안내 문구 포함
    assert "추천" in body["note"]


def test_complete_requires_auth():
    r = client.post("/api/v1/academy/courses/1/complete")
    assert r.status_code == 401


def test_complete_creates_badge():
    tok = _adopter_token()
    h = {"Authorization": f"Bearer {tok}"}
    r = client.post("/api/v1/academy/courses/1/complete", headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["course_id"] == 1
    assert body["passed"] is True

    # 수료 배지가 /me 에 반영
    me = client.get("/api/v1/academy/me", headers=h).json()
    assert any(c["course_id"] == 1 and c["passed"] for c in me)


def test_complete_unknown_course_404():
    tok = _adopter_token()
    h = {"Authorization": f"Bearer {tok}"}
    r = client.post("/api/v1/academy/courses/9999/complete", headers=h)
    assert r.status_code == 404

