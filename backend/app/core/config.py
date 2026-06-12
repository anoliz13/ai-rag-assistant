from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    project_name: str = "AI RAG Assistant"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"

    database_url: str = "postgresql+asyncpg://raguser:ragpass@postgres:5432/ragdb"
    database_url_sync: str = "postgresql://raguser:ragpass@postgres:5432/ragdb"

    redis_url: str = "redis://redis:6379/0"

    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "documents"

    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    llm_provider: str = "claude"
    llm_model: str = "claude-sonnet-4-20250514"

    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"

    chunk_size: int = 1000
    chunk_overlap: int = 200

    vector_store: str = "pgvector"

    rate_limit_per_minute: int = 30

    model_config = {"env_file": ".env", "extra": "allow"}


settings = Settings()
