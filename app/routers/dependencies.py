from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
from app.utils.jwts import verify_jwt
from app.config import settings
from jwt.exceptions import InvalidTokenError
import logging
from fastapi.templating import Jinja2Templates
from app.models.models import Client
from app.services.clients import Clients


log = logging.getLogger(__name__)

templates = Jinja2Templates(directory="views")



jwt_bearer = HTTPBearer(auto_error=True)


def get_jwt_payload(credentials: HTTPAuthorizationCredentials = Depends(jwt_bearer))->dict:
    jwt_token = credentials.credentials
    try:
        jwt_payload = verify_jwt(jwt_token, settings.JWT_PUBLIC_KEY)
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
    

def get_client_id(credentials: HTTPAuthorizationCredentials = Depends(jwt_bearer))->str:
    jwt_payload = get_jwt_payload(credentials)
    if jwt_payload:
        return jwt_payload['aud']
    else:
        raise HTTPException(status_code=401, detail="invalid token")


async def check_client(client_id: str , redirect_uri: str=None)->Client:
    client = await Clients().get(client_id)
    if not client:
        raise HTTPException(status_code=400, detail="client not found")
    if client.disabled:
        raise HTTPException(status_code=400, detail="client disabled")
    if redirect_uri and not client.allowed_uris or redirect_uri not in client.allowed_uris:
        raise HTTPException(status_code=400, detail="redirect_uri not allowed")
    return client