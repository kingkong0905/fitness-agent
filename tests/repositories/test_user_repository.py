import pytest

from app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
class TestUserRepository:
    async def test_create_and_get_by_email(self, db_session):
        repo = UserRepository(db_session)
        user = await repo.create("alice@example.com", "hashed")
        assert user.id is not None
        assert user.email == "alice@example.com"

        fetched = await repo.get_by_email("alice@example.com")
        assert fetched is not None
        assert fetched.id == user.id

    async def test_get_by_email_returns_none_for_unknown(self, db_session):
        repo = UserRepository(db_session)
        result = await repo.get_by_email("nobody@example.com")
        assert result is None
