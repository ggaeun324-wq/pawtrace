"""PawTrace Academy 테스트 (교육/퀴즈/수료/AI 보조)."""
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
    assert all(c["question_count"] >= 1 for c in courses)


def test_course_detail_hides_answers():
    r = client.get("/api/v1/academy/courses/1")
    assert r.status_code == 200
    body = r.json()
    assert "content" in body
    assert len(body["questions"]) >= 1
    # 정답 필드가 상세 응답에 노출되면 안 됨
    for q in body["questions"]:
        assert "answer_index" not in q
        assert "options" in q


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


def test_submit_requires_auth():
    r = client.post("/api/v1/academy/courses/1/submit", json={"answers": [0, 0, 0]})
    assert r.status_code == 401


def test_submit_grades_and_creates_badge():
    tok = _adopter_token()
    h = {"Authorization": f"Bearer {tok}"}
    # course 1 정답: 2,2,1
    r = client.post(
        "/api/v1/academy/courses/1/submit", json={"answers": [2, 2, 1]}, headers=h
    )
    assert r.status_code == 200
    body = r.json()
    assert body["score"] == 3
    assert body["total"] == 3
    assert body["passed"] is True
    # 채점 결과에는 정답/해설 공개
    assert all("answer_index" in item for item in body["results"])

    # 수료 배지가 /me 에 반영
    me = client.get("/api/v1/academy/me", headers=h).json()
    assert any(c["course_id"] == 1 and c["passed"] for c in me)


def test_submit_wrong_answer_count_400():
    tok = _adopter_token()
    h = {"Authorization": f"Bearer {tok}"}
    r = client.post(
        "/api/v1/academy/courses/1/submit", json={"answers": [0]}, headers=h
    )
    assert r.status_code == 400
