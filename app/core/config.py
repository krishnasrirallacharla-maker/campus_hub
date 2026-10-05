from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "College Management Event System"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "college-event-mgmt-super-secret-jwt-key-change-in-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Database
    DATABASE_URL: str = "postgresql+pg8000://postgres:postgres@localhost:5432/college_events_db"

    # Admin seed defaults
    FIRST_SUPERUSER_EMAIL: str = "admin@college.edu"
    FIRST_SUPERUSER_PASSWORD: str = "AdminPassword123!"
    FIRST_SUPERUSER_NAME: str = "System Administrator"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ]

    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_postgres_url(cls, v: str) -> str:
        if isinstance(v, str):
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+pg8000://", 1)
            elif v.startswith("postgresql://") and "+" not in v:
                return v.replace("postgresql://", "postgresql+pg8000://", 1)
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )


settings = Settings()
