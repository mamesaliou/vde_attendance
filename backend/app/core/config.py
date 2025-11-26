import os
from enum import Enum
from typing import List, ClassVar, Dict, Any
from pydantic_settings import BaseSettings
from functools import lru_cache


class UserRole(Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"


class BackendSettings(BaseSettings):

    CONNECTION_STRING: str = os.getenv("DATABASE_URL", "sqlite:///./user_database.db")
    DEBUG: bool = False if os.path.exists('.env') else True

    USER_TOKEN_PREFIX: str = "user_token_"
    USER_DATA_PREFIX: str = "user_data_"

    PROJECT_NAME: str = "app API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DESCRIPTION: str = "app API - Une API pour la gestion des authentifications"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    API_KEY: str = os.getenv("API_KEY", "your-secret-key-here")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "RS256")
    JWT_ISSUER: str = os.getenv("JWT_ISSUER", "vde-attendance")
    JWT_AUDIENCE: str = os.getenv("JWT_AUDIENCE", "vde-attendance-api")
    JWT_SERVER_AUDIENCE: str = os.getenv("JWT_SERVER_AUDIENCE", "vde-attendance-api")
    TRUSTED_SERVICES: List[str] = os.getenv("TRUSTED_SERVICES", "").split(",") if os.getenv("TRUSTED_SERVICES") else []
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = 60
    
    # Chemins des clés RSA pour JWT
    PRIVATE_KEY_PATH: str = os.getenv("PRIVATE_KEY_PATH", "./secrets/private_key.pem")
    PUBLIC_KEY_PATH: str = os.getenv("PUBLIC_KEY_PATH", "./secrets/public_key.pem")
    PRIVATE_KEY_PASSWORD: str = os.getenv("PRIVATE_KEY_PASSWORD", "")
    
    BACKEND_CORS_ORIGINS: List[str] = os.getenv("BACKEND_CORS_ORIGINS", "*").split(",")
    
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    MAX_BODY_SIZE: int = 1024 * 1024
    MAX_FILE_SIZE: int = 5 * 1024 * 1024
    
    PUBLIC_ENDPOINTS: ClassVar[List[str]] = [
        "/api/v1/health",  
        "/docs",         
        "/redoc",   
        "/openapi.json", 
        "/api/v1/docs",
        "/api/v1/redoc",
        "/api/v1/openapi.json",
        "/api/v1/auth/public-key",
        "/api/v1/auth/register",
        "/api/v1/auth/token",
        "/flutter_service_worker.js",
        "/assets/",        
        "/icons/",
        "/favicon.ico",
        "/manifest.json",
        "/.well-known/",
        "/static/",
        "/health",
    ]

    PUBLIC_INTERNAL_ENDPOINTS: ClassVar[List[str]] = [
        "/api/v1/internal/",
    ]

    MIDDLEWARE_CONFIG: ClassVar[List[Dict[str, Any]]] = [
        {
            "name": "request_logging",
            "class": "request_logging_middleware",
            "enabled": True,
            "description": "Logger d'abord pour voir toutes les requêtes"
        },
        {
            "name": "request_size",
            "class": "request_size_middleware",
            "enabled": True,
            "description": "Vérifier la taille avant tout traitement"
        },
        {
            "name": "rate_limit",
            "class": "rate_limit_middleware",
            "enabled": True,
            "description": "Limiter le taux de requêtes"
        },
        {
            "name": "security",
            "class": "SecurityMiddleware",
            "enabled": True, 
            "description": "Appliquer les en-têtes de sécurité"
        },
        {
            "name": "verify_token",
            "class": "verify_token",
            "enabled": True,
            "description": "Vérifier l'authentification"
        },
        {
            "name": "catch_exceptions",
            "class": "catch_exceptions_middleware",
            "enabled": True,
            "description": "Attraper les exceptions en dernier"
        }
    ]

    def configure_middleware(self) -> List[Dict[str, Any]]:
        middleware_config = self.MIDDLEWARE_CONFIG.copy()
        if self.DEBUG:
            for middleware in middleware_config:
                if middleware["name"] == "rate_limit":
                    middleware["enabled"] = False
                    break
        return middleware_config

    class Config:
        case_sensitive = True
        env_file = ".env.example" if os.path.exists(".env.example") else ".env"
        env_prefix = "APP_SOLUTIONS_"
        validate_default = True
        extra = "ignore"

@lru_cache()
def get_settings() -> BackendSettings:
    return BackendSettings()

settings = get_settings()
