"""Authentication, password storage and authorization boundaries."""
from __future__ import annotations

from app.core.security import create_access_token, hash_password, verify_password


def test_password_hash_is_salted_and_verifiable():
    h1 = hash_password("s3cret-passphrase")
    h2 = hash_password("s3cret-passphrase")
    assert h1 != h2, "each hash must use a fresh salt"
    assert h1.startswith("scrypt$")
    assert verify_password("s3cret-passphrase", h1)
    assert not verify_password("wrong-password", h1)
    assert not verify_password("s3cret-passphrase", None)


def test_short_password_rejected():
    import pytest

    with pytest.raises(ValueError):
        hash_password("short")


def test_register_login_me(client):
    reg = client.post(
        "/api/auth/register",
        json={"email": "carol@example.com", "password": "a-long-password", "display_name": "Carol"},
    )
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    assert reg.json()["user"]["email"] == "carol@example.com"

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["display_name"] == "Carol"

    dupe = client.post(
        "/api/auth/register",
        json={"email": "carol@example.com", "password": "a-long-password"},
    )
    assert dupe.status_code == 409

    login = client.post(
        "/api/auth/login", json={"email": "carol@example.com", "password": "a-long-password"}
    )
    assert login.status_code == 200

    bad = client.post(
        "/api/auth/login", json={"email": "carol@example.com", "password": "nope-nope-nope"}
    )
    assert bad.status_code == 401
    assert "Invalid email or password" in bad.json()["detail"]


def test_login_sets_httponly_cookie(client, user_a):
    resp = client.post(
        "/api/auth/login", json={"email": "alice@example.com", "password": "correct-horse-9"}
    )
    assert resp.status_code == 200
    cookie = resp.headers.get("set-cookie", "")
    assert "vc_token=" in cookie
    assert "HttpOnly" in cookie


def test_missing_and_invalid_tokens(client):
    client.cookies.clear()  # a login cookie may be present from another test
    assert client.get("/api/auth/me").status_code == 401
    assert (
        client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-jwt"}).status_code
        == 401
    )


def test_token_signed_with_other_secret_is_rejected(client):
    import jwt

    forged = jwt.encode({"sub": "abc", "iss": "viral-clips", "aud": "authenticated", "exp": 9999999999},
                        "attacker-secret", algorithm="HS256")
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {forged}"})
    assert resp.status_code == 401


def test_access_token_roundtrip():
    token = create_access_token("user-123", {"email": "x@y.z"})
    assert isinstance(token, str) and token.count(".") == 2
