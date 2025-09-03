from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import jwt
import datetime
from app.utils.rands import rand_str
from typing import Tuple
from cryptography.hazmat.backends import default_backend
import base64


def eddsa_keypair()->Tuple[ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey]:
    priv = ed25519.Ed25519PrivateKey.generate()
    pub = priv.public_key()
    return priv, pub

def eddsa_keypair_pem()->Tuple[str, str]:
    priv, pub = eddsa_keypair()
    priv_pem = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,  # standard PKCS#8
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,  # X.509 SPKI
    )
    return priv_pem.decode('utf-8'), pub_pem.decode('utf-8')

def eddsa_sign(private_key_pem: str, message: bytes, encode_type: str = 'base64') -> str:
    if not private_key_pem.startswith("----"):
        private_key_pem = f"-----BEGIN PRIVATE KEY-----\n{private_key_pem}\n-----END PRIVATE KEY-----"
    priv_key = serialization.load_pem_private_key(private_key_pem.encode('utf-8'), password=None, backend=default_backend())
    signature = priv_key.sign(message)
    if encode_type == 'hex':
        return signature.hex()
    elif encode_type == 'base64':
        return base64.b64encode(signature).decode('utf-8')
    elif not encode_type or encode_type == 'bytes':
        return signature


def eddsa_verify(public_key_pem: str, message: bytes, signature: bytes) -> bool:
    if not public_key_pem.startswith("----"):
        public_key_pem = f"-----BEGIN PUBLIC KEY-----\n{public_key_pem}\n-----END PUBLIC KEY-----"
    pub_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'), backend=default_backend())
    try:
        pub_key.verify(signature, message)
        return True
    except Exception:
        return False

if __name__ == "__main__":
    priv_pem, pub_pem = eddsa_keypair_pem()
    print(priv_pem)
    print(pub_pem)
    signature = eddsa_sign(priv_pem, b"hello", encode_type="bytes")
    print(eddsa_verify(pub_pem, b"hello", signature))