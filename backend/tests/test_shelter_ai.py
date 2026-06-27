"""Shelter AI Assistant 테스트 (초안 생성 / 강아지 저장 / 권한)."""
import io

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


def test_ai_draft_requires_staff_role():
    # 일반 사용자는 보호소 AI 보조 기능에 접근할 수 없음(403)
    r = client.post(
        "/api/v1/shelter/dogs/ai-draft",
        data={"name": "콩이", "breed_hint": "진돗개"},
        headers=_adopter_headers(),
    )
    assert r.status_code == 403


def test_ai_draft_generates_editable_draft_without_saving():
    photo = io.BytesIO(b"fake-image-bytes")
    r = client.post(
        "/api/v1/shelter/dogs/ai-draft",
        data={
            "name": "콩이",
            "breed_hint": "진돗개",
            "color_hint": "갈색",
            "temperament_hint": "사람을 좋아하고 활발해요",
        },
        files={"photo": ("kong.jpg", photo, "image/jpeg")},
        headers=_staff_headers(),
    )
    assert r.status_code == 200
    body = r.json()
    assert body["breed_label"] == "진돗개"
    assert body["breed_is_estimate"] is True
    assert "콩이" in body["intro"]
    assert len(body["personality_keywords"]) >= 1
    # 사진을 올리면 (스텁) 썸네일 URL 이 함께 와야 함
    assert body["thumbnail_url"]
    # 초안임을 알리는 안내 문구가 있어야 함(자동 게시 방지)
    assert "초안" in body["note"]


def test_staff_can_create_dog_after_review():
    h = _staff_headers()
    payload = {
        "name": "두부",
        "breed_label": "믹스(추정)",
        "age_estimate": "추정 1살",
        "gender": "female",
        "is_neutered": False,
        "story": "직원이 확인하고 수정한 소개글이에요.",
        "thumbnail_url": "local://stub/dogs/dubu.jpg",
    }
    r = client.post("/api/v1/shelter/dogs", json=payload, headers=h)
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "두부"
    assert body["adoption_status"] == "available"
    assert body["shelter_id"] == 1  # 직원 담당 보호소

    # Pet Passport 에 입소 이벤트가 생겨야 함
    passport = client.get(f"/api/v1/dogs/{body['id']}/passport").json()
    assert any(e["event_type"] == "intake" for e in passport["events"])

    # 담당 보호소 목록에 새 강아지가 보여야 함
    listing = client.get("/api/v1/shelter/dogs", headers=h).json()
    assert any(d["id"] == body["id"] for d in listing)


def test_create_dog_requires_auth():
    r = client.post("/api/v1/shelter/dogs", json={"name": "노바"})
    assert r.status_code == 401
