from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_current_user, get_plan_service
from app.models.user import User
from app.schemas.plan import PlanGenerateRequest, PlanListItem, PlanOut
from app.services.plan_service import PlanService

router = APIRouter(prefix="/plans", tags=["plans"])


@router.post("/generate", response_model=PlanOut, status_code=status.HTTP_201_CREATED)
async def generate_plan(
    payload: PlanGenerateRequest,
    current_user: User = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service),
):
    return await service.generate(current_user.id, payload.week_start, payload.extra_notes)


@router.get("", response_model=list[PlanListItem])
async def list_plans(
    current_user: User = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service),
):
    return await service.list(current_user.id)


@router.get("/{plan_id}", response_model=PlanOut)
async def get_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service),
):
    return await service.get(plan_id, current_user.id)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service),
):
    await service.delete(plan_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
