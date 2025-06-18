from typing import Annotated
from fastapi import FastAPI, Depends, APIRouter, Response
from dotenv import load_dotenv
import os
from fastapi import Request
from fastapi.security import APIKeyHeader
from fastapi.exceptions import HTTPException
from fastapi import Security
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from app.drivers.db import create_db_if_not_exists

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == settings.ADMIN_API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Key",
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_if_not_exists()
    await asyncio.create_subprocess_shell("uv run alembic upgrade head")
    yield



# from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(root_path=settings.ROOT_PATH, title="Mini OAuth2", description="Mini OAuth2 is a simple OAuth 2.0 server implementation." , lifespan=lifespan)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers.auth import router as auth_router
from app.routers.clients import router as clients_router
from app.routers.users import router as users_router
from app.routers.user_info import router as user_info_router
from app.routers.signup import router as signup_router
from app.routers.social_login import router as social_login_router
from app.routers.passwords import router as passwords_router
from app.routers.social_user import router as social_user_router
from app.routers.public import router as public_router

app.include_router(auth_router)
app.include_router(clients_router , dependencies=[Depends(get_api_key)])
app.include_router(users_router , dependencies=[Depends(get_api_key)])
app.include_router(user_info_router)
app.include_router(signup_router)
app.include_router(social_login_router)
app.include_router(passwords_router, prefix="/password/reset")
app.include_router(social_user_router)
app.include_router(public_router)

@app.get("/.well-known/openid-configuration")
async def configuration():
    prefix = settings.EXTERNAL_DOMAIN+(settings.ROOT_PATH if settings.ROOT_PATH else "")
    return {
        "issuer": f"{prefix}",
        "authorization_endpoint": f"{prefix}/signin",
        "token_endpoint": f"{prefix}/token",
        "userinfo_endpoint": f"{prefix}/userinfo",
        # 'revocation_endpoint': f"{settings.EXTERNAL_HOST}/revoke",
        'response_modes_supported': ['query', 'fragment', 'form_post'],
        'grant_types_supported': ['authorization_code'],
        'algorithms_supported': ['EdDSA'],
        'subject_types_supported': ['public'],
        'response_types_supported': ['code'],
        'google_authorization_endpoint': f"{prefix}/signin/google",
        'github_authorization_endpoint': f"{prefix}/signin/github",
        'apple_authorization_endpoint': f"{prefix}/signin/apple",
    }

@app.get("/health", tags=["Health"])
async def health():
    return Response(status_code=200 , content="OK")

if __name__ == "__main__":
    import uvicorn
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-p',"--port", type=int, default=4000)
    parser.add_argument("--reload", type=bool, default=True)
    args = parser.parse_args()
    uvicorn.run('app.main:app', host='0.0.0.0', port=args.port , reload=args.reload)