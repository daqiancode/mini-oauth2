from pydantic import BaseModel, ConfigDict
from enum import Enum

redis_prefix = "mini_oauth2/"
auth_prefix = redis_prefix + "auth/"
signup_prefix = redis_prefix + "signup/"

class Provider(str, Enum):
    google = "google"
    apple = "apple"
    github = "github"
    linkedin = "linkedin"
    wechat = "wechat"


class ResponseType(str, Enum):
    code = "code"
    password = "password"
    token = "token"
    id_token = "id_token"

class GrantType(str, Enum):
    authorization_code = "authorization_code"
    password = "password"
    implicit = "implicit"
    client_credentials = "client_credentials"
    refresh_token = "refresh_token"


class SigninRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    response_type: ResponseType
    client_id: str
    redirect_uri: str
    scope: str|None = None
    state: str|None = None
    provider: Provider|None = None


from app.drivers.cache import redis_client
import json
from app.config import settings
from app.utils.rands import rand_str


async def set_state(context: dict):
    state = rand_str(16)
    await redis_client.set(auth_prefix + 'state/' + state, json.dumps(context), ex=60*60*24)
    return state

async def get_state(state: str):
    data = await redis_client.get(auth_prefix + 'state/' + state)
    return json.loads(data) if data else None

async def delete_state(state: str):
    await redis_client.delete(auth_prefix + 'state/' + state)


async def set_code(context: dict, user_id: int|str):
    code = rand_str(16)
    await redis_client.set(auth_prefix+'code/' + code, json.dumps({'context':context, 'user_id':user_id}), ex=settings.JWT_EXPIRES_IN_HOURS * 60 * 60)
    return code


async def get_code(code: str):
    data = await redis_client.get(auth_prefix + 'code/' + code)
    return json.loads(data) if data else None

async def delete_code(code: str):
    await redis_client.delete(auth_prefix + 'code/' + code)


async def put_invalid_jti(jti: str , expires_in_seconds: int = settings.JWT_EXPIRES_IN_HOURS * 60 * 60):
    await redis_client.set(auth_prefix + 'invalid_jti/' + jti, '1', ex=expires_in_seconds)

async def get_invalid_jti(jti: str)->bool:
    data = await redis_client.get(auth_prefix + 'invalid_jti/' + jti)
    return data == b'1'