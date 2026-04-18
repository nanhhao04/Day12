import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")

    # App Info
    app_name: str = Field(default="Production ReAct Agent", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")

    # LLM
    llm_provider: str = Field(default="mock", env="LLM_PROVIDER")
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    llm_model: str = Field(default="gpt-4o-mini", env="LLM_MODEL")

    # Security
    agent_api_key: str = Field(default="day12-lab6-secret-key", env="AGENT_API_KEY")
    jwt_secret: str = Field(default="super-secret-jwt-key", env="JWT_SECRET")
    allowed_origins: str = Field(default="*", env="ALLOWED_ORIGINS")

    # Rate limiting
    rate_limit_per_minute: int = Field(default=10, env="RATE_LIMIT_PER_MINUTE")

    # Budget
    monthly_budget_usd: float = Field(default=10.0, env="MONTHLY_BUDGET_USD")

    # Storage
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    model_config = SettingsConfigDict(
        env_file=".env.local", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins(self) -> List[str]:
        return self.allowed_origins.split(",")

settings = Settings()
