from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "AURORA"
    environment: str = "development"
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "aurora"
    hf_api_url: Optional[str] = None
    hf_api_key: Optional[str] = None
    max_file_bytes: int = 200000
    scan_extensions: tuple[str, ...] = (
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".java",
        ".go",
        ".rb",
        ".php",
        ".cs",
        ".cpp",
        ".c",
        ".rs",
        ".swift",
        ".kt",
        ".kts",
        ".sql",
        ".sh",
        ".yaml",
        ".yml",
        ".json",
        ".toml",
        ".ini",
        ".md",
    )

    class Config:
        env_file = ".env"


settings = Settings()
