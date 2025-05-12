from typing import Annotated
from fastapi import FastAPI, Depends, APIRouter
from dotenv import load_dotenv
import os
from fastapi import Request
from fastapi.security import APIKeyHeader
from fastapi.exceptions import HTTPException
from fastapi import Security
from app.config import settings

from app.drivers.init_db import init_db
load_dotenv()

init_db()

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == settings.ADMIN_API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Key",
        )

# from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(root_path=settings.ROOT_PATH)

# app.add_middleware(SessionMiddleware, secret_key="!secret")

from app.routers.auth import router as auth_router
from app.routers.clients import router as clients_router
from app.routers.users import router as users_router
from app.routers.user_info import router as user_info_router
from app.routers.signup import router as signup_router
from app.routers.social_login import router as social_login_router
from app.routers.passwords import router as passwords_router

app.include_router(auth_router)
app.include_router(clients_router , dependencies=[Depends(get_api_key)])
app.include_router(users_router , dependencies=[Depends(get_api_key)])
app.include_router(user_info_router)
app.include_router(signup_router)
app.include_router(social_login_router)
app.include_router(passwords_router, prefix="/password/reset")

@app.get("/.well-known/openid-configuration")
async def configuration():
    return {
        "issuer": f"{settings.EXTERNAL_HOST}/",
        "authorization_endpoint": f"{settings.EXTERNAL_HOST}/signin",
        "token_endpoint": f"{settings.EXTERNAL_HOST}/token",
        "userinfo_endpoint": f"{settings.EXTERNAL_HOST}/userinfo",
        # 'revocation_endpoint': f"{settings.EXTERNAL_HOST}/revoke",
        'response_modes_supported': ['query', 'fragment', 'form_post'],
        'grant_types_supported': ['authorization_code'],
        'algorithms_supported': ['EdDSA'],
        'subject_types_supported': ['public'],
        'response_types_supported': ['code'],
        'google_authorization_endpoint': f"{settings.EXTERNAL_HOST}/google/signin",
        'github_authorization_endpoint': f"{settings.EXTERNAL_HOST}/github/signin",
        'apple_authorization_endpoint': f"{settings.EXTERNAL_HOST}/apple/signin",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=settings.PORT , reload=True)