from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pydantic import field_validator

# from dotenv import load_dotenv

# load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8',case_sensitive=False , extra='ignore')
    # API Settings
    ROOT_PATH: str | None = None
    PROJECT_NAME: str = "mini-oauth2"
    ADMIN_API_KEY: str | None = None
    EXTERNAL_DOMAIN: str
    # Security
    API_KEY_HEADER: str = "X-API-Key"
    API_KEYS: list[str] | None = None
    #  replace empty string with None
    # JWT_PRIVATE_KEY: str 
    # JWT_PUBLIC_KEY: str 
    # JWT_EXPIRES_IN_HOURS: int = 24
    # JWT_ALGORITHM: str = "EdDSA"

    
    REDIS_URL: str
    # Database
    DB_URL: str 
    DB_POOL_SIZE: int = 200
    DB_MAX_OVERFLOW: int = 100
    DB_ECHO: bool = False
    
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
    WECHAT_MP_FILE:str|None = None
    WECHAT_MP_FILE_CONTENT:str|None = None

    LINKEDIN_CLIENT_ID: str|None = None
    LINKEDIN_CLIENT_SECRET: str|None = None



    @field_validator("API_KEYS",mode="before")
    @classmethod
    def validate_api_keys(cls, v:str)->list[str]:
        if v is None:
            return []
        return v.split(",")
    
    
settings = Settings()
env = settings

import logging
logging.basicConfig(level=logging.INFO)
# set log format
logging.getLogger().handlers[0].setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))


log = logging.getLogger(__name__)
