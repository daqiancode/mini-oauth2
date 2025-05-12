import cryptography
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import base64
import hashlib

def generate_key_from_secret(secret: str) -> bytes:
    """
    Generate an AES key from a secret string using MD5
    
    Args:
        secret: Secret string to generate key from
    
    Returns:
        16-byte (128-bit) key derived from MD5 hash
    """
    return hashlib.md5(secret.encode('utf-8')).digest()

def aes_encrypt(plaintext: str, secret: str) -> str:
    """
    Encrypt a string using AES encryption with MD5-derived key
    
    Args:
        plaintext: String to encrypt
        secret: Secret string to generate key from
    
    Returns:
        Base64 encoded encrypted string
    """
    # Generate key from secret
    key = generate_key_from_secret(secret)
    
    # Convert string to bytes
    plaintext_bytes = plaintext.encode('utf-8')
    
    # Generate a random IV
    iv = os.urandom(16)
    
    # Create an encryptor object
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    
    # Pad the data
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(plaintext_bytes) + padder.finalize()
    
    # Encrypt the data
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    # Combine IV and ciphertext and encode to base64
    encrypted_data = iv + ciphertext
    return base64.b64encode(encrypted_data).decode('utf-8')

def aes_decrypt(encrypted_text: str, secret: str) -> str:
    """
    Decrypt an AES encrypted string using MD5-derived key
    
    Args:
        encrypted_text: Base64 encoded encrypted string
        secret: Secret string used to generate key
    
    Returns:
        Decrypted string
    """
    # Generate key from secret
    key = generate_key_from_secret(secret)
    
    # Decode base64
    encrypted_data = base64.b64decode(encrypted_text)
    
    # Extract IV and ciphertext
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    
    # Create a decryptor object
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    
    # Decrypt the data
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Unpad the data
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    
    return plaintext.decode('utf-8')

