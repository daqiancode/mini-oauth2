from app.services.oauth_client import GoogleOAuthClient, AppleOAuthClient, GithubOAuthClient, LinkedinOAuthClient, WechatOAuthClient, OAuthClient
from app.config import env

class Providers:
    providers = {}

    def __init__(self):
        if env.GOOGLE_CLIENT_ID and env.GOOGLE_CLIENT_SECRET:
            self.providers["google"] = GoogleOAuthClient(env.GOOGLE_CLIENT_ID, env.GOOGLE_CLIENT_SECRET)
        if env.APPLE_CLIENT_ID and env.APPLE_CLIENT_SECRET:
            self.providers["apple"] = AppleOAuthClient(env.APPLE_CLIENT_ID, env.APPLE_CLIENT_SECRET)
        if env.GITHUB_CLIENT_ID and env.GITHUB_CLIENT_SECRET:
            self.providers["github"] = GithubOAuthClient(env.GITHUB_CLIENT_ID, env.GITHUB_CLIENT_SECRET)
        if env.LINKEDIN_CLIENT_ID and env.LINKEDIN_CLIENT_SECRET:
            self.providers["linkedin"] = LinkedinOAuthClient(env.LINKEDIN_CLIENT_ID, env.LINKEDIN_CLIENT_SECRET)
        if env.WECHAT_APPID and env.WECHAT_APPSECRET:
            self.providers["wechat"] = WechatOAuthClient(env.WECHAT_APPID, env.WECHAT_APPSECRET)


    def check_provider(self, provider:str)->bool:
        return provider in self.providers

    def get_provider(self, provider:str)->OAuthClient:
        return self.providers[provider]


providers = Providers()
