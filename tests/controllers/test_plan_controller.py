from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import PROFILE_PAYLOAD

MOCK_PLAN = {
    "week_summary": "A solid intermediate week.",
    "days": [
        {
            "day": "Monday",
            "focus": "Upper Body",
            "duration_minutes": 45,
            "warmup": ["Arm circles"],
            "exercises": [],
            "cooldown": ["Stretch"],
            "calories_estimate": 300,
        }
    ],
    "weekly_tips": ["Stay hydrated"],
    "nutrition_note": "Eat enough protein.",
}


@pytest.mark.asyncio
class TestPlanController:
    async def test_generate_plan_requires_auth(self, client):
        resp = await client.post("/plans/generate", json={"week_start": "2026-10-14"})
        assert resp.status_code == 401

    async def test_generate_plan_requires_profile(self, client, auth_headers):
        resp = await client.post(
            "/plans/generate", json={"week_start": "2026-10-14"}, headers=auth_headers
        )
        assert resp.status_code == 400

    async def test_generate_plan_success(self, client, auth_headers):
        await client.post("/profile", json=PROFILE_PAYLOAD, headers=auth_headers)
        with patch(
            "app.services.agent_service.AgentService.generate_weekly_plan",
            new_callable=AsyncMock,
            return_value=MOCK_PLAN,
        ):
            resp = await client.post(
                "/plans/generate", json={"week_start": "2026-10-14"}, headers=auth_headers
            )
        assert resp.status_code == 201
        data = resp.json()
        assert data["notes"] == "A solid intermediate week."
        assert "generated_plan" in data

    async def test_list_plans_empty(self, client, auth_headers):
        resp = await client.get("/plans", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_get_plan_not_found(self, client, auth_headers):
        resp = await client.get("/plans/999", headers=auth_headers)
        assert resp.status_code == 404

    async def test_delete_plan(self, client, auth_headers):
        await client.post("/profile", json=PROFILE_PAYLOAD, headers=auth_headers)
        with patch(
            "app.services.agent_service.AgentService.generate_weekly_plan",
            new_callable=AsyncMock,
            return_value=MOCK_PLAN,
        ):
            create_resp = await client.post(
                "/plans/generate", json={"week_start": "2026-10-14"}, headers=auth_headers
            )
        plan_id = create_resp.json()["id"]

        del_resp = await client.delete(f"/plans/{plan_id}", headers=auth_headers)
        assert del_resp.status_code == 204

        get_resp = await client.get(f"/plans/{plan_id}", headers=auth_headers)
        assert get_resp.status_code == 404
