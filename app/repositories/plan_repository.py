from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plan import TrainingPlan


class PlanRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id_and_user(self, plan_id: int, user_id: int) -> TrainingPlan | None:
        result = await self.db.execute(
            select(TrainingPlan).where(
                TrainingPlan.id == plan_id,
                TrainingPlan.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int) -> list[TrainingPlan]:
        result = await self.db.execute(
            select(TrainingPlan)
            .where(TrainingPlan.user_id == user_id)
            .order_by(TrainingPlan.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        user_id: int,
        title: str,
        week_start: date,
        generated_plan: str,
        notes: str | None,
    ) -> TrainingPlan:
        plan = TrainingPlan(
            user_id=user_id,
            title=title,
            week_start=week_start,
            generated_plan=generated_plan,
            notes=notes,
        )
        self.db.add(plan)
        await self.db.commit()
        await self.db.refresh(plan)
        return plan

    async def delete(self, plan: TrainingPlan) -> None:
        await self.db.delete(plan)
        await self.db.commit()
