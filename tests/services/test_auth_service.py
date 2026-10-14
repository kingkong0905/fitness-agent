from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService, hash_password, verify_password


@pytest.mark.asyncio
class TestAuthService:
    def _make_service(self, user=None):
        repo = AsyncMock(spec=UserRepository)
        repo.get_by_email.return_value = user
        repo.create.return_value = MagicMock(id=1, email="a@b.com")
        return AuthService(repo), repo

    async def test_register_new_user(self):
        service, repo = self._make_service(user=None)
        result = await service.register("a@b.com", "pass123")
        repo.create.assert_called_once()
        assert result.email == "a@b.com"

    async def test_register_duplicate_email_raises_409(self):
        service, _ = self._make_service(user=MagicMock())
        with pytest.raises(HTTPException) as exc:
            await service.register("a@b.com", "pass")
        assert exc.value.status_code == 409

    async def test_login_success(self):
        password = "secret"
        user = MagicMock(email="a@b.com", hashed_password=hash_password(password))
        service, _ = self._make_service(user=user)
        token = await service.login("a@b.com", password)
        assert token.token_type == "bearer"
        assert token.access_token

    async def test_login_wrong_password_raises_401(self):
        user = MagicMock(email="a@b.com", hashed_password=hash_password("correct"))
        service, _ = self._make_service(user=user)
        with pytest.raises(HTTPException) as exc:
            await service.login("a@b.com", "wrong")
        assert exc.value.status_code == 401

    async def test_login_unknown_email_raises_401(self):
        service, _ = self._make_service(user=None)
        with pytest.raises(HTTPException) as exc:
            await service.login("nobody@b.com", "pass")
        assert exc.value.status_code == 401

    def test_hash_and_verify_password(self):
        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed)
        assert not verify_password("wrong", hashed)
