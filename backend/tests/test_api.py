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
