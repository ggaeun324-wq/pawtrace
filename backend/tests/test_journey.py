"""Family Journey 테스트 (작성 권한 / 타임라인 / 응원 / AI 초안)."""
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


def test_my_journey_requires_auth():
    assert client.get("/api/v1/journey/me").status_code == 401


def test_public_dog_timeline_oldest_first():
    # 데모: 입양자가 초코(dog 2)에 분기별 기록을 남겨둠
    r = client.get("/api/v1/journey/dog/2")
    assert r.status_code == 200
    entries = r.json()
    assert len(entries) >= 2
    # 성장 흐름이므로 오래된 → 최신 순서
    times = [e["created_at"] for e in entries]
    assert times == sorted(times)


def test_only_adopter_can_write_for_their_dog():
    h = _adopter_headers()
    # 입양한 강아지(초코=2)에는 작성 가능
    ok = client.post(
        "/api/v1/journey",
        json={
            "dog_id": 2,
            "quarter_label": "2026 3분기",
            "title": "잘 지내요",
            "body": "오늘도 산책했어요.",
        },
        headers=h,
    )
    assert ok.status_code == 201

    # 입양하지 않은 강아지(1)에는 작성 불가(403)
    no = client.post(
        "/api/v1/journey",
        json={"dog_id": 1, "title": "안돼요", "body": "내 강아지가 아니에요."},
        headers=h,
    )
    assert no.status_code == 403


def test_staff_without_adoption_cannot_write():
    r = client.post(
        "/api/v1/journey",
        json={"dog_id": 2, "title": "권한없음", "body": "입양 관계가 없어요."},
        headers=_staff_headers(),
    )
    assert r.status_code == 403


def test_cheer_increments():
    h = _adopter_headers()
    entries = client.get("/api/v1/journey/dog/2").json()
    target = entries[0]
    before = target["cheers"]
    r = client.post(f"/api/v1/journey/{target['id']}/cheer", headers=h)
    assert r.status_code == 200
    assert r.json()["cheers"] == before + 1


def test_ai_draft_keeps_user_memo_and_does_not_judge():
    h = _adopter_headers()
    memo = "오늘 초코랑 한강 산책했어요"
    r = client.post(
        "/api/v1/journey/draft",
        json={"memo": memo, "dog_name": "초코"},
        headers=h,
    )
    assert r.status_code == 200
    body = r.json()
    # 사용자가 쓴 메모 내용이 초안에 그대로 보존되어야 함(지어내지 않음)
    assert "한강 산책" in body["draft"]
    assert "행복" in body["note"]  # 행복을 판단하지 않는다는 안내
