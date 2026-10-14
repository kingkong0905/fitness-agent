from fastapi import HTTPException, status

from app.models.profile import MemberProfile
from app.repositories.profile_repository import ProfileRepository


class ProfileService:
    def __init__(self, profile_repo: ProfileRepository):
        self.profile_repo = profile_repo

    async def get(self, user_id: int) -> MemberProfile:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        return profile

    async def upsert(self, user_id: int, data: dict) -> MemberProfile:
        existing = await self.profile_repo.get_by_user_id(user_id)
        if existing:
            return await self.profile_repo.update(existing, data)
        return await self.profile_repo.create(user_id, data)

    async def update(self, user_id: int, data: dict) -> MemberProfile:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        return await self.profile_repo.update(profile, data)
