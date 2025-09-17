from fastapi import APIRouter, Depends, Request,Form,Query,HTTPException
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import Annotated
from app.utils.urls import set_url_params
from app.services.users import Users
from app.utils.jwts import create_access_token
from app.config import env, settings
from app.routers.forms import SigninRequest, redis_prefix, ResponseType, GrantType, set_code,get_code,delete_code,put_invalid_jti,get_invalid_jti
from app.services.clients import Clients
from app.utils.urls import encode_url_params, check_url_in_domains
from app.routers.dependencies import jwt_bearer, get_jwt_payload, templates , check_client
from datetime import datetime, timezone
from app.services.client_users import ClientUsers, ClientUserPost
from app.utils.urls import replace_url_host
from app.routers.forms import set_state, get_state, delete_state
from app.services.providers import providers
import logging
log = logging.getLogger(__name__)
router = APIRouter(tags=["OAuth2"])




@router.get("/signin" , description="Signin page")
async def signin(request: Request, query: Annotated[SigninRequest, Query()]):
    #check client_id , response_type , redirect_uri , scope
    client = await check_client(query.client_id, query.redirect_uri)
    if query.response_type != ResponseType.code:
        raise HTTPException(status_code=400, detail="response_type not supported")

    if query.provider:
        if not providers.check_provider(query.provider):
            raise HTTPException(status_code=400, detail="provider not allowed")
        redirect_uri = request.url_for('callback')
        redirect_uri = replace_url_host(str(redirect_uri), env.EXTERNAL_DOMAIN)
        log.info("/signin - redirect_uri: %s", redirect_uri)
        state = await set_state({ **request.query_params })
        provider = providers.get_provider(query.provider)
        log.info("/signin - get_authorize_url: %s", provider.get_authorize_url(redirect_uri, state))
        return RedirectResponse(provider.get_authorize_url(redirect_uri, state))

    
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
        return templates.TemplateResponse("signin.html", {'request': request,'query': encode_url_params({ **request.query_params }) , 'error': str(e) , 'client': client})
    user = await Users().get(user_id)
    if user.disabled:
        return templates.TemplateResponse("signin.html", {'request': request,'query': encode_url_params({ **request.query_params }) , 'error': 'User disabled' , 'client': client})
    code = await set_code({ **request.query_params }, user_id, client.jwt_expires_in_hours)
    # expire 10 minutes

    # issue code to redis
    # redirect to redirect_uri with code
    return RedirectResponse(set_url_params(query.redirect_uri, {"code": code,'state':query.state} , remove_none=False))

@router.get("/callback")
async def callback(request: Request):
    state = request.query_params.get('state')
    context = await get_state(state)
    log.info("callback context: %s", context)
    if not context:
        raise HTTPException(status_code=400, detail="state not found")
    await delete_state(state)
    provider = providers.get_provider(context['provider'])
    if not provider:
        raise HTTPException(status_code=400, detail="provider not found")
    redirect_uri = request.url_for('callback')
    redirect_uri = replace_url_host(str(redirect_uri), env.EXTERNAL_DOMAIN)
    token = await provider.get_access_token(request.query_params.get('code'), redirect_uri)
    user = await provider.get_userinfo(token['access_token'])
    # user_id = await Users().save_or_update(user['name'], user['picture'], email=user['email'], provider=context['provider'])
    client_user = await ClientUsers().save_or_update(ClientUserPost(client_id=context['client_id'], email=user.get('email'), mobile=user.get('mobile'), openid=user.get('openid'), name=user.get('name'), avatar=user.get('picture'), provider=context['provider']))
    client = await Clients().get(context['client_id'])
    code = await set_code(context, client_user.user_id, client.jwt_expires_in_hours)
    return RedirectResponse(set_url_params(context['redirect_uri'], {"code": code, 'state': context['state']}))


class TokenRequest(BaseModel):
    grant_type: GrantType
    code: str
    redirect_uri: str
    client_id: str
    client_secret: str|None = None

