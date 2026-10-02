# import requests
# import random
# from time import sleep

# while True:
#     heart_rate = random.randint(60, 120)
#     try:
#         response = requests.post("http://localhost:5000/data", json={"device": "smartwatch", "heart_rate": heart_rate})
#         print(f"[Smartwatch] Sent: {heart_rate} BPM")
#     except:
#         print("Connection failed.")
#     sleep(2)

import requests
import random
from time import sleep
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
import os

aes_key = b'1234567890abcdef'  # Use the same 16-byte key across all devices
hmac_key = b'0987654321fedcba'  # Use the same HMAC key
iv = b'0000000000000000'  # Static IV (for debugging)

def add_padding(data: bytes) -> bytes:
    """Add PKCS#7 padding."""
    padding_length = 16 - (len(data) % 16)
    return data + bytes([padding_length] * padding_length)

def remove_padding(data: bytes) -> bytes:
    """Remove PKCS#7 padding."""
    padding_length = data[-1]
    if padding_length < 1 or padding_length > 16:
        raise ValueError(f"Invalid padding length: {padding_length}")
    return data[:-padding_length]

def encrypt_data(data: bytes) -> bytes:
    """Encrypt data using AES-128-CBC with PKCS#7 padding."""
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    padded_data = add_padding(data)  # FIXED: No need to encode
    return encryptor.update(padded_data) + encryptor.finalize()
    

def sign_data(data: str) -> bytes:
    """Generate HMAC-SHA256 signature."""
    h = hmac.HMAC(hmac_key, hashes.SHA256())
    h.update(data)
    return h.finalize()

while True:
    heart_rate = random.randint(60, 120)
    data = str(heart_rate).encode()
    encrypted_data = encrypt_data(data)
    signature = sign_data(data)
    try:
        response = requests.post(
            "http://localhost:5000/data",
            data=encrypted_data,
            headers={"HMAC": signature.hex()}
        )
        print(f"[Smartwatch] Sent encrypted: {encrypted_data.hex()}")
    except:
        print("Connection failed.")
    sleep(2)