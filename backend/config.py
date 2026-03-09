from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Database
    database_url: str
    sync_database_url: str
    
    # OpenAI
    openai_api_key: str

    # Anthropic
    anthropic_api_key: str

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""

    
    # Admin secret — required to create tenants (set in .env)
    admin_secret: str

    # LangSmith (for Phase 3, defined now so it's ready)
    langchain_api_key: str = ""
    langchain_tracing_v2: str = "false"
    langchain_project: str = "clarifai"

    class Config:
        env_file = Path(__file__).parent / ".env"
        env_file_encoding = "utf-8"

# Single instance imported everywhere
settings = Settings()