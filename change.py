import requests
import configparser

config = configparser.ConfigParser()

config.read("config/config.ini", encoding='utf-8')

HOST = config.get("server", "HOST")
PORT = config.get("server", "PORT")


def set_device_property(sid, pid, value, device_id, device_name=None):
    print("set_device_property")
    url = f"http://{HOST}:{PORT}/api/set_prop"  # 替换为实际服务器地址
    headers = {
        "Authorization": "122661"  # 带上 Authorization 头
    }
    params = {
        "sid": sid,
        "pid": pid,
        "value": value,
        "device_id": device_id,
    }

    # 如果 device_name 不为空，则添加到请求参数中
    if device_name:
        params["device_name"] = device_name

    # 发起 POST 请求
    response = requests.post(url, headers=headers, json=params)

    # 检查请求是否成功
    if response.status_code == 200:
        data = response.json()
        # 判断响应 code 是否为 0
        if data.get("code") == 0:
            print("Request successful:", data)
            return data
        else:
            print("Error in response:", data.get("msg"))
            return None
    else:
        print("Failed to connect to the server:", response.status_code)
        return None
print("About to set device property...")
set_device_property(sid=2, pid=1, value=False, device_id="674063304")