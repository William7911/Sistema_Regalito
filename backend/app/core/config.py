import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://regalito_admin:Regalito_2026@localhost:5433/regalito_pos")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:8000,http://localhost:3000")
    FEL_ENABLED: bool = os.getenv("FEL_ENABLED", "true").lower() in ("1", "true", "yes")
    FEL_API_URL: str = os.getenv("FEL_API_URL", "")
    FEL_API_KEY: str = os.getenv("FEL_API_KEY", "")
    FEL_TIMEOUT: int = int(os.getenv("FEL_TIMEOUT", "15"))
    FEL_SERIE: str = os.getenv("FEL_SERIE", "FEL")
    FEL_EMISOR_NIT: str = os.getenv("FEL_EMISOR_NIT", "")
    FEL_EMISOR_NOMBRE: str = os.getenv("FEL_EMISOR_NOMBRE", "")

    # Configuración de Servidor de Correo (SMTP)
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "Tienda El Regalito")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")
    SMTP_USE_SSL: bool = os.getenv("SMTP_USE_SSL", "false").lower() in ("1", "true", "yes")

    @property
    def cors_origins_list(self) -> list:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"

settings = Settings()
