from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
from app.utils.jwts import verify_jwt_eddsa
from app.config import settings
from jwt.exceptions import InvalidTokenError
import logging


log = logging.getLogger(__name__)


jwt_bearer = HTTPBearer(auto_error=True)


def get_jwt_payload(credentials: HTTPAuthorizationCredentials = Depends(jwt_bearer))->dict:
    jwt_token = credentials.credentials
    try:
        jwt_payload = verify_jwt_eddsa(jwt_token, settings.JWT_PUBLIC_KEY)
        return jwt_payload
    except InvalidTokenError as e:
        log.error(e)
        raise HTTPException(status_code=401, detail="invalid token")
        
def get_user_id(credentials: HTTPAuthorizationCredentials = Depends(jwt_bearer))->int:
    jwt_payload = get_jwt_payload(credentials)
    if jwt_payload:
        return int(jwt_payload['sub'])
    else:
        raise HTTPException(status_code=401, detail="invalid token")