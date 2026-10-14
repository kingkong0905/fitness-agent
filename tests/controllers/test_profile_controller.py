import pytest

from tests.conftest import PROFILE_PAYLOAD


@pytest.mark.asyncio
class TestProfileController:
    async def test_get_profile_unauthenticated(self, client):
        resp = await client.get("/profile")
        assert resp.status_code == 401

    async def test_get_profile_not_found(self, client, auth_headers):
        resp = await client.get("/profile", headers=auth_headers)
        assert resp.status_code == 404

    async def test_create_and_get_profile(self, client, auth_headers):
        resp = await client.post("/profile", json=PROFILE_PAYLOAD, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["full_name"] == "Test User"
        assert data["fitness_level"] == "intermediate"

        resp = await client.get("/profile", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["full_name"] == "Test User"

    async def test_create_profile_twice_upserts(self, client, auth_headers):
        await client.post("/profile", json=PROFILE_PAYLOAD, headers=auth_headers)
        updated = {**PROFILE_PAYLOAD, "age": 35}
        resp = await client.post("/profile", json=updated, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["age"] == 35

    async def test_update_profile(self, client, auth_headers):
        await client.post("/profile", json=PROFILE_PAYLOAD, headers=auth_headers)
        resp = await client.put("/profile", json={"weight_kg": 70.0}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["weight_kg"] == 70.0

    async def test_update_profile_not_found(self, client, auth_headers):
        resp = await client.put("/profile", json={"weight_kg": 70.0}, headers=auth_headers)
        assert resp.status_code == 404
