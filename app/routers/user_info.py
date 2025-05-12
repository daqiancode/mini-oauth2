from fastapi import APIRouter
from fastapi.security import OAuth2AuthorizationCodeBearer
from app.config import settings
from typing import Annotated
from fastapi import Depends, HTTPException
from app.services.users import Users
from jwt.exceptions import InvalidTokenError
from app.utils.jwts import verify_jwt_eddsa
import logging
log = logging.getLogger(__name__)

router = APIRouter(tags=["User Info"])

bearer = OAuth2AuthorizationCodeBearer(authorizationUrl=f"{settings.EXTERNAL_HOST}/signin", tokenUrl=f"{settings.EXTERNAL_HOST}/token")

async def get_user_id(token = Depends(bearer)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_jwt_eddsa(token, settings.JWT_PUBLIC_KEY)
        return payload['sub']
    except InvalidTokenError as e:
        log.error(e)
        raise credentials_exception


@router.get("/userinfo" , description="Get user info")
def userinfo(user_id = Depends(get_user_id)):
    user = Users().get(user_id)
    if user:
        return user._asdict()
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")

