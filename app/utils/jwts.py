from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import jwt
import datetime

def generate_eddsa_keypair():
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    private_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_bytes.decode('utf-8'), public_bytes.decode('utf-8')


def sign_jwt_eddsa(payload: dict, private_key_pem: str) -> str:
    if not private_key_pem.startswith("----"):
        private_key_pem = f"-----BEGIN PRIVATE KEY-----\n{private_key_pem}\n-----END PRIVATE KEY-----"
    return jwt.encode(payload, private_key_pem, algorithm="EdDSA")

def verify_jwt_eddsa(token: str, public_key_pem: str) -> dict:
    if not public_key_pem.startswith("----"):
        public_key_pem = f"-----BEGIN PUBLIC KEY-----\n{public_key_pem}\n-----END PUBLIC KEY-----"
    return jwt.decode(token, public_key_pem, algorithms=["EdDSA"])

def create_access_token(private_key: str , user_id: str , roles: str ,duration_minutes: int,**kwargs):
    payload = {
        "sub": str(user_id),
        "exp": datetime.datetime.now() + datetime.timedelta(minutes=duration_minutes)
    }
    if roles:
        payload['roles'] = roles
    if kwargs:
        payload.update(kwargs)
    return sign_jwt_eddsa(payload,private_key)

if __name__ == "__main__":
    private_key , public_key = generate_eddsa_keypair()
    print(private_key)
    print(public_key)
    # token = sign_jwt_eddsa({"sub": "1234567890"}, private_key)
    # print(token)
    # print(verify_jwt_eddsa(token, public_key))