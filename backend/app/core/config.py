"""Application configuration management."""
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central application configuration loaded from environment variables."""

    # Application metadata
    app_name: str = Field("AI Knowledge Engine", env="APP_NAME")
    environment: str = Field("local", env="APP_ENV")
    debug: bool = Field(False, env="DEBUG")

    # Networking
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    cors_allow_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ],
        env="CORS_ALLOW_ORIGINS",
    )

    # Database
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")

    # Paths & storage
    knowledge_base_path: str = Field(
        "backend/data/knowledge_base.pkl", env="KNOWLEDGE_BASE_PATH"
    )
    faiss_index_path: str = Field(
        "backend/data/faiss_index.bin", env="FAISS_INDEX_PATH"
    )

    # Model / AI providers
    embedding_model_name: str = Field(
        "all-MiniLM-L6-v2", env="EMBEDDING_MODEL_NAME"
    )
    language_model_path: Optional[str] = Field(
        default=None, env="LANGUAGE_MODEL_PATH"
    )
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", env="OPENAI_MODEL")
    openai_embedding_model: str = Field(
        "text-embedding-3-large", env="OPENAI_EMBEDDING_MODEL"
    )

    # Security / Authentication
    secret_key: str = Field(
        default="your-secret-key-change-in-production", 
        env="SECRET_KEY"
    )
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30 * 24 * 60, env="ACCESS_TOKEN_EXPIRE_MINUTES")  # 30 days

    # Integrations
    huggingface_token: Optional[str] = Field(default=None, env="HUGGINGFACE_TOKEN")
    google_service_account_file: Optional[str] = Field(
        default=None, env="GOOGLE_SERVICE_ACCOUNT_FILE"
    )
    google_sheet_id: Optional[str] = Field(default=None, env="GOOGLE_SHEET_ID")
    slack_webhook_url: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")

    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("cors_allow_origins", pre=True)
    def _split_origins(cls, value):  # noqa: D401,N805
        """Ensures CORS origins may be provided as comma separated string."""

        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance."""

    return Settings()
