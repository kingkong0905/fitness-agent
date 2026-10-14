import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
class TestUserModel:
    async def test_user_creation(self, db_session):
        user = await UserRepository(db_session).create("model@test.com", "hashed_pw")
        assert isinstance(user, User)
        assert user.id is not None
        assert user.created_at is not None

    async def test_user_email_is_unique(self, db_session):
        repo = UserRepository(db_session)
        await repo.create("dup@test.com", "hash1")
        with pytest.raises(IntegrityError):
            await repo.create("dup@test.com", "hash2")
