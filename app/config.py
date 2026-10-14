from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./fitness.db"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    ANTHROPIC_API_KEY: str = ""
    PROMPT_NAME: str = "weekly_plan"
    PROMPT_VERSION: str = "v1"

    model_config = {"env_file": ".env"}


settings = Settings()
