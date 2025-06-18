from fastapi import APIRouter, Depends, Request, Form, Query, HTTPException
from fastapi.responses import RedirectResponse
from typing import Annotated
from app.utils.urls import set_url_params, replace_url_host
from app.services.users import Users
from app.config import env
from app.routers.forms import SigninRequest, redis_prefix, set_state, set_code, get_state, delete_state
import os
from app.services.oauth_client import GoogleOAuthClient, GithubOAuthClient, AppleOAuthClient, WechatOAuthClient, LinkedinOAuthClient
from app.models.models import UserSource
import logging
log = logging.getLogger(__name__)

router = APIRouter(tags=["Social Signin"])

@router.get("/signin/google")
async def signin_via_google(request: Request, qs: Annotated[SigninRequest, Query()]):
    log.info("signin google: %s", qs.model_dump())
    redirect_uri = request.url_for('callback_via_google')
    redirect_uri = replace_url_host(str(redirect_uri), env.EXTERNAL_DOMAIN)
    log.info("/signin/google - redirect_uri: %s", redirect_uri)
    state = await set_state(qs.model_dump())
    google_oauth = GoogleOAuthClient(env.GOOGLE_CLIENT_ID, env.GOOGLE_CLIENT_SECRET)
    log.info("/signin/google - google_oauth.get_authorize_url: %s", google_oauth.get_authorize_url(redirect_uri, state))
    return RedirectResponse(google_oauth.get_authorize_url(redirect_uri, state))

@router.get("/callback/google")
async def callback_via_google(request: Request):
    log.info("callback google: %s", request.query_params)
    state = request.query_params.get('state')
    context = await get_state(state)
    await delete_state(state)
    google_oauth = GoogleOAuthClient(env.GOOGLE_CLIENT_ID, env.GOOGLE_CLIENT_SECRET)
    redirect_uri = request.url_for('callback_via_google')
    redirect_uri = replace_url_host(str(redirect_uri), env.EXTERNAL_DOMAIN)
    token = await google_oauth.get_access_token(request.query_params.get('code'), redirect_uri)
    user = await google_oauth.get_userinfo(token['access_token'])
    user_id = await Users().save_or_update(user['name'], user['picture'], email=user['email'], source=UserSource.google)
    code = await set_code(context, user_id)
    return RedirectResponse(set_url_params(context['redirect_uri'], {"code": code, 'state': context['state']}))

# Similar changes for other social login providers (Github, Apple, Wechat)
# Each endpoint needs to be made async and await the async operations

@router.get("/signin/github")
async def signin_via_github(request: Request, qs: Annotated[SigninRequest, Query()]):
    log.info("signin github: %s", qs.model_dump())
    redirect_uri = request.url_for('callback_via_github')
    redirect_uri = replace_url_host(str(redirect_uri), env.EXTERNAL_DOMAIN)
    state = await set_state(qs.model_dump())
    github_oauth = GithubOAuthClient(env.GITHUB_CLIENT_ID, env.GITHUB_CLIENT_SECRET)
    return RedirectResponse(github_oauth.get_authorize_url(redirect_uri, state))

@router.get("/callback/github")
async def callback_via_github(request: Request):
    log.info("callback github: %s", request.query_params)
    state = request.query_params.get('state')
    context = await get_state(state)
    await delete_state(state)
    github_oauth = GithubOAuthClient(env.GITHUB_CLIENT_ID, env.GITHUB_CLIENT_SECRET)
    redirect_uri = request.url_for('callback_via_github')
    redirect_uri = replace_url_host(str(redirect_uri), env.EXTERNAL_DOMAIN)
    token = await github_oauth.get_access_token(request.query_params.get('code'), redirect_uri)
    user = await github_oauth.get_userinfo(token['access_token'])
    log.info("github user: %s", user)
    user_id = await Users().save_or_update(user['name'], user['avatar_url'], email=user['email'], source=UserSource.github)
    code = await set_code(context, user_id)
    return RedirectResponse(set_url_params(context['redirect_uri'], {"code": code, 'state': context['state']}))

@router.get("/signin/apple")
async def signin_via_apple(request: Request, qs: Annotated[SigninRequest, Query()]):
    log.info("signin apple: %s", qs.model_dump())
    redirect_uri = request.url_for('callback_via_apple')
    redirect_uri = replace_url_host(str(redirect_uri), env.EXTERNAL_DOMAIN)
    state = await set_state(qs.model_dump())
    apple_oauth = AppleOAuthClient(env.APPLE_CLIENT_ID, env.APPLE_CLIENT_SECRET)
    return RedirectResponse(apple_oauth.get_authorize_url(redirect_uri, state))

