import pytest

from app.models.profile import MemberProfile
from app.repositories.profile_repository import ProfileRepository
from app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
class TestMemberProfileModel:
    async def test_profile_fields(self, db_session):
        user = await UserRepository(db_session).create("prof@test.com", "hash")
        profile = await ProfileRepository(db_session).create(user.id, {
            "full_name": "Jane Doe",
            "age": 25,
            "gender": "female",
            "weight_kg": 60.0,
            "height_cm": 165.0,
            "fitness_level": "advanced",
            "goals": "endurance",
            "available_days": "Tuesday,Thursday,Saturday",
            "equipment": "treadmill,resistance bands",
            "health_notes": "mild knee pain",
        })
        assert isinstance(profile, MemberProfile)
        assert profile.user_id == user.id
        assert profile.fitness_level == "advanced"
        assert profile.health_notes == "mild knee pain"

    async def test_profile_updated_at_set_on_update(self, db_session):
        user = await UserRepository(db_session).create("upd@test.com", "hash")
        repo = ProfileRepository(db_session)
        profile = await repo.create(user.id, {
            "full_name": "Tim", "age": 22, "gender": "male",
            "weight_kg": 70.0, "height_cm": 175.0, "fitness_level": "beginner",
            "goals": "general fitness", "available_days": "Monday", "equipment": "bodyweight",
        })
        updated = await repo.update(profile, {"age": 23})
        assert updated.age == 23
        assert updated.updated_at is not None
