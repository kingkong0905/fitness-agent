from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.repositories.profile_repository import ProfileRepository
from app.services.profile_service import ProfileService


@pytest.mark.asyncio
class TestProfileService:
    def _repo(self, profile=None):
        repo = AsyncMock(spec=ProfileRepository)
        repo.get_by_user_id.return_value = profile
        repo.create.return_value = MagicMock(id=1, user_id=10)
        repo.update.return_value = MagicMock(id=1, user_id=10, age=31)
        return repo

    async def test_get_existing_profile(self):
        profile = MagicMock()
        service = ProfileService(self._repo(profile=profile))
        result = await service.get(user_id=10)
        assert result is profile

    async def test_get_missing_profile_raises_404(self):
        service = ProfileService(self._repo(profile=None))
        with pytest.raises(HTTPException) as exc:
            await service.get(user_id=10)
        assert exc.value.status_code == 404

    async def test_upsert_creates_when_missing(self):
        repo = self._repo(profile=None)
        service = ProfileService(repo)
        await service.upsert(user_id=10, data={"full_name": "Alice"})
        repo.create.assert_called_once_with(10, {"full_name": "Alice"})

    async def test_upsert_updates_when_existing(self):
        repo = self._repo(profile=MagicMock())
        service = ProfileService(repo)
        await service.upsert(user_id=10, data={"age": 31})
        repo.update.assert_called_once()

    async def test_update_missing_profile_raises_404(self):
        service = ProfileService(self._repo(profile=None))
        with pytest.raises(HTTPException) as exc:
            await service.update(user_id=10, data={"age": 31})
        assert exc.value.status_code == 404
