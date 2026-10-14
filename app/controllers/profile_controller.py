from fastapi import APIRouter, Depends, status

from app.dependencies import get_current_user, get_profile_service
from app.models.user import User
from app.schemas.profile import ProfileCreate, ProfileOut, ProfileUpdate
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileOut)
async def get_profile(
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
):
    return await service.get(current_user.id)


@router.post("", response_model=ProfileOut, status_code=status.HTTP_201_CREATED)
async def create_profile(
    payload: ProfileCreate,
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
):
    return await service.upsert(current_user.id, payload.model_dump())


@router.put("", response_model=ProfileOut)
async def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
):
    return await service.update(current_user.id, payload.model_dump(exclude_none=True))
