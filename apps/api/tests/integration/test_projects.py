"""Integration tests: projects API."""

from __future__ import annotations

import pytest


REGISTER_URL = "/api/v1/auth/register"
PROJECTS_URL = "/api/v1/projects"


async def _register_and_token(client, email: str = "test@example.com") -> str:
    res = await client.post(REGISTER_URL, json={"email": email, "password": "password123"})
    assert res.status_code == 201, res.text
    return res.json()["access_token"]


@pytest.mark.asyncio
async def test_create_project_success(client):
    token = await _register_and_token(client, "proj1@example.com")
    res = await client.post(
        PROJECTS_URL,
        json={"name": "my-app", "source_type": "local_workspace"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["name"] == "my-app"
    assert body["source_type"] == "local_workspace"
    assert body["status"] == "created"
    assert "id" in body


@pytest.mark.asyncio
async def test_create_project_requires_auth(client):
    res = await client.post(PROJECTS_URL, json={"name": "no-auth", "source_type": "zip_upload"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_list_projects(client):
    token = await _register_and_token(client, "proj2@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    await client.post(PROJECTS_URL, json={"name": "app-a", "source_type": "local_workspace"}, headers=headers)
    await client.post(PROJECTS_URL, json={"name": "app-b", "source_type": "zip_upload"}, headers=headers)

    res = await client.get(PROJECTS_URL, headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 2
    names = [p["name"] for p in body["items"]]
    assert "app-a" in names
    assert "app-b" in names


@pytest.mark.asyncio
async def test_get_project_by_id(client):
    token = await _register_and_token(client, "proj3@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_res = await client.post(
        PROJECTS_URL,
        json={"name": "findme", "source_type": "github_repository", "description": "test desc"},
        headers=headers,
    )
    project_id = create_res.json()["id"]

    res = await client.get(f"{PROJECTS_URL}/{project_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["name"] == "findme"
    assert res.json()["description"] == "test desc"


@pytest.mark.asyncio
async def test_get_project_not_found(client):
    token = await _register_and_token(client, "proj4@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    fake_id = "00000000-0000-0000-0000-000000000000"
    res = await client.get(f"{PROJECTS_URL}/{fake_id}", headers=headers)
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_list_projects_isolated_between_users(client):
    token_a = await _register_and_token(client, "usera@example.com")
    token_b = await _register_and_token(client, "userb@example.com")

    await client.post(
        PROJECTS_URL,
        json={"name": "user-a-project", "source_type": "local_workspace"},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    res_b = await client.get(PROJECTS_URL, headers={"Authorization": f"Bearer {token_b}"})
    assert res_b.json()["total"] == 0
