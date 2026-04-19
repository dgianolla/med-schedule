import json
from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@host:5432/schedule_db"
    APPHEALTH_BASE_URL: str = "https://back.apphealth.com.br:9090/api-vita"
    APPHEALTH_API_KEY: str = ""
    CORS_ORIGINS: Union[str, List[str]] = '["http://localhost:3000","http://localhost:3001"]'
    LOG_LEVEL: str = "info"
    ENV: str = "development"
    API_PREFIX: str = "/api/v1"

    SUPABASE_URL: Optional[str] = None
    SUPABASE_PUBLISHABLE_KEY: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    SUPABASE_SECRET_KEY: Optional[str] = None

    JWT_SECRET_KEY: str = "super_secret_key_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 horas

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, str):
            return json.loads(self.CORS_ORIGINS)
        return self.CORS_ORIGINS

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()
