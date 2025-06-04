from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pydantic import field_validator

# from dotenv import load_dotenv

# load_dotenv()

def ensure_pem_format(key: str, is_private: bool) -> str:
    if is_private:
        if not key.startswith("-----"):
            return '-----BEGIN PRIVATE KEY-----\n'+key+'\n-----END PRIVATE KEY-----'
    else:
        if not key.startswith("-----"):
            return '-----BEGIN PUBLIC KEY-----\n'+key+'\n-----END PUBLIC KEY-----'
    return key

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8',case_sensitive=False , extra='ignore')
    # API Settings
    ROOT_PATH: str = os.getenv("ROOT_PATH")
    PROJECT_NAME: str = "mini-oauth2"
    ADMIN_API_KEY: str | None = None
    EXTERNAL_DOMAIN: str = "http://localhost:3000"
    # Security
    API_KEY_HEADER: str = "X-API-Key"
    API_KEYS: list[str] | None = None
    #  replace empty string with None
    JWT_PRIVATE_KEY: str 
    JWT_PUBLIC_KEY: str 
    JWT_EXPIRES_IN: int = 24*60
    JWT_ALGORITHM: str = "EdDSA"

    
    REDIS_URL: str ="redis://localhost:6379/0"
    # Database
    DB_URL: str ="postgresql+asyncpg://postgres:postgres@localhost:5431/minioauth2"
    
    IS_REDIS_CLUSTER: bool = False


    EMAIL_HOST: str|None = None
    EMAIL_PORT: int | None = None
    EMAIL_USERNAME: str | None = None
    EMAIL_PASSWORD: str | None = None
    EMAIL_SSL: bool | None = True
    EMAIL_FROM: str | None = EMAIL_USERNAME

    GOOGLE_CLIENT_ID: str|None = None
    GOOGLE_CLIENT_SECRET: str|None = None

    GITHUB_CLIENT_ID: str|None = None
    GITHUB_CLIENT_SECRET: str|None = None

    APPLE_CLIENT_ID: str|None = None
    APPLE_CLIENT_SECRET: str|None = None

    WECHAT_APPID: str|None = None
    WECHAT_APPSECRET: str|None = None

    LINKEDIN_CLIENT_ID: str|None = None
    LINKEDIN_CLIENT_SECRET: str|None = None


    @field_validator("API_KEYS",mode="before")
    @classmethod
    def validate_api_keys(cls, v:str)->list[str]:
        if v is None:
            return []
        return v.split(",")
    

    
settings = Settings()
settings.JWT_PRIVATE_KEY = ensure_pem_format(settings.JWT_PRIVATE_KEY, True)
settings.JWT_PUBLIC_KEY = ensure_pem_format(settings.JWT_PUBLIC_KEY, False)
env = settings

import logging
logging.basicConfig(level=logging.INFO)
# set log format
logging.getLogger().handlers[0].setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))


log = logging.getLogger(__name__)
