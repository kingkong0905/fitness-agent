from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.repositories.plan_repository import PlanRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.user_repository import UserRepository
from app.services.agent_service import AgentService
from app.services.auth_service import AuthService, decode_access_token
from app.services.plan_service import PlanService
from app.services.profile_service import ProfileService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


async def get_profile_repo(db: AsyncSession = Depends(get_db)) -> ProfileRepository:
    return ProfileRepository(db)


async def get_plan_repo(db: AsyncSession = Depends(get_db)) -> PlanRepository:
    return PlanRepository(db)


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
) -> AuthService:
    return AuthService(user_repo)


async def get_profile_service(
    profile_repo: ProfileRepository = Depends(get_profile_repo),
) -> ProfileService:
    return ProfileService(profile_repo)


async def get_plan_service(
    plan_repo: PlanRepository = Depends(get_plan_repo),
    profile_repo: ProfileRepository = Depends(get_profile_repo),
) -> PlanService:
    return PlanService(plan_repo, profile_repo, AgentService())


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repo),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = decode_access_token(token)
    if email is None:
        raise credentials_exception
    user = await user_repo.get_by_email(email)
    if user is None:
        raise credentials_exception
    return user
