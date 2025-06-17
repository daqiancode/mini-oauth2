from fastapi import APIRouter
from fastapi.security import OAuth2AuthorizationCodeBearer
from app.config import settings
from typing import Annotated
from fastapi import Depends, HTTPException
from app.services.users import Users
from jwt.exceptions import InvalidTokenError
from app.utils.jwts import verify_jwt_eddsa
import logging
from pydantic import BaseModel
log = logging.getLogger(__name__)

router = APIRouter(tags=["User Info"])

bearer = OAuth2AuthorizationCodeBearer(authorizationUrl=f"{settings.EXTERNAL_DOMAIN}/signin", tokenUrl=f"{settings.EXTERNAL_DOMAIN}/token")

async def get_user_id(token = Depends(bearer)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_jwt_eddsa(token, settings.JWT_PUBLIC_KEY)
        return int(payload['sub'])
    except InvalidTokenError as e:
        log.error(e)
        raise credentials_exception

@router.get("/userinfo", description="Get user info")
async def userinfo(user_id = Depends(get_user_id)):
    user = await Users().get(user_id)
    if user:
        return user
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")

class UserPut(BaseModel):
    name: str|None = None
    avatar: str|None = None

@router.put("/userinfo", description="Modify user info")
async def modify_userinfo(user_id = Depends(get_user_id), user: UserPut = Depends(UserPut)):
    await Users().update(user_id, user.name, user.email, user.roles)
    return {"result": "OK"}

class UserPasswordPut(BaseModel):
    old_password: str
    password: str

@router.put("/userinfo/password", description="Modify user password")
async def modify_userinfo_password(user_id = Depends(get_user_id), password: UserPasswordPut = Depends(UserPasswordPut)):
    await Users().update_password_with_old_password(user_id, password.old_password, password.password)
    return {"result": "OK"}


# @router.delete("/userinfo", description="Delete user")
# async def delete_userinfo(user_id = Depends(get_user_id)):
#     await Users().delete(user_id)
#     return {"result": "OK"}