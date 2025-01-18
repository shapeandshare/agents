import hashlib
import hmac
import os


def hash_it(payload: str):
    secret_key: bytes = os.environ["HASH_KEY"].encode(encoding="utf-8")

    # Create an HMAC object with SHA256
    hmac_obj: hmac.HMAC = hmac.new(secret_key, payload.encode(encoding="utf-8"), hashlib.sha256)

    # Calculate the HMAC signature
    signature = hmac_obj.hexdigest()

    # print(signature)  # Output: a 64-character hexadecimal string
    return signature