@router.post("/token" , description="fetch token with code")
async def token(form: Annotated[TokenRequest, Form()]):
    # check code is valid from redis
    # get client & check

    if form.grant_type != GrantType.authorization_code:
        raise HTTPException(status_code=400, detail="grant_type not supported")
    code_value = await get_code(form.code)
    # await delete_code(form.code)
    if not code_value:
        raise HTTPException(status_code=400, detail="code not found")
    # check redirect_uri is match
    if code_value['context']['redirect_uri'] != form.redirect_uri:
        raise HTTPException(status_code=400, detail="redirect_uri not match")
    # user = await Users().get(code_value['user_id'])
    # client = await Clients().get(form.client_id)
    user_id = code_value['user_id']
    return await _issue_token(user_id, form.client_id, client_secret=form.client_secret, need_check_client=True)
    # user = await ClientUsers().get_user_info(user_id, form.client_id)
    # if not user:
    #     raise HTTPException(status_code=400, detail="user not found")
    # if user.get('disabled'):
    #     raise HTTPException(status_code=400, detail="user disabled")
    # access_token = create_access_token(client.jwt_private_key, user_id, form.client_id, user.get('roles') ,settings.JWT_EXPIRES_IN_HOURS)
    # # issue jwt token
    # return {"access_token": access_token, 'expires_in': settings.JWT_EXPIRES_IN_HOURS * 60 * 60, "token_type": "Bearer"}


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


@router.get("/introspect" , description="OIDC introspect")
async def validate(jwt_payload: dict = Depends(get_jwt_payload)):
    try:
        jti = jwt_payload['jti']
        client_id = jwt_payload['aud']
        if await get_invalid_jti(jti):
            return {"active": False}
        client = await Clients().get(client_id)
        if not client or client.disabled:
            return {"active": False}
        jwt_payload['active'] = True
        return jwt_payload
    except Exception as e:
        raise HTTPException(status_code=401, detail="invalid token")


class ExchangeRequest(BaseModel):
    client_id: str
    access_token: str
    provider: str
@router.post("/exchange")
async def exchange(request: Request, form: Annotated[ExchangeRequest, Form()]):
    # exchange google, apple, github, linkedin, wechat token to jwt token
    log.info("exchange: %s", form)
    access_token = form.access_token
    user = await providers.get_provider(form.provider).get_userinfo(access_token)
    client_user = await ClientUsers().save_or_update(ClientUserPost(client_id=form.client_id, email=user.get('email'), mobile=user.get('mobile'), openid=user.get('openid'), name=user.get('name'), avatar=user.get('picture'), provider=form.provider))
    # google_oauth = providers.get_provider(form.provider)
    # user = await google_oauth.get_userinfo(access_token)
    # user_id = await Users().save_or_update(user.get('name'), user.get('picture'), email=user.get('email'), provider=form.provider)
    return await _issue_token(client_user.user_id, form.client_id, None, need_check_client=False)


async def _issue_token(user_id: str, client_id: str,client_secret: str|None = None , need_check_client: bool = True) -> dict:
    client = await Clients().get(client_id)
    if need_check_client:
        if not client:
            raise HTTPException(status_code=400, detail="client not found")
        if client.client_secret != client_secret:
            raise HTTPException(status_code=400, detail="client secret not match")
    user = await ClientUsers().get_user_info(user_id, client_id)
    if user.get('disabled'):
        raise HTTPException(status_code=400, detail="user disabled")
    access_token = create_access_token(client.jwt_private_key, user_id, client_id, user.get('roles') ,client.jwt_expires_in_hours ,client.jwt_algorithm)
    return {"access_token": access_token, 'expires_in': client.jwt_expires_in_hours * 60 * 60, "token_type": "Bearer"}

from jwcrypto import jwk

@router.get("/jwks" , description="jwks")
async def jwks():
    clients = await Clients().list(disabled=False)
    keys = []
    for client in clients:
        if client.jwt_algorithm.startswith("HS"):
            continue
        key = jwk.JWK.from_pem(client.jwt_public_key.encode('utf-8'))
        public_jwk = key.export_public(as_dict=True)
        public_jwk['kid'] = client.id
        # public_jwk['public_key'] = client.jwt_public_key
        keys.append(public_jwk)
    return {"keys": keys}

