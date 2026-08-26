from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./risk_manager.db"
    risk_engine_mode: str = Field(default="demo", pattern="^(demo|llm)$")
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str | None = None
    cors_origins: str = "http://localhost:5173"
    max_input_length: int = 10_000
    rate_limit_per_minute: int = 30
    default_user_id: str = "demo-user"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
