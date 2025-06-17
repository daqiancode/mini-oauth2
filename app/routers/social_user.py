from fastapi import APIRouter, Depends, Request, Form, Query, HTTPException
from app.services.users import Users
from app.config import env
from app.services.oauth_client import GoogleOAuthClient, GithubOAuthClient, AppleOAuthClient, WechatOAuthClient, LinkedinOAuthClient
import logging
from pydantic import BaseModel
log = logging.getLogger(__name__)


router = APIRouter(tags=["Social Mobile"])


class SocialIdTokenRequest(BaseModel):
    id_token: str
    provider: str # google, apple, facebook, twitter, github, linkedin, wechat, qq, weibo, alipay

@router.post("/social/user")
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
    return user