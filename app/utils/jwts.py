import jwt
import datetime
from app.utils.rands import rand_str


def sign_jwt(payload: dict, private_key_pem: str, algorithm: str = "EdDSA") -> str:
    return jwt.encode(payload, private_key_pem, algorithm=algorithm)

def verify_jwt(token: str, public_key_pem: str) -> dict:
    # get the algorithm from jwt token header
    algorithm = jwt.get_unverified_header(token).get('alg')
    return jwt.decode(token, public_key_pem, algorithms=algorithm)

def create_access_token(private_key: str , user_id: str , client_id: str , roles: str ,expire_in_hours: int ,algorithm: str = "EdDSA",**kwargs):
    payload = {
        "sub": str(user_id),
        "aud": client_id,
        "exp": datetime.datetime.now() + datetime.timedelta(hours=expire_in_hours),
        "jti": rand_str(20)
    }
    if roles:
        payload['roles'] = roles
    if kwargs:
        payload.update(kwargs)
    return sign_jwt(payload,private_key, algorithm=algorithm)

