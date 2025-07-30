import os
import base64
import json
import datetime
import requests
from typing import Optional
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


def _derive_key(secret_key: str, salt: Optional[str] = None) -> bytes:
    salt_bytes = salt.encode("utf-8")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt_bytes,
        iterations=100000,
        backend=default_backend(),
    )
    return kdf.derive(secret_key.encode("utf-8"))


def is_token_valid(token: str) -> bool:
    try:
        secret_key = os.environ["LLM7_SECRET_KEY"]
        salt = os.getenv("LLM7_SALT")
        key = _derive_key(secret_key, salt)

        raw = base64.b64decode(token)
        iv = raw[:12]
        ciphertext = raw[12:-16]
        tag = raw[-16:]

        aesgcm = AESGCM(key)
        decrypted = aesgcm.decrypt(iv, ciphertext + tag, None)
        data = json.loads(decrypted.decode())

        expiry = datetime.datetime.fromisoformat(data["expiresAt"])
        return datetime.datetime.utcnow() < expiry
    except Exception:
        return False


def token_exists(token: str) -> bool:
    try:
        base_url = os.environ["LLM7_TOKEN_URL"]
        secret_key = os.environ["LLM7_SECRET_KEY"]
        url = f"{base_url}/token_exists"
        headers = {"Authorization": f"Bearer {secret_key}"}
        response = requests.post(url, headers=headers, json={"token": token}, timeout=5)
        return response.status_code == 200 and response.json() is True
    except Exception:
        return False


def record_usage(email: str, token_value: str, model: str, tokens_in: int, tokens_out: int) -> bool:
    try:
        base_url = os.environ["LLM7_TOKEN_URL"]
        secret_key = os.environ["LLM7_SECRET_KEY"]
        url = f"{base_url}/admin/stats"
        headers = {"Authorization": f"Bearer {secret_key}"}
        payload = {
            "email": email,
            "token_value": token_value,
            "model": model,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
        }
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        return response.status_code == 201
    except Exception:
        return False
