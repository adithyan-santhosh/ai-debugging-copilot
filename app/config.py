import os
from functools import lru_cache


class Settings:
    app_name: str = "AI Debugging Copilot"
    environment: str = os.getenv("ENVIRONMENT", "development")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    pg_dsn: str = os.getenv("POSTGRES_DSN", "postgresql://user:password@localhost:5432/debugcopilot")
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    vector_dir: str = os.getenv("VECTOR_DIR", "./vectors")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
