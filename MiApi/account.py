from config import *
import json
import requests
import os
from . import utils
from urllib import parse
import requests.utils

MiUser = mi_user
MiPass = mi_pass
MiNick = mi_nick


class TokenStore:
    """
    存取小米账号token
    """

    def __init__(self):
        self.token_path = os.path.join(os.path.expanduser("~"), '.xd_mi_token')
        self.token = self.__read_token()

    def __read_token(self):
        if not os.path.exists(self.token_path):
            return dict()
        with open(self.token_path, "r", encoding="utf-8") as fp:
            return json.load(fp)

    def __write_token(self):
        with open(self.token_path, "w+", encoding="utf-8") as fp:
            json.dump(self.token, fp)

    def get_file_token(self):
        return self.__read_token()

    def save_token(self, token: dict):
        self.token = token
        self.__write_token()

    def update_token(self, key, value):
        self.token[key] = value
        self.__write_token()
        return self.token


class MiAccountSession:
    def __init__(self, username: str = MiUser, password: str = MiPass, nickname: str = MiNick):
        self.username = username
        self.password = password
        self.nickname = nickname
        self.session = requests.Session()
        self.token_store = TokenStore()
        self.token = self.token_store.token
        self.request = self.__init_session()

    def __init_session(self):
        if not self.token:
            self.token = self.__login()
            if not self.token:
                raise Exception("登录失败， 检查用户名密码")
        self.session.headers = {'User-Agent': 'APP/com.xiaomi.mihome APPV/6.0.103 iosPassportSDK/3.9.0 iOS/14.4 miHSTS',
                                'x-xiaomi-protocal-flag-cli': 'PROTOCAL-HTTP2'}
        cookies = {
            'serviceToken': self.token.get("service_token"),
            "userId": self.token.get("user_id"),
            "PassportDeviceId": self.token.get("device_id")
        }
        requests.utils.add_dict_to_cookiejar(self.session.cookies, cookies)
        return self.session

    def __get_login_data(self, device_id):
        url = "https://account.xiaomi.com/pass/serviceLogin?sid=xiaomiio&_json=true"
        headers = {'User-Agent': 'APP/com.xiaomi.mihome APPV/6.0.103 iosPassportSDK/3.9.0 iOS/14.4 miHSTS'}
        cookies = {'sdkVersion': '3.9', 'deviceId': device_id}
        self.login_session.headers = headers
        requests.utils.add_dict_to_cookiejar(self.login_session.cookies, cookies)
        r = self.login_session.get(url)
        result = json.loads(r.text[11:])
        return dict(qs=result.get("qs"), sid=result.get("sid"),
                    _sign=result.get("_sign"), callback=result.get("callback"),
                    user=self.username, hash=utils.get_hash(self.password))

    def __login(self):
        self.login_session = requests.Session()
        url = "https://account.xiaomi.com/pass/serviceLoginAuth2"
        device_id = utils.get_random(16) if not self.token else self.token.get("deviceId")  # 本设备的ID 如果没有的话随机生成一个
        data = self.__get_login_data(device_id)
        data["_json"] = "true"
        r = self.login_session.post(url, data=data)
        result = json.loads(r.text[11:])
        code = result.get("code")
        if not code:
            user_id = result.get("userId")
            pass_token = result.get("passToken")
            location = result.get("location")
            nonce = result.get("nonce")
            security_token = result.get("ssecurity")
            service_token = self.__get_service_token(location, nonce, security_token)
            token = {
                "user_id": str(user_id),
                "pass_token": pass_token,
                "device_id": device_id,
                "service_token": service_token,
                "security_token": security_token,
                "username": self.username,
            }
            self.token_store.save_token(token)
            return token
        else:
            return dict()

    def __get_service_token(self, location, nonce, security_token):
        n = f"nonce={str(nonce)}&{security_token}"
        sign = utils.base64.b64encode(utils.hashlib.sha1(n.encode()).digest()).decode()
        url = f"{location}&clientSign={parse.quote(sign)}"
        r = self.login_session.get(url)
        token = r.cookies.get("serviceToken")
        return token
