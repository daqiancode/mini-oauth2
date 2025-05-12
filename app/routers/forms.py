from pydantic import BaseModel
from enum import Enum

redis_prefix = "mini_oauth2/"
auth_prefix = redis_prefix + "auth/"
signup_prefix = redis_prefix + "signup/"

class ResponseType(str, Enum):
    code = "code"

class GrantType(str, Enum):
    authorization_code = "authorization_code"


class SigninRequest(BaseModel):
    response_type: ResponseType
    client_id: str
    redirect_uri: str
    scope: str|None = None
    state: str|None = None


from app.drivers.cache import redis_client
import json
from app.config import settings
from app.utils.rands import rand_str


def set_state( context:dict):
    state = rand_str(16)
    redis_client.set(auth_prefix + 'state/' + state, json.dumps(context) , ex=60*60*24)
    return state

def get_state(state:str):
    return json.loads(redis_client.get(auth_prefix + 'state/' + state))

def delete_state(state:str):
    redis_client.delete(auth_prefix + 'state/' + state)


def set_code( context:dict, user_id:int|str):
    code = rand_str(16)
    redis_client.set(auth_prefix+'code/' + code, json.dumps({'context':context, 'user_id':user_id}) , ex=settings.JWT_EXPIRES_IN)
    return code


def get_code(code:str):
    return json.loads(redis_client.get(auth_prefix + 'code/' + code))

def delete_code(code:str):
    redis_client.delete(auth_prefix + 'code/' + code)
