from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://seace_user:seace_password@localhost:5433/seace_db"
    
    # API Keys
    GEMINI_API_KEY: str = ""
    
    # Power BI
    POWERBI_IFRAME_URL: str = ""
    
    # JWT
    SECRET_KEY: str = "your_super_secret_jwt_key_here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SEACE ProjectFinder"
    
    # OSCE Configuration
    OSCE_BASE_URL: str = "https://contratacionesabiertas.osce.gob.pe"
    OSCE_API_URL: str = "https://contratacionesabiertas.osce.gob.pe/api"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Rate Limiting
    GEMINI_RATE_LIMIT_PER_MINUTE: int = 60
    OSCE_RATE_LIMIT_PER_MINUTE: int = 30
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # CORS - Permitir túneles de VS Code y otros dominios
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000", 
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "https://*.devtunnels.ms",
        "https://*.devtunnels.com",
        "https://*.vscode-cdn.net",
        "https://vscode.dev",
        "*"  # Permitir todos los orígenes en desarrollo
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
