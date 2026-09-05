"""Integration tests: registration and login API."""

from __future__ import annotations

import pytest


REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"


@pytest.mark.asyncio
async def test_register_success(client):
    res = await client.post(REGISTER_URL, json={
        "email": "alice@example.com",
        "password": "password123",
        "full_name": "Alice Test",
    })
    assert res.status_code == 201
    body = res.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "alice@example.com"
    assert body["user"]["full_name"] == "Alice Test"
    assert body["user"]["is_active"] is True


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {"email": "bob@example.com", "password": "password123"}
    await client.post(REGISTER_URL, json=payload)  # first registration
    res = await client.post(REGISTER_URL, json=payload)  # duplicate
    assert res.status_code == 409
    assert "already exists" in res.json()["message"].lower()


@pytest.mark.asyncio
async def test_register_weak_password(client):
    res = await client.post(REGISTER_URL, json={
        "email": "weak@example.com",
        "password": "short",  # < 8 chars
    })
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post(REGISTER_URL, json={
        "email": "charlie@example.com",
        "password": "password123",
    })
    res = await client.post(LOGIN_URL, json={
        "email": "charlie@example.com",
        "password": "password123",
    })
    assert res.status_code == 200
    body = res.json()
    assert body["access_token"]
    assert body["user"]["email"] == "charlie@example.com"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post(REGISTER_URL, json={
        "email": "diana@example.com",
        "password": "password123",
    })
    res = await client.post(LOGIN_URL, json={
        "email": "diana@example.com",
        "password": "wrongpassword",
    })
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    res = await client.post(LOGIN_URL, json={
        "email": "nobody@example.com",
        "password": "password123",
    })
    assert res.status_code == 401
