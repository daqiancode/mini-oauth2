from fastapi import APIRouter, Depends, Request, Form, Query, HTTPException
from app.services.users import Users
from app.config import env
from app.services.oauth_client import GoogleOAuthClient, GithubOAuthClient, AppleOAuthClient, WechatOAuthClient, LinkedinOAuthClient
import logging
from pydantic import BaseModel
from app.utils.jwts import create_access_token
log = logging.getLogger(__name__)


router = APIRouter(tags=["Social Mobile"])


class SocialIdTokenRequest(BaseModel):
    access_token: str
    provider: str # google, apple, facebook, twitter, github, linkedin, wechat, qq, weibo, alipay

@router.post("/social/user", description="Login with social access_token")
async def social_id_token(request: Request , form: SocialIdTokenRequest = Depends(SocialIdTokenRequest)):
    if request.provider == "google":
        user = await GoogleOAuthClient(env.GOOGLE_CLIENT_ID, env.GOOGLE_CLIENT_SECRET).get_userinfo(request.id_token)
    elif request.provider == "apple":
        user = await AppleOAuthClient().get_userinfo(request.id_token)
    elif request.provider == "github":
        user = await GithubOAuthClient(env.GITHUB_CLIENT_ID, env.GITHUB_CLIENT_SECRET).get_userinfo(request.id_token)
    elif request.provider == "linkedin":
        user = await LinkedinOAuthClient(env.LINKEDIN_CLIENT_ID, env.LINKEDIN_CLIENT_SECRET).get_userinfo(request.id_token)
    elif request.provider == "wechat":
        user = await WechatOAuthClient(env.WECHAT_CLIENT_ID, env.WECHAT_CLIENT_SECRET).get_userinfo(request.id_token)
    else:
        raise HTTPException(status_code=400, detail="Invalid provider")
    
    # save user to database
    user = await Users().save_or_update(user.get("name"), user.get("avatar"), user.get("email"), user.get("openid"), user.get("source"))
    jwt = create_access_token(env.JWT_PRIVATE_KEY, user.id, user.roles, env.JWT_EXPIRES_IN_HOURS * 60)
    return {"access_token": jwt , "expires_in": env.JWT_EXPIRES_IN_HOURS * 60}