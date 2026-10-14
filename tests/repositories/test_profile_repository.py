import pytest
import pytest_asyncio

from app.repositories.profile_repository import ProfileRepository
from app.repositories.user_repository import UserRepository

_PROFILE_DATA = {
    "full_name": "Bob",
    "age": 30,
    "gender": "male",
    "weight_kg": 80.0,
    "height_cm": 180.0,
    "fitness_level": "beginner",
    "goals": "weight loss",
    "available_days": "Monday,Wednesday",
    "equipment": "bodyweight",
}


@pytest.mark.asyncio
class TestProfileRepository:
    @pytest_asyncio.fixture
    async def user(self, db_session):
        return await UserRepository(db_session).create("bob@example.com", "hashed")

    async def test_create_and_get(self, db_session, user):
        repo = ProfileRepository(db_session)
        profile = await repo.create(user.id, _PROFILE_DATA)
        assert profile.user_id == user.id
        assert profile.full_name == "Bob"

        fetched = await repo.get_by_user_id(user.id)
        assert fetched is not None
        assert fetched.id == profile.id

    async def test_get_returns_none_for_missing(self, db_session, user):
        repo = ProfileRepository(db_session)
        result = await repo.get_by_user_id(user.id)
        assert result is None

    async def test_update(self, db_session, user):
        repo = ProfileRepository(db_session)
        profile = await repo.create(user.id, _PROFILE_DATA)
        updated = await repo.update(profile, {"age": 31, "weight_kg": 78.0})
        assert updated.age == 31
        assert updated.weight_kg == 78.0
