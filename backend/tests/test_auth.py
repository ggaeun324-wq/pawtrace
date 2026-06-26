"""인증 플로우 테스트 (회원가입/로그인/내 정보)."""
import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _unique_email() -> str:
    return f"user_{uuid.uuid4().hex[:10]}@test.com"


def test_register_login_me_flow():
    email = _unique_email()
    r = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "display_name": "테스터", "role": "user"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["role"] == "user"

    r = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token

    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == email


def test_admin_cannot_self_register():
    r = client.post(
        "/api/v1/auth/register",
        json={
            "email": _unique_email(),
            "password": "password123",
            "display_name": "x",
            "role": "admin",
        },
    )
    assert r.status_code == 403


def test_duplicate_email_rejected():
    email = _unique_email()
    body = {"email": email, "password": "password123", "display_name": "x", "role": "user"}
    assert client.post("/api/v1/auth/register", json=body).status_code == 201
    assert client.post("/api/v1/auth/register", json=body).status_code == 409


def test_shelter_staff_requires_shelter():
    r = client.post(
        "/api/v1/auth/register",
        json={
            "email": _unique_email(),
            "password": "password123",
            "display_name": "x",
            "role": "shelter_staff",
        },
    )
    assert r.status_code == 422


def test_me_requires_token():
    assert client.get("/api/v1/auth/me").status_code == 401


def test_wrong_password_rejected():
    email = _unique_email()
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "display_name": "x", "role": "user"},
    )
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "nope"})
    assert r.status_code == 401
