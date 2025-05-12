from pydantic_settings import BaseSettings
from functools import lru_cache
import os,re
from dotenv import load_dotenv

load_dotenv()

def ensure_pem_format(key: str, is_private: bool) -> str:
    if is_private:
        if not key.startswith("-----"):
            return '-----BEGIN PRIVATE KEY-----\n'+key+'\n-----END PRIVATE KEY-----'
    else:
        if not key.startswith("-----"):
            return '-----BEGIN PUBLIC KEY-----\n'+key+'\n-----END PUBLIC KEY-----'
    return key

class Settings(BaseSettings):
    # API Settings
    ROOT_PATH: str = os.getenv("ROOT_PATH")
    PROJECT_NAME: str = "mini-oauth2"
    PORT: int = os.getenv("PORT", 3000)
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "")
    EXTERNAL_HOST: str = os.getenv("EXTERNAL_HOST", "http://localhost:3000")
    # Security
    API_KEY_HEADER: str = "X-API-Key"
    API_KEYS: str = os.getenv("API_KEYS", "")
    #  replace empty string with None
    JWT_PRIVATE_KEY: str = os.getenv("JWT_PRIVATE_KEY", "")
    JWT_PUBLIC_KEY: str = os.getenv("JWT_PUBLIC_KEY", "")
    JWT_EXPIRES_IN: int = int(os.getenv("JWT_EXPIRES_IN", 24*60))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "EdDSA")

    
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    # Database
    DATABASE_URL: str = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@localhost:5432/mini_oauth2")
    
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")


    EMAIL_HOST: str = os.getenv("EMAIL_HOST", '')
    EMAIL_PORT: int = os.getenv("EMAIL_PORT", 587)
    EMAIL_USERNAME: str = os.getenv("EMAIL_USERNAME", '')
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", '')
    EMAIL_SSL: bool = os.getenv("EMAIL_SSL", False)
    EMAIL_FROM: str = os.getenv("EMAIL_FROM",'')
    
    class Config:
        case_sensitive = True

settings = Settings()
settings.JWT_PRIVATE_KEY = ensure_pem_format(settings.JWT_PRIVATE_KEY, True)
settings.JWT_PUBLIC_KEY = ensure_pem_format(settings.JWT_PUBLIC_KEY, False)


