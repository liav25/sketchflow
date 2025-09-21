from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # App settings
    app_name: str = "SketchFlow Backend"
    app_env: str = "production"  # development, production
    debug: bool = False
    # Mocking settings (useful in dev)
    mock_mode: bool = False  # When true, conversion returns mock output
    mock_latency_ms: int = 0  # Optional artificial delay for mocks
    
    # CORS settings (dev-friendly: keep as raw string to avoid parsing issues)
    # In dev we allow-all via app.main; this value is not critical.
    allowed_origins: str = "*"
    
    # File upload settings
    max_file_size_mb: int = 10
    allowed_file_types: List[str] = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    
    # Storage settings
    storage_path: str = "storage"

    # Database settings
    database_url: str = "sqlite+aiosqlite:///./storage/sketchflow.db"
    
    # Pydantic v2 style config: ignore unknown env vars to avoid dev friction
    # Look for .env in parent directory (project root)
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


settings = Settings()
