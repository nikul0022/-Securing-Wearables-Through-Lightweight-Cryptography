# from flask import Flask, request
# app = Flask(__name__)

# @app.route('/data', methods=['POST'])
# def receive_data():
#     data = request.get_json()
#     print(f"[CLOUD] Received: {data}")
#     return "OK"

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.exceptions import InvalidSignature

app = Flask(__name__)

# Static keys and IV for debugging
aes_key = b'1234567890abcdef'
hmac_key = b'0987654321fedcba'
iv = b'0000000000000000'  # Static IV

def remove_padding(data: bytes) -> bytes:
    """Remove PKCS#7 padding with strict validation."""
    if not data:
        raise ValueError("Data is empty")
    padding_length = data[-1]
    
    # Validate padding length
    if padding_length < 1 or padding_length > 16:
        raise ValueError(f"Invalid padding length: {padding_length}")
    
    # Validate padding bytes
    padding = data[-padding_length:]
    if padding != bytes([padding_length] * padding_length):
        raise ValueError("Invalid padding bytes")
    
    return data[:-padding_length]

def decrypt_data(encrypted_data: bytes) -> str:
    """Decrypt data using AES-128-CBC and remove PKCS#7 padding."""
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    return remove_padding(padded_data).decode('utf-8')

def verify_hmac(data: str, received_hmac: bytes):
    """Verify HMAC signature."""
    h = hmac.HMAC(hmac_key, hashes.SHA256())
    h.update(data.encode('utf-8'))
    h.verify(received_hmac)  # Throws exception if invalid
    
# @app.route('/data', methods=['POST'])
# def receive_data():
#     try:
#         encrypted_data = request.data  # Ciphertext only (no IV)
#         received_hmac = bytes.fromhex(request.headers.get("HMAC", ""))
        
#         # Decrypt using static IV
#         cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
#         decryptor = cipher.decryptor()
#         padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
#         # Debug logs
#         print(f"\n[CLOUD] Decrypted (with padding): {padded_data.hex()}")
        
#         # Remove padding
#         plaintext_bytes = remove_padding(padded_data)
#         plaintext = plaintext_bytes.decode('utf-8')
        
#         # Verify HMAC
#         h = hmac.HMAC(hmac_key, hashes.SHA256())
#         h.update(plaintext.encode('utf-8'))
#         h.verify(received_hmac)
        
#         print(f"[CLOUD] Verified: {plaintext}")
#         return jsonify({"status": "success"}), 200
    
#     except Exception as e:
#         print(f"[CLOUD] Error: {str(e)}")
#         return jsonify({"error": str(e)}), 400

@app.route('/data', methods=['POST'])
def receive_data():
    try:
        encrypted_data = request.data  # Get ciphertext
        received_hmac = bytes.fromhex(request.headers.get("HMAC", ""))  # Extract HMAC

        # Extract IV (first 16 bytes of data)
        if len(encrypted_data) > 16:
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]
        else:
            iv = b'0000000000000000'
            ciphertext = encrypted_data

        # Decrypt using AES-128-CBC
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove padding
        plaintext_bytes = remove_padding(padded_data)
        plaintext = plaintext_bytes.decode('utf-8')

        # Compute expected HMAC
        computed_hmac = hmac.HMAC(hmac_key, hashes.SHA256())
        computed_hmac.update(plaintext.encode('utf-8'))
        expected_hmac = computed_hmac.finalize()

        # Debug print the HMAC values
        print(f"[CLOUD] Received HMAC: {received_hmac.hex()}")
        print(f"[CLOUD] Expected HMAC: {expected_hmac.hex()}")

        # Verify HMAC
        if received_hmac != expected_hmac:
            print(f"[CLOUD] ⚠️ HMAC verification failed! Data might be tampered.")
            return jsonify({"error": "HMAC verification failed"}), 400
        
        print(f"[CLOUD] ✅ Verified: {plaintext}")
        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"[CLOUD] Error: {str(e)}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)