from fastapi import APIRouter, Depends, Request,Form,Query,HTTPException
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import Annotated
from app.utils.urls import set_url_params
from app.services.users import Users
from app.utils.jwts import create_access_token
from app.config import settings
from app.routers.forms import SigninRequest, redis_prefix, ResponseType, GrantType, set_code,get_code,delete_code
from app.services.clients import Clients
from app.utils.urls import encode_url_params, check_url_in_domains
import logging
log = logging.getLogger(__name__)
router = APIRouter(tags=["Auth"])


templates = Jinja2Templates(directory="views")


@router.get("/signin" , description="Signin page")
async def signin(request: Request, query: Annotated[SigninRequest, Query()]):
    #check client_id , response_type , redirect_uri , scope
    client = await Clients().get_client_by_id(query.client_id)
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
    try:
        user_id = await Users().signin(form.email, form.password)
    except Exception as e:
        return templates.TemplateResponse("signin.html", {'request': request,'query': encode_url_params(query.model_dump()) , 'error': str(e)})
    user = await Users().get(user_id)
    if user.disabled:
        return templates.TemplateResponse("signin.html", {'request': request,'query': encode_url_params(query.model_dump()) , 'error': 'User disabled'})
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
    user = await Users().get(code_value['user_id'])
    if not user:
        raise HTTPException(status_code=400, detail="user not found")
    if user.disabled:
        raise HTTPException(status_code=400, detail="user disabled")
    access_token = create_access_token(settings.JWT_PRIVATE_KEY, user.id, user.roles ,settings.JWT_EXPIRES_IN_HOURS * 60)
    # issue jwt token
    return {"access_token": access_token, 'expires_in': settings.JWT_EXPIRES_IN_HOURS * 60}


# @router.options("/token")
# def token_options(request: Request):
#     # CORS allowd Access-Control-Allow-Origin
#     response = Response(headers={"Access-Control-Allow-Origin": "*"})
#     response.headers["Access-Control-Allow-Methods"] = "POST"
#     response.headers["Access-Control-Allow-Headers"] = "Content-Type"
#     return response
