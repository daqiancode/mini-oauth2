import jwt
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import base64
from typing import Dict, Tuple
from app.utils.rands import rand_str

def generate_eddsa_keypair() -> Dict[str, str]:
    """
    Generate a new EdDSA key pair and return them as base64 encoded strings.
    
    Returns:
        Dict[str, str]: Dictionary containing 'private_key' and 'public_key' as base64 strings
    """
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    
    return {
        "private_key": base64.b64encode(private_bytes).decode(),
        "public_key": base64.b64encode(public_bytes).decode()
    }

def create_jwt(payload: dict, private_key: str) -> str:
    """
    Create a JWT token using EdDSA algorithm.
    
    Args:
        payload (dict): The JWT payload
        private_key (str): Base64 encoded private key
    
    Returns:
        str: JWT token
    """
    key_bytes = base64.b64decode(private_key)
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(key_bytes)
    return jwt.encode(payload, private_key, algorithm="EdDSA")

def verify_jwt(token: str, public_key: str) -> dict:
    """
    Verify and decode a JWT token using EdDSA algorithm.
    
    Args:
        token (str): JWT token to verify
        public_key (str): Base64 encoded public key
    
    Returns:
        dict: Decoded JWT payload
    """
    key_bytes = base64.b64decode(public_key)
    public_key = ed25519.Ed25519PublicKey.from_public_bytes(key_bytes)
    return jwt.decode(token, public_key, algorithms="EdDSA")

from app.config import settings
import datetime
# create access token with Ed25519 algorithm
def create_access_token(user_id: str , role: str ,duration_minutes: int=settings.JWT_EXPIRES_IN,**kwargs):
    payload = {
        "sub": str(user_id),
        "exp": datetime.datetime.now() + datetime.timedelta(minutes=duration_minutes)
    }
    if role:
        payload['role'] = role
    if kwargs:
        payload.update(kwargs)
    key_bytes = base64.b64decode(settings.JWT_PRIVATE_KEY)
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(key_bytes)
    return jwt.encode(payload, private_key, algorithm="EdDSA")

if __name__ == "__main__":
    # Generate a new key pair
    keys = generate_eddsa_keypair()
    print("Generated EdDSA keys:")
    print(f"Private key: {keys['private_key']}")
    print(f"Public key: {keys['public_key']}")
    # # Verify the JWT
    access_token = create_access_token("123","admin",60)
    print("access_token:",access_token)
    print("verify_jwt:",verify_jwt(access_token,settings.JWT_PUBLIC_KEY))