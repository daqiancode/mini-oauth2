import jwt
import datetime
from app.utils.rands import rand_str


def sign_jwt(payload: dict, private_key_pem: str, algorithm: str = "EdDSA",headers: dict = None) -> str:
    return jwt.encode(payload, private_key_pem, algorithm=algorithm, headers=headers)

def verify_jwt(token: str, public_key_pem: str) -> dict:
    # get the algorithm from jwt token header
    header = jwt.get_unverified_header(token)
    algorithm = header.get('alg')
    audience = header.get('kid')
    return jwt.decode(token, public_key_pem, algorithms=algorithm , audience=audience)

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
    return sign_jwt(payload,private_key, algorithm=algorithm , headers={"kid": client_id})

from typing import Tuple

supported_algorithms = [
    "HS256",
    "HS384",
    "HS512",
    "RS256",
    "RS384",
    "RS512",
    "ES256",
    "ES384",
    "ES512",
    "EdDSA"
]

from app.utils.signs import hs_keypair, rs_keypair, es_keypair, eddsa_keypair


def is_supported_algorithm(algorithm:str) -> bool:
    return algorithm in supported_algorithms

def create_key_pair(algorithm:str) -> Tuple[str, str]:
    """
    create key pair for jwt
    @return: tuple of private key and public key
    """
    if not is_supported_algorithm(algorithm):
        raise ValueError(f"Invalid algorithm: {algorithm}")
    if algorithm == "HS256":
        return hs_keypair(32)
    elif algorithm == "HS384":
        return hs_keypair(48)
    elif algorithm == "HS512":
        return hs_keypair(64)
    elif algorithm == "RS256":
        return rs_keypair(2048)
    elif algorithm == "RS384":
        return rs_keypair(3072)
    elif algorithm == "RS512":
        return rs_keypair(4096)
    elif algorithm == "ES256":
        return es_keypair(256)
    elif algorithm == "ES384":
        return es_keypair(384)
    elif algorithm == "ES512":
        return es_keypair(521)
    elif algorithm == "EdDSA":
        return eddsa_keypair()
    else:
        raise ValueError(f"Invalid algorithm: {algorithm}")

