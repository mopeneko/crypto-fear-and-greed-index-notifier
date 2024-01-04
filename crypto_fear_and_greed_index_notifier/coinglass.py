import json
from Crypto.Cipher import AES
import base64
import zlib
import httpx


def aes_ecb_decrypt(cipher_data, secret_key):
    cipher = AES.new(secret_key, AES.MODE_ECB)
    plaintext = cipher.decrypt(cipher_data)
    return plaintext


def derive_key_from_header_and_path(header_encrypted, api_path):
    derived_key = base64.b64encode(
        ("coinglass" + f"/api/{api_path}" + "coinglass").encode("utf-8")
    ).decode("utf-8")
    derived_key = derived_key[:16]
    plaintext_key = aes_ecb_decrypt(
        base64.b64decode(header_encrypted), derived_key.encode("utf-8")
    )

    return plaintext_key.hex()


def fetch_long_short_rate():
    API_BASE_URL = "fapi.coinglass.com"
    API_PATH = "futures/longShortRate"

    USER_HEADER = "np2bO7ZbU/fdgqaLwe7D0QEJRpN7SFxep9gFyNIGvAR/UDUoiTOfkPwwxCNuSzik"

    master_key = derive_key_from_header_and_path(USER_HEADER, API_PATH)
    decompressed_master_key = zlib.decompress(
        bytes.fromhex(master_key), zlib.MAX_WBITS | 16
    ).decode("utf-8")

    response = httpx.get(
        f"https://{API_BASE_URL}/api/{API_PATH}",
        params={"symbol": "BTC", "timeType": 1},
    )
    response_data = response.json()["data"]

    master_key = derive_key_from_header_and_path(response.headers["user"], API_PATH)
    decompressed_master_key = zlib.decompress(
        bytes.fromhex(master_key), zlib.MAX_WBITS | 16
    ).decode("utf-8")

    # print(f"Master Key: {decompressed_master_key}")
    # print(f"IV: None (ECB)\n")

    decrypted_response = aes_ecb_decrypt(
        base64.b64decode(response_data), decompressed_master_key.encode("utf-8")
    ).hex()

    # print(f"Decrypted Response: {decrypted_response}\n")

    decompressed_response = zlib.decompress(
        bytes.fromhex(decrypted_response), zlib.MAX_WBITS | 16
    )

    # print(f"Decompressed Response: {decompressed_response.decode('utf-8')}")
    return json.loads(decompressed_response.decode("UTF-8"))
