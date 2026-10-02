# import requests
# import random
# from time import sleep

# while True:
#     latitude = random.uniform(-90, 90)
#     longitude = random.uniform(-180, 180)
#     try:
#         response = requests.post("http://localhost:5000/data", json={"device": "gps", "latitude": latitude, "longitude": longitude})
#         print(f"[GPS] Sent: {latitude}, {longitude}")
#     except:
#         print("Connection failed.")
#     sleep(3)

import requests
import random
import os
from time import sleep
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac

# Use static keys and IV for debugging
aes_key = b'1234567890abcdef'  # 16-byte key
hmac_key = b'0987654321fedcba'  # 16-byte key
iv = b'0000000000000000'  # Static IV for testing

def add_padding(data: bytes) -> bytes:
    """Add PKCS#7 padding to data."""
    padding_length = 16 - (len(data) % 16)
    return data + bytes([padding_length] * padding_length)

def remove_padding(data: bytes) -> bytes:
    """Remove PKCS#7 padding."""
    padding_length = data[-1]
    if padding_length < 1 or padding_length > 16:
        raise ValueError(f"Invalid padding length: {padding_length}")
    return data[:-padding_length]

def encrypt_data(data: str) -> bytes:
    """Encrypt data using AES-128-CBC with PKCS#7 padding."""
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    padded_data = add_padding(data.encode('utf-8'))  # Apply proper padding
    return encryptor.update(padded_data) + encryptor.finalize()

def sign_data(data: str) -> bytes:
    """Generate HMAC-SHA256 signature."""
    h = hmac.HMAC(hmac_key, hashes.SHA256())
    h.update(data.encode('utf-8'))
    return h.finalize()

# Main loop
while True:
    latitude = random.uniform(-90, 90)
    longitude = random.uniform(-180, 180)
    data_str = f"{latitude},{longitude}"
    
    encrypted_data = encrypt_data(data_str)
    signature = sign_data(data_str)
    
    # Debug logs
    print(f"\n[GPS] Plaintext: {data_str}")
    print(f"[GPS] Encrypted: {encrypted_data.hex()}")
    
    try:
        response = requests.post(
            "http://localhost:5000/data",
            data=encrypted_data,
            headers={"HMAC": signature.hex()}
        )
        print(f"[GPS] Status Code: {response.status_code}")
    except Exception as e:
        print(f"[GPS] Error: {e}")
    
    sleep(3)