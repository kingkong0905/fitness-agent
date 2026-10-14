import json

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.plan import TrainingPlan
from app.models.profile import MemberProfile
from app.models.user import User
from app.schemas.plan import PlanGenerateRequest, PlanListItem, PlanOut
from app.services.agent import generate_weekly_plan

router = APIRouter(prefix="/plans", tags=["plans"])


def _plan_to_out(plan: TrainingPlan) -> PlanOut:
    return PlanOut(
        id=plan.id,
        user_id=plan.user_id,
        title=plan.title,
        week_start=plan.week_start,
        generated_plan=json.loads(plan.generated_plan),
        notes=plan.notes,
        created_at=plan.created_at,
    )


@router.post("/generate", response_model=PlanOut, status_code=status.HTTP_201_CREATED)
async def generate_plan(
    payload: PlanGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MemberProfile).where(MemberProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please complete your profile before generating a plan",
        )

    plan_data = await generate_weekly_plan(profile, payload.week_start, payload.extra_notes)

    title = f"Weekly Plan — {payload.week_start.strftime('%B %d, %Y')}"
    plan = TrainingPlan(
        user_id=current_user.id,
        title=title,
        week_start=payload.week_start,
        generated_plan=json.dumps(plan_data),
        notes=plan_data.get("week_summary"),
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return _plan_to_out(plan)


@router.get("", response_model=list[PlanListItem])
async def list_plans(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TrainingPlan)
        .where(TrainingPlan.user_id == current_user.id)
        .order_by(TrainingPlan.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{plan_id}", response_model=PlanOut)
async def get_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TrainingPlan).where(
            TrainingPlan.id == plan_id, TrainingPlan.user_id == current_user.id
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return _plan_to_out(plan)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TrainingPlan).where(
            TrainingPlan.id == plan_id, TrainingPlan.user_id == current_user.id
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    await db.delete(plan)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
