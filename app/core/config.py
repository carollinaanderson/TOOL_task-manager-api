from __future__ import annotations
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Task Manager API"
    app_env: str = "development"
    app_debug: bool = False
    app_secret_key: str = "insecure-dev-only"
    access_token_expire_minutes: int = 30
    database_url: str = "postgresql+psycopg2://task_user:task_pass@db:5432/task_manager"

    model_config = {"env_file": ".env", "case_sensitive": False}


@lru_cache
def get_settings() -> Settings:
    return Settings()
