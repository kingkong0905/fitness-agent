import json
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.repositories.plan_repository import PlanRepository
from app.repositories.profile_repository import ProfileRepository
from app.services.plan_service import PlanService


@pytest.mark.asyncio
class TestPlanService:
    def _make_service(self, profile=None, plan=None, plans=None):
        plan_repo = AsyncMock(spec=PlanRepository)
        profile_repo = AsyncMock(spec=ProfileRepository)
        agent = AsyncMock()

        profile_repo.get_by_user_id.return_value = profile

        dummy_plan = MagicMock()
        dummy_plan.id = 1
        dummy_plan.user_id = 5
        dummy_plan.title = "Weekly Plan — October 14, 2026"
        dummy_plan.week_start = date(2026, 10, 14)
        dummy_plan.generated_plan = json.dumps({"week_summary": "Good week", "days": []})
        dummy_plan.notes = "Good week"
        dummy_plan.created_at = MagicMock()

        plan_repo.create.return_value = dummy_plan
        plan_repo.get_by_id_and_user.return_value = plan if plan is not None else dummy_plan
        plan_repo.list_by_user.return_value = plans or [dummy_plan]
        agent.generate_weekly_plan.return_value = {"week_summary": "Good week", "days": []}

        return PlanService(plan_repo, profile_repo, agent), plan_repo, profile_repo, agent

    async def test_generate_raises_400_without_profile(self):
        service, _, _, _ = self._make_service(profile=None)
        with pytest.raises(HTTPException) as exc:
            await service.generate(user_id=5, week_start=date(2026, 10, 14), extra_notes=None)
        assert exc.value.status_code == 400

    async def test_generate_calls_agent_and_saves(self):
        service, plan_repo, _, agent = self._make_service(profile=MagicMock())
        result = await service.generate(user_id=5, week_start=date(2026, 10, 14), extra_notes=None)
        agent.generate_weekly_plan.assert_called_once()
        plan_repo.create.assert_called_once()
        assert result.notes == "Good week"

    async def test_list_returns_plans(self):
        service, plan_repo, _, _ = self._make_service(profile=MagicMock())
        result = await service.list(user_id=5)
        plan_repo.list_by_user.assert_called_once_with(5)
        assert len(result) == 1

    async def test_get_missing_plan_raises_404(self):
        service, plan_repo, _, _ = self._make_service()
        plan_repo.get_by_id_and_user.return_value = None
        with pytest.raises(HTTPException) as exc:
            await service.get(plan_id=99, user_id=5)
        assert exc.value.status_code == 404

    async def test_delete_missing_plan_raises_404(self):
        service, plan_repo, _, _ = self._make_service()
        plan_repo.get_by_id_and_user.return_value = None
        with pytest.raises(HTTPException) as exc:
            await service.delete(plan_id=99, user_id=5)
        assert exc.value.status_code == 404

    async def test_delete_calls_repo(self):
        plan = MagicMock()
        service, plan_repo, _, _ = self._make_service()
        plan_repo.get_by_id_and_user.return_value = plan
        await service.delete(plan_id=1, user_id=5)
        plan_repo.delete.assert_called_once_with(plan)
