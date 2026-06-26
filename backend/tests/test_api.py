"""기본 스모크 테스트. (pytest)"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_today_dog_matches_frontend():
    r = client.get("/api/v1/dogs/today")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "봄이"
    assert body["adoption_status"] == "available"


def test_shelters_have_available_count():
    r = client.get("/api/v1/shelters?region=서울")
    assert r.status_code == 200
    shelters = r.json()
    assert len(shelters) >= 1
    assert "available_dog_count" in shelters[0]


def test_passport_timeline():
    r = client.get("/api/v1/dogs/1/passport")
    assert r.status_code == 200
    assert len(r.json()["events"]) >= 1


def test_happy_endings_returns_adopted():
    r = client.get("/api/v1/dogs/happy-endings")
    assert r.status_code == 200
    dogs = r.json()
    assert len(dogs) >= 1
    assert all(d["adoption_status"] == "adopted" for d in dogs)


def test_urgent_dogs_sorted_by_deadline():
    r = client.get("/api/v1/dogs/urgent")
    assert r.status_code == 200
    dogs = r.json()
    assert len(dogs) >= 1
    # 모두 입양 가능 + 마감일 보유
    assert all(d["adoption_status"] == "available" for d in dogs)
    assert all(d["protect_end_date"] for d in dogs)
    # days_left 계산 + 마감 빠른 순 정렬 확인
    deadlines = [d["protect_end_date"] for d in dogs]
    assert deadlines == sorted(deadlines)
    assert all(d["days_left"] is not None for d in dogs)
