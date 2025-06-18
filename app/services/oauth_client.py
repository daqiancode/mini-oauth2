import httpx
from app.utils.urls import set_url_params
from fastapi import HTTPException
import logging
logger = logging.getLogger(__name__)

class OAuthClient:
    def __init__(self, client_id: str, client_secret: str, authorize_url: str, access_token_url: str, userinfo_endpoint: str, scope:str=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorize_url = authorize_url
        self.access_token_url = access_token_url
        self.userinfo_endpoint = userinfo_endpoint
        self.scope = scope
        self.authorization_extra_params = {}


    def get_authorize_url(self ,redirect_uri:str, state:str , **kwargs):
        # escape redirect_uri
        params = {}
        params.update(self.authorization_extra_params)
        params.update({
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": self.scope,
            "state": state
        })
        params.update(kwargs)
        return set_url_params(self.authorize_url, params)
    
    async def get_access_token(self, code:str, redirect_uri:str):
        data = {
            'grant_type': 'authorization_code',
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        async with httpx.AsyncClient(headers={"Accept": "application/json"}) as client:
            resp = await client.post(self.access_token_url, data=data)
            return resp.json()
        
    async def get_userinfo(self, access_token:str=None):
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.userinfo_endpoint, headers={"Authorization": f"Bearer {access_token}"})
            return resp.json()


class GoogleOAuthClient(OAuthClient):
    """
    https://accounts.google.com/.well-known/openid-configuration
    """
    def __init__(self, client_id: str, client_secret: str, authorize_url: str="https://accounts.google.com/o/oauth2/v2/auth", access_token_url: str="https://oauth2.googleapis.com/token", userinfo_endpoint: str="https://www.googleapis.com/oauth2/v3/userinfo", scope:str="email profile"):
        super().__init__(client_id, client_secret, authorize_url, access_token_url, userinfo_endpoint, scope)
        self.authorization_extra_params = {
            "access_type": "offline",
            "prompt": "consent"
        }

    async def get_userinfo(self, access_token:str=None):
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.userinfo_endpoint, headers={"Authorization": f"Bearer {access_token}"})
            return resp.json()



class GithubOAuthClient(OAuthClient):
    def __init__(self, client_id: str, client_secret: str, authorize_url: str="https://github.com/login/oauth/authorize", access_token_url: str="https://github.com/login/oauth/access_token", userinfo_endpoint: str="https://api.github.com/user", scope:str="user:email"):
        super().__init__(client_id, client_secret, authorize_url, access_token_url, userinfo_endpoint, scope)

    async def get_userinfo(self, access_token:str=None):
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.userinfo_endpoint, headers={"Authorization": f"Bearer {access_token}"})
            result = resp.json()
            if not result['email']:
                emails_endpoint = self.userinfo_endpoint + '/emails'
                resp = await client.get(emails_endpoint, headers={"Authorization": f"Bearer {access_token}"})
                emails = resp.json()
                if not emails:
                    raise HTTPException(status_code=400, detail="No email found")
                primary_email = next((email for email in emails if email['primary'] and email['verified']), None)
                if not primary_email:
                    primary_email = emails[0]
                result['email'] = primary_email['email']
            return result
        

class AppleOAuthClient(OAuthClient):
    def __init__(self, client_id: str, client_secret: str, authorize_url: str="https://appleid.apple.com/auth/authorize", access_token_url: str="https://appleid.apple.com/auth/token", userinfo_endpoint: str="https://appleid.apple.com/auth/userinfo", scope:str="email name"):
        super().__init__(client_id, client_secret, authorize_url, access_token_url, userinfo_endpoint, scope)
        self.authorization_extra_params = {
            "response_mode": "form_post"
        }


    async def get_userinfo(self, access_token:str=None):
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.userinfo_endpoint, headers={"Authorization": f"Bearer {access_token}"})
            return resp.json()
    


class WechatOAuthClient(OAuthClient):
    def __init__(self, client_id: str, client_secret: str, authorize_url: str="https://open.weixin.qq.com/connect/qrconnect", access_token_url: str="https://api.weixin.qq.com/sns/oauth2/access_token", userinfo_endpoint: str="https://api.weixin.qq.com/sns/userinfo", scope:str="snsapi_login" , lang:str="zh_CN"):
        super().__init__(client_id, client_secret, authorize_url, access_token_url, userinfo_endpoint, scope)
        self.lang = lang

    def get_authorize_url(self ,redirect_uri:str, state:str , **kwargs):
        params = {
            "appid": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": self.scope,
            "state": state,
            "lang": self.lang
        }
        params.update(kwargs)
        return set_url_params(self.authorize_url, params)+"#wechat_redirect"
    
    async def get_access_token(self, code:str, redirect_uri:str=None):
        data = {
            'appid': self.client_id,
            'secret': self.client_secret,
            'grant_type': 'authorization_code',
            "code": code
        }
        async with httpx.AsyncClient(headers={"Accept": "application/json"}) as client:
            resp = await client.post(self.access_token_url, data=data)
            return resp.json()

    async def get_userinfo(self, access_token:str=None ,openid:str=None):
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.userinfo_endpoint, params={"openid": openid , "access_token": access_token, "lang": self.lang})
            logger.info("wechat userinfo: %s", resp.json())
            return resp.json()
    

class LinkedinOAuthClient(OAuthClient):
    def __init__(self, client_id: str, client_secret: str, authorize_url: str="https://www.linkedin.com/oauth/v2/authorization", access_token_url: str="https://www.linkedin.com/oauth/v2/accessToken", userinfo_endpoint: str="https://api.linkedin.com/v2/me", scope:str="r_liteprofile r_emailaddress"):
        super().__init__(client_id, client_secret, authorize_url, access_token_url, userinfo_endpoint, scope)

    async def get_userinfo(self, access_token:str=None):
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.userinfo_endpoint, headers={"Authorization": f"Bearer {access_token}"})
            return resp.json()
    