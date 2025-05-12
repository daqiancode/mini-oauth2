from fastapi import APIRouter, Depends, Request,Form,Query,HTTPException
from fastapi.responses import RedirectResponse
from typing import Annotated
from app.utils.urls import set_url_params, replace_url_host
from app.services.users import Users
from app.config import settings
from app.routers.forms import SigninRequest, redis_prefix, set_state, set_code, get_state, delete_state
import os
from app.services.oauth_client import GoogleOAuthClient, GithubOAuthClient, AppleOAuthClient, WechatOAuthClient
from app.models.models import UserSource
import logging
log = logging.getLogger(__name__)
from app.models.models import UserSource

router = APIRouter(tags=["Social Signin"])

# Google Signin
@router.get("/signin/google")
async def signin_via_google(request: Request ,qs: Annotated[SigninRequest, Query()]):
    log.info("signin google: %s", qs.model_dump())
    redirect_uri = request.url_for('callback_via_google')
    redirect_uri = replace_url_host(str(redirect_uri), settings.EXTERNAL_HOST)
    state = set_state(qs.model_dump())
    # return await oauth.google.authorize_redirect(request, redirect_uri , state=state)
    google_oauth = GoogleOAuthClient(os.getenv('GOOGLE_CLIENT_ID'), os.getenv('GOOGLE_CLIENT_SECRET'))
    return RedirectResponse(google_oauth.get_authorize_url(redirect_uri, state))

@router.get("/callback/google")
async def callback_via_google(request: Request):
    log.info("callback google: %s", request.query_params)
    state = request.query_params.get('state')
    context = get_state(state)
    delete_state(state)
    # token = await oauth.google.authorize_access_token(request)
    google_oauth = GoogleOAuthClient(os.getenv('GOOGLE_CLIENT_ID'), os.getenv('GOOGLE_CLIENT_SECRET'))
    redirect_uri = request.url_for('callback_via_google')
    redirect_uri = replace_url_host(str(redirect_uri), settings.EXTERNAL_HOST)
    token = await google_oauth.get_access_token(request.query_params.get('code'), redirect_uri)
    user = await google_oauth.get_userinfo(token['access_token'])
    user_id = Users().save_or_update(user['name'] , user['picture'] , email=user['email'] , source=UserSource.google)
    code = set_code(context, user_id)
    return RedirectResponse(set_url_params(context['redirect_uri'], {"code": code,'state':context['state']}))


# Github Signin
@router.get("/signin/github")
async def signin_via_github(request: Request ,qs: Annotated[SigninRequest, Query()]):
    log.info("signin github: %s", qs.model_dump())
    redirect_uri = request.url_for('callback_via_github')
    redirect_uri = replace_url_host(str(redirect_uri), settings.EXTERNAL_HOST)
    state = set_state(qs.model_dump())
    github_oauth = GithubOAuthClient(os.getenv('GITHUB_CLIENT_ID'), os.getenv('GITHUB_CLIENT_SECRET'))
    return RedirectResponse(github_oauth.get_authorize_url(redirect_uri, state))

@router.get("/callback/github")
async def callback_via_github(request: Request):
    log.info("callback github: %s", request.query_params)
    state = request.query_params.get('state')
    context = get_state(state)
    delete_state(state)
    github_oauth = GithubOAuthClient(os.getenv('GITHUB_CLIENT_ID'), os.getenv('GITHUB_CLIENT_SECRET'))
    redirect_uri = request.url_for('callback_via_github')
    redirect_uri = replace_url_host(str(redirect_uri), settings.EXTERNAL_HOST)
    token = await github_oauth.get_access_token(request.query_params.get('code'), redirect_uri)
    user = await github_oauth.get_userinfo(token['access_token'])
    user_id = Users().save_or_update(user['name'] , user['avatar_url'] , email=user['email'] , source=UserSource.github)
    
    code = set_code(context, user_id)
    return RedirectResponse(set_url_params(context['redirect_uri'], {"code": code,'state':context['state']}))


# Apple Signin

@router.get("/signin/apple")
async def signin_via_apple(request: Request ,qs: Annotated[SigninRequest, Query()]):
    log.info("signin apple: %s", qs.model_dump())
    redirect_uri = request.url_for('callback_via_apple')
    redirect_uri = replace_url_host(str(redirect_uri), settings.EXTERNAL_HOST)
    state = set_state(qs.model_dump())
    apple_oauth = AppleOAuthClient(os.getenv('APPLE_CLIENT_ID'), os.getenv('APPLE_CLIENT_SECRET'))
    return RedirectResponse(apple_oauth.get_authorize_url(redirect_uri, state))

@router.get("/callback/apple")
async def callback_via_apple(request: Request):
    log.info("callback apple: %s", request.query_params)
    state = request.query_params.get('state')
    context = get_state(state)
    delete_state(state)
    apple_oauth = AppleOAuthClient(os.getenv('APPLE_CLIENT_ID'), os.getenv('APPLE_CLIENT_SECRET'))
    redirect_uri = request.url_for('callback_via_apple')
    redirect_uri = replace_url_host(str(redirect_uri), settings.EXTERNAL_HOST)
    token = await apple_oauth.get_access_token(request.query_params.get('code'), redirect_uri)
    user = await apple_oauth.get_userinfo(token['access_token'])
    # save user 
    user_id = Users().save_or_update(user['name'] , user['picture'] , email=user['email'] , source=UserSource.apple)
    
    code = set_code(context, user_id)
    return RedirectResponse(set_url_params(context['redirect_uri'], {"code": code,'state':context['state']}))


# Wechat Qrcode Signin
@router.get("/callback/wechat")
async def callback_via_wechat(request: Request):
    log.info("callback wechat: %s", request.query_params)
    state = request.query_params.get('state')
    context = get_state(state)
    delete_state(state)
    wechat_oauth = WechatOAuthClient(os.getenv("WECHAT_APPID"), os.getenv("WECHAT_APPSECRET"))
    redirect_uri = request.url_for('callback_via_wechat')
    redirect_uri = replace_url_host(str(redirect_uri), settings.EXTERNAL_HOST)
    token = await wechat_oauth.get_access_token(request.query_params.get('code'), redirect_uri)
    user = await wechat_oauth.get_userinfo(token['access_token'])
    # save user 
    user_id = Users().save_or_update(user['name'] , user['picture'] , openid=user['openid'] , source=UserSource.wechat)
    
    code = set_code(context, user_id)
    return RedirectResponse(set_url_params(context['redirect_uri'], {"code": code,'state':context['state']}))

@router.get("/signin/wechat")
async def signin_via_wechat_qrcode(request: Request,qs: Annotated[SigninRequest, Query()]):
    log.info("signin wechat qrcode")
    # Generate QR code for the login URL
    state = set_state(qs.model_dump())
    redirect_uri = request.url_for('callback_via_wechat')
    redirect_uri = replace_url_host(str(redirect_uri), settings.EXTERNAL_HOST)
    wechat_oauth = WechatOAuthClient(os.getenv("WECHAT_APPID"), os.getenv("WECHAT_APPSECRET"))
    return RedirectResponse(wechat_oauth.get_authorize_url(redirect_uri, state))
