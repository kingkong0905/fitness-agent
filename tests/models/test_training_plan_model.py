import json
from datetime import date

import pytest

from app.models.plan import TrainingPlan
from app.repositories.plan_repository import PlanRepository
from app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
class TestTrainingPlanModel:
    async def test_plan_stores_json(self, db_session):
        user = await UserRepository(db_session).create("plan@test.com", "hash")
        plan_data = {"week_summary": "Great week", "days": []}
        plan = await PlanRepository(db_session).create(
            user_id=user.id,
            title="Test Plan",
            week_start=date(2026, 10, 14),
            generated_plan=json.dumps(plan_data),
            notes="Great week",
        )
        assert isinstance(plan, TrainingPlan)
        assert json.loads(plan.generated_plan) == plan_data
        assert plan.week_start == date(2026, 10, 14)
