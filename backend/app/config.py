import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@localhost:5432/school_attendance"
    )
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    allowed_hosts: list = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    
    model_config = ConfigDict(env_file=".env")

settings = Settings()