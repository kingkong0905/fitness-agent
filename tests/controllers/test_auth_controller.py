import pytest


@pytest.mark.asyncio
class TestAuthController:
    async def test_register_success(self, client):
        resp = await client.post("/auth/register", json={"email": "u@x.com", "password": "pass123"})
        assert resp.status_code == 201
        assert resp.json()["email"] == "u@x.com"

    async def test_register_duplicate_returns_409(self, client):
        await client.post("/auth/register", json={"email": "u@x.com", "password": "pass123"})
        resp = await client.post("/auth/register", json={"email": "u@x.com", "password": "pass123"})
        assert resp.status_code == 409

    async def test_login_success(self, client):
        await client.post("/auth/register", json={"email": "u@x.com", "password": "pass123"})
        resp = await client.post("/auth/login", data={"username": "u@x.com", "password": "pass123"})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_login_wrong_password_returns_401(self, client):
        await client.post("/auth/register", json={"email": "u@x.com", "password": "pass123"})
        resp = await client.post("/auth/login", data={"username": "u@x.com", "password": "wrong"})
        assert resp.status_code == 401

    async def test_login_unknown_email_returns_401(self, client):
        resp = await client.post("/auth/login", data={"username": "ghost@x.com", "password": "x"})
        assert resp.status_code == 401