@router.post("/callback/apple")
async def callback_via_apple(request: Request):
    log.info("callback apple: %s", request.form)
    code = request.form.get('code')
    state = request.form.get('state')
    id_token = request.form.get('id_token')
    context = await get_state(state)    
    await delete_state(state)
    apple_oauth = AppleOAuthClient(env.APPLE_CLIENT_ID, env.APPLE_CLIENT_SECRET)
    redirect_uri = request.url_for('callback_via_apple')
    redirect_uri = replace_url_host(str(redirect_uri), env.EXTERNAL_DOMAIN)
    token = await apple_oauth.get_access_token(request.query_params.get('code'), redirect_uri)
    user = await apple_oauth.get_userinfo(token['access_token'])
    user_id = await Users().save_or_update(user['name'], user['picture'], email=user['email'], source=UserSource.apple)
    code = await set_code(context, user_id)
    return RedirectResponse(set_url_params(context['redirect_uri'], {"code": code, 'state': context['state']}))

@router.get("/signin/linkedin")
async def signin_via_linkedin(request: Request, qs: Annotated[SigninRequest, Query()]):
    log.info("signin linkedin: %s", qs.model_dump())
    redirect_uri = request.url_for('callback_via_linkedin')
    redirect_uri = replace_url_host(str(redirect_uri), env.EXTERNAL_DOMAIN)
    state = await set_state(qs.model_dump())
    linkedin_oauth = LinkedinOAuthClient(env.LINKEDIN_CLIENT_ID, env.LINKEDIN_CLIENT_SECRET)
    return RedirectResponse(linkedin_oauth.get_authorize_url(redirect_uri, state))

@router.get("/callback/linkedin")
async def callback_via_linkedin(request: Request):
    log.info("callback linkedin: %s", request.query_params)
    state = request.query_params.get('state')
    context = await get_state(state)
    await delete_state(state)
    linkedin_oauth = LinkedinOAuthClient(env.LINKEDIN_CLIENT_ID, env.LINKEDIN_CLIENT_SECRET)
    redirect_uri = request.url_for('callback_via_linkedin')
    redirect_uri = replace_url_host(str(redirect_uri), env.EXTERNAL_DOMAIN)
    token = await linkedin_oauth.get_access_token(request.query_params.get('code'), redirect_uri)
    user = await linkedin_oauth.get_userinfo(token['access_token'])
    user_id = await Users().save_or_update(user['name'], user['picture'], email=user['email'], source=UserSource.linkedin)
    code = await set_code(context, user_id)
    return RedirectResponse(set_url_params(context['redirect_uri'], {"code": code, 'state': context['state']}))

    
@router.get("/signin/wechat")
async def signin_via_wechat(request: Request, qs: Annotated[SigninRequest, Query()]):
    log.info("signin wechat: %s", qs.model_dump())
    redirect_uri = request.url_for('callback_via_wechat')
    redirect_uri = replace_url_host(str(redirect_uri), env.EXTERNAL_DOMAIN)
    state = await set_state(qs.model_dump())
    wechat_oauth = WechatOAuthClient(env.WECHAT_APPID, env.WECHAT_APPSECRET)
    return RedirectResponse(wechat_oauth.get_authorize_url(redirect_uri, state))

@router.get("/callback/wechat")
async def callback_via_wechat(request: Request):
    log.info("callback wechat: %s", request.query_params)
    state = request.query_params.get('state')
    context = await get_state(state)
    await delete_state(state)
    wechat_oauth = WechatOAuthClient(env.WECHAT_APPID, env.WECHAT_APPSECRET)
    redirect_uri = request.url_for('callback_via_wechat')
    redirect_uri = replace_url_host(str(redirect_uri), env.EXTERNAL_DOMAIN)
    log.info("wechat redirect_uri: %s", redirect_uri)
    token = await wechat_oauth.get_access_token(request.query_params.get('code'), redirect_uri)
    log.info("wechat token: %s", token)
    user = await wechat_oauth.get_userinfo(token['access_token'], request.query_params.get('openid'))
    log.info("wechat user: %s", user)
    user_id = await Users().save_or_update(user['nickname'], user['headimgurl'], openid=user['openid'], source=UserSource.wechat)
    code = await set_code(context, user_id)
    return RedirectResponse(set_url_params(context['redirect_uri'], {"code": code, 'state': context['state']}))