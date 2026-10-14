from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import MemberProfile


class ProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: int) -> MemberProfile | None:
        result = await self.db.execute(
            select(MemberProfile).where(MemberProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: int, data: dict) -> MemberProfile:
        profile = MemberProfile(user_id=user_id, **data)
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def update(self, profile: MemberProfile, data: dict) -> MemberProfile:
        for field, value in data.items():
            setattr(profile, field, value)
        profile.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile
