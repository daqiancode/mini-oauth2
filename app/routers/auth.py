from fastapi import APIRouter, Depends, Request,Form,Query,HTTPException
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import Annotated
from app.utils.urls import set_url_params
from app.services.users import Users
from app.utils.jwts import create_access_token
from app.config import settings
from app.routers.forms import SigninRequest, redis_prefix, ResponseType, GrantType, set_code,get_code,delete_code,put_invalid_jti,get_invalid_jti
from app.services.clients import Clients
from app.utils.urls import encode_url_params, check_url_in_domains
from app.routers.dependencies import jwt_bearer, get_jwt_payload, templates
from datetime import datetime, timezone
from app.services.client_users import ClientUsers
import logging
log = logging.getLogger(__name__)
router = APIRouter(tags=["OAuth2"])




@router.get("/signin" , description="Signin page")
async def signin(request: Request, query: Annotated[SigninRequest, Query()]):
    #check client_id , response_type , redirect_uri , scope
    client = await Clients().get(query.client_id)
    if not client:
        raise HTTPException(status_code=400, detail="client not found")
    if client.disabled:
        raise HTTPException(status_code=400, detail="client disabled")
    if query.response_type != ResponseType.code:
        raise HTTPException(status_code=400, detail="response_type not supported")
    if not check_url_in_domains(query.redirect_uri, client.allowed_domains):
        raise HTTPException(status_code=400, detail="redirect_uri not allowed")
    # render signin page
    return templates.TemplateResponse("signin.html", {'request': request,'query': encode_url_params(query.model_dump()), 'client': client})

class SigninPostRequest(BaseModel):
    email: str
    password: str
    mfa: str|None = None


@router.post("/signin" , description="Signin page")
async def signin_post(form: Annotated[SigninPostRequest, Form()], query: Annotated[SigninRequest, Query()], request: Request):
    # check username, password, MFA
    client = await Clients().get(query.client_id)
    try:
        user_id = await Users().signin(form.email, form.password, query.client_id)
    except Exception as e:
        return templates.TemplateResponse("signin.html", {'request': request,'query': encode_url_params(query.model_dump()) , 'error': str(e) , 'client': client})
    user = await Users().get(user_id)
    if user.disabled:
        return templates.TemplateResponse("signin.html", {'request': request,'query': encode_url_params(query.model_dump()) , 'error': 'User disabled' , 'client': client})
    code = await set_code(query.model_dump(), user_id)
    # expire 10 minutes

    # issue code to redis
    # redirect to redirect_uri with code
    return RedirectResponse(set_url_params(query.redirect_uri, {"code": code,'state':query.state} , remove_none=False))

class TokenRequest(BaseModel):
    grant_type: GrantType
    code: str
    redirect_uri: str
    client_id: str
    client_secret: str

@router.post("/token" , description="fetch token with code")
async def token(form: Annotated[TokenRequest, Form()]):
    # check code is valid from redis
    # get client & check
    code_value = await get_code(form.code)
    await delete_code(form.code)
    if not code_value:
        raise HTTPException(status_code=400, detail="code not found")
    # check redirect_uri is match
    if code_value['context']['redirect_uri'] != form.redirect_uri:
        raise HTTPException(status_code=400, detail="redirect_uri not match")
    # user = await Users().get(code_value['user_id'])
    client = await Clients().get(form.client_id)
    user_id = code_value['user_id']
    user = await ClientUsers().get_user_info(user_id, form.client_id)
    if not user:
        raise HTTPException(status_code=400, detail="user not found")
    if user.disabled:
        raise HTTPException(status_code=400, detail="user disabled")
    access_token = create_access_token(client.jwt_private_key, user_id, form.client_id, user.roles ,settings.JWT_EXPIRES_IN_HOURS)
    # issue jwt token
    return {"access_token": access_token, 'expires_in': settings.JWT_EXPIRES_IN_HOURS * 60}


# @router.options("/token")
# def token_options(request: Request):
#     # CORS allowd Access-Control-Allow-Origin
#     response = Response(headers={"Access-Control-Allow-Origin": "*"})
#     response.headers["Access-Control-Allow-Methods"] = "POST"
#     response.headers["Access-Control-Allow-Headers"] = "Content-Type"
#     return response


@router.post("/signout" , description="signout")
async def signout(jwt_payload: dict = Depends(get_jwt_payload)):
    # delete jwt token
    try:
        jti = jwt_payload['jti']
        expires_in = int(jwt_payload['exp'] - datetime.now(timezone.utc).timestamp())
        if expires_in < 0:
            expires_in = 0
            return {"message": "signout success"}
        await put_invalid_jti(jti, expires_in)
    except Exception as e:
        raise HTTPException(status_code=401, detail="invalid token")
    return {"message": "signout success"}


@router.get("/validate" , description="validate token")
async def validate(jwt_payload: dict = Depends(get_jwt_payload)):
    try:
        jti = jwt_payload['jti']
        client_id = jwt_payload['aud']
        if await get_invalid_jti(jti):
            return {"valid": False}
        return {"valid": True}
    except Exception as e:
        raise HTTPException(status_code=401, detail="invalid token")