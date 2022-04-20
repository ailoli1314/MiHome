import random
import string
import os
import time
import base64
import hashlib
import hmac
import json
from datetime import datetime
import colorama


def get_random(length):
    return ''.join(random.sample(string.ascii_letters + string.digits, length))


def generate_nonce():
    nonce = os.urandom(8) + int(time.time() / 60).to_bytes(4, 'big')
    return base64.b64encode(nonce).decode()


def generate_signed_nonce(secret, nonce):
    m = hashlib.sha256()
    m.update(base64.b64decode(secret))
    m.update(base64.b64decode(nonce))
    return base64.b64encode(m.digest()).decode()


def generate_signature(url, signed_nonce, nonce, data):
    sign = '&'.join([url, signed_nonce, nonce, 'data=' + data])
    signature = hmac.new(key=base64.b64decode(signed_nonce),
                         msg=sign.encode(),
                         digestmod=hashlib.sha256).digest()
    return base64.b64encode(signature).decode()


def sign_data(uri, data, secret):
    if not isinstance(data, str):
        data = json.dumps(data)
    nonce = generate_nonce()
    signed_nonce = generate_signed_nonce(secret, nonce)
    signature = generate_signature(uri, signed_nonce, nonce, data)
    return {'_nonce': nonce, 'data': data, 'signature': signature}


def get_hash(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest().upper()


def info_log(message: str, module: str = "提示", *args, **kwargs):
    s = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sf = colorama.Fore.GREEN + message + colorama.Fore.RESET
    print(f"{s} [{module}] {sf}", *args, **kwargs)


def error_log(message: str, module: str = "错误", *args, **kwargs):
    s = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sf = colorama.Fore.RED + message + colorama.Fore.RESET
    print(f"{s} [{module}] {sf}", *args, **kwargs)
