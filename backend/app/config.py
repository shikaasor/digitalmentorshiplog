import os
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    # Database (Supabase PostgreSQL)
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # JWT
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://localhost:8000","https://digitalmentorshiplog.vercel.app"]
    ALLOWED_HOSTS: Union[List[str], str] = ["*"]

    @field_validator('ALLOWED_ORIGINS', 'ALLOWED_HOSTS', mode='before')
    @classmethod
    def parse_comma_separated(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(',')]
        return v

    # File Storage (Supabase Storage)
    SUPABASE_STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET")
    MAX_FILE_SIZE: int = 10485760  # 10MB

    # Email (optional)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # Application
    APP_NAME: str = "Digital Mentorship Log"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
