import configparser
import os
import sys
if sys.platform == "darwin":
    os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

now_dir = os.getcwd()
sys.path.append(now_dir)
from MiApi import MiService
from MiApi import http_server

mi = MiService()
device_list = mi.get_device_list()
print(f"device_list: {device_list}")


config = configparser.ConfigParser()

config.read("config/config.ini", encoding='utf-8')

auth_key = config.get("server", "AuthKey")
HOST = config.get("server", "HOST")
PORT = config.get("server", "PORT")
http_server.run(host=HOST, port=PORT)