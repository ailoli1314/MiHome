from .account import MiAccountSession
from . import utils

DEVICES = []


class Device:
    def __init__(self, device_id: str):
        self.mi_account = MiAccountSession()
        self.session = self.mi_account.request
        self.security_token = self.mi_account.token.get("security_token")
        self.server_url = "https://api.io.mi.com/app"
        self.device_id = device_id

    def device_info(self):
        for device in DEVICES:
            if device.get("did") == self.device_id:
                return device
        return dict()

    def http_request(self, uri: str, data: dict = None) -> dict:
        url = self.server_url + uri
        if data:
            params = utils.sign_data(uri, data, self.security_token)
            r = self.session.post(url, data=params)
        else:
            r = self.session.get(url)
        return r.json()

    def do_action(self, sid, aid, values: list = [], pid="1"):
        uri = "/miotspec/action"
        params = dict(params={"did": self.device_id, "siid": sid, "piid": pid, "aiid": aid, "in": values})
        result = self.http_request(uri, params)
        request_code = result.get("code")
        if not request_code:
            data = result.get("result")
            code = result.get("code")
            if not code:
                return dict(code=0, msg="success", data=data)
            else:
                return dict(code=code, msg="error", data=dict())
        return dict(code=request_code, msg="request error", data=dict())

    def get_device_props(self, items: list):
        """
        :param items: [{"piid": pid, "siid": sid}]
        :return:
        """
        uri = "/miotspec/prop/get"
        params = dict(params=self.add_devices_id(items))
        result = self.http_request(uri, params)
        code = result.get("code")
        if not code:
            data = result.get("result")
            return dict(code=0, msg="success", data=data)
        else:
            return dict(code=code, msg=result.get("message"), data=list())

    def get_device_prop(self, sid, pid):
        uri = "/miotspec/prop/get"
        params=[{"did": self.device_id, "piid": pid, "siid": sid}]
        params = dict(params=[{"did": self.device_id, "piid": pid, "siid": sid}])
        result = self.http_request(uri, params)
        code = result.get("code")
        if not code:
            data = result.get("result")[0]
            return dict(code=0, msg="success", data=data)
        else:
            return dict(code=code, msg=result.get("message"), data=dict())

    def set_device_prop(self, sid, pid, value):
        uri = "/miotspec/prop/set"
        params = dict(params=[{"did": self.device_id, "piid": pid, "siid": sid, "value": value}])
        result = self.http_request(uri, params)
        code = result.get("code")
        if not code:
            data = result.get("result")[0]
            return dict(code=0, msg="success", data=data)
        else:
            return dict(code=code, msg=result.get("message"), data=dict())

    def set_device_props(self, items: list):
        uri = "/miotspec/prop/set"
        params = dict(params=self.add_devices_id(items))
        result = self.http_request(uri, params)
        code = result.get("code")
        if not code:
            data = result.get("result")
            return dict(code=0, msg="success", data=data)
        else:
            return dict(code=code, msg=result.get("message"), data=list())

    def add_devices_id(self, items: list):
        c = list()
        for item in items:
            item["did"] = self.device_id
            c.append(item)
        return c


class MiService:
    def __init__(self):
        mi_account = MiAccountSession()
        self.session = mi_account.request
        self.security_token = mi_account.token.get("security_token")
        global DEVICES
        DEVICES = self.__get_device_list()

    @staticmethod
    def find_device(device_name) -> Device:
        for device in DEVICES:
            name = device.get("name")
            if device_name in name:
                return Device(device.get("did"))
        raise Exception("device not found")

    @staticmethod
    def use_device(device_id):
        return Device(device_id)

    def __get_device_list(self):
        uri = "/home/device_list"
        params = {"getVirtualModel": False, "getHuamiDevices": 0}
        result = self.__http_request(uri, data=params)
        device_list = result.get("result").get("list")
        return result

    def get_device_list(self):
        result = self.__get_device_list()
        code = result.get("code")
        if not code:
            device_list = result.get("result").get("list")
            device_list = device_list if device_list else list()
            return dict(code=0, msg="success", data=device_list)
        else:
            return dict(code=code, msg=result.get("message"), data=list())

    def __http_request(self, uri: str, data: dict = None) -> dict:
        url = "https://api.io.mi.com/app" + uri
        if data:
            params = utils.sign_data(uri, data, self.security_token)
            r = self.session.post(url, data=params)
        else:
            r = self.session.get(url)
        return r.json()
