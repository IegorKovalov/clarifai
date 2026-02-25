from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Database
    database_url: str
    sync_database_url: str
    
    # OpenAI
    openai_api_key: str
    
    # LangSmith (for Phase 3, defined now so it's ready)
    langchain_api_key: str = ""
    langchain_tracing_v2: str = "false"
    langchain_project: str = "clarifai"

    class Config:
        env_file = Path(__file__).parent / ".env"
        env_file_encoding = "utf-8"

# Single instance imported everywhere
settings = Settings()