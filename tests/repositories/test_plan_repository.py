import json
from datetime import date

import pytest
import pytest_asyncio

from app.repositories.plan_repository import PlanRepository
from app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
class TestPlanRepository:
    @pytest_asyncio.fixture
    async def user(self, db_session):
        return await UserRepository(db_session).create("carol@example.com", "hashed")

    async def test_create_and_get(self, db_session, user):
        repo = PlanRepository(db_session)
        plan = await repo.create(
            user_id=user.id,
            title="Week Plan",
            week_start=date(2026, 10, 14),
            generated_plan=json.dumps({"week_summary": "Test week"}),
            notes="Test week",
        )
        assert plan.id is not None
        assert plan.user_id == user.id

        fetched = await repo.get_by_id_and_user(plan.id, user.id)
        assert fetched is not None
        assert fetched.title == "Week Plan"

    async def test_get_returns_none_for_wrong_user(self, db_session, user):
        repo = PlanRepository(db_session)
        plan = await repo.create(
            user_id=user.id, title="Plan",
            week_start=date(2026, 10, 14), generated_plan="{}", notes=None,
        )
        result = await repo.get_by_id_and_user(plan.id, user_id=9999)
        assert result is None

    async def test_list_by_user(self, db_session, user):
        repo = PlanRepository(db_session)
        await repo.create(user_id=user.id, title="Plan A", week_start=date(2026, 10, 7), generated_plan="{}", notes=None)
        await repo.create(user_id=user.id, title="Plan B", week_start=date(2026, 10, 14), generated_plan="{}", notes=None)
        plans = await repo.list_by_user(user.id)
        assert len(plans) == 2

    async def test_delete(self, db_session, user):
        repo = PlanRepository(db_session)
        plan = await repo.create(
            user_id=user.id, title="Plan",
            week_start=date(2026, 10, 14), generated_plan="{}", notes=None,
        )
        await repo.delete(plan)
        result = await repo.get_by_id_and_user(plan.id, user.id)
        assert result is None
