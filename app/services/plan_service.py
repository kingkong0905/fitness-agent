import json
from datetime import date

from fastapi import HTTPException, status

from app.models.plan import TrainingPlan
from app.repositories.plan_repository import PlanRepository
from app.repositories.profile_repository import ProfileRepository
from app.schemas.plan import PlanOut
from app.services.agent_service import AgentService


class PlanService:
    def __init__(
        self,
        plan_repo: PlanRepository,
        profile_repo: ProfileRepository,
        agent: AgentService,
    ):
        self.plan_repo = plan_repo
        self.profile_repo = profile_repo
        self.agent = agent

    async def generate(
        self, user_id: int, week_start: date, extra_notes: str | None
    ) -> PlanOut:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please complete your profile before generating a plan",
            )

        plan_data = await self.agent.generate_weekly_plan(profile, week_start, extra_notes)
        plan = await self.plan_repo.create(
            user_id=user_id,
            title=f"Weekly Plan — {week_start.strftime('%B %d, %Y')}",
            week_start=week_start,
            generated_plan=json.dumps(plan_data),
            notes=plan_data.get("week_summary"),
        )
        return self._to_out(plan)

    async def list(self, user_id: int) -> list[TrainingPlan]:
        return await self.plan_repo.list_by_user(user_id)

    async def get(self, plan_id: int, user_id: int) -> PlanOut:
        plan = await self.plan_repo.get_by_id_and_user(plan_id, user_id)
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
        return self._to_out(plan)

    async def delete(self, plan_id: int, user_id: int) -> None:
        plan = await self.plan_repo.get_by_id_and_user(plan_id, user_id)
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
        await self.plan_repo.delete(plan)

    def _to_out(self, plan: TrainingPlan) -> PlanOut:
        return PlanOut(
            id=plan.id,
            user_id=plan.user_id,
            title=plan.title,
            week_start=plan.week_start,
            generated_plan=json.loads(plan.generated_plan),
            notes=plan.notes,
            created_at=plan.created_at,
        )
