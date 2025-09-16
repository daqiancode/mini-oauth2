from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from typing import Tuple
from cryptography.hazmat.backends import default_backend
import base64
from abc import ABC, abstractmethod

from jwt import algorithms
from app.utils.rands import rand_str
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import rsa


def hs_keypair(key_size: int = 32) -> Tuple[str,str]:
    key = rand_str(key_size)
    return key, key

def eddsa_keypair()->Tuple[str,str]:
    priv = ed25519.Ed25519PrivateKey.generate()
    pub = priv.public_key()
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


def rs_keypair(key_size: int = 2048) -> Tuple[str,str]:
    priv = rsa.generate_private_key(key_size)
    pub = priv.public_key()
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

def es_keypair(key_size: int = 256) -> Tuple[str,str]:
    if key_size == 256:
        curve = ec.SECP256R1()
    elif key_size == 384:
        curve = ec.SECP384R1()
    elif key_size == 521:
        curve = ec.SECP521R1()
    elif key_size == 224:
        curve = ec.SECP224R1()
    elif key_size == 192:
        curve = ec.SECP192R1()
    else:
        raise ValueError(f"Invalid key size: {key_size}")
    priv = ec.generate_private_key(curve)
    pub = priv.public_key()
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

