from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str = "sqlite:///./main.db"
    
    # Configuración JWT
    SECRET_KEY: str = "tu_clave_secreta_aqui"  # Cambiar en producción
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configuración API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Dormilon Industries API"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()