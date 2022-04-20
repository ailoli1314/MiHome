import configparser
import os

config = configparser.ConfigParser()

config.read(os.path.join(os.path.split(__file__)[0], "config.ini"), encoding='utf-8')


mi_user = config.get("account", "MiUsername")
mi_pass = config.get("account", "MiPassword")
mi_nick = config.get("account", "MiNickname")
auth_key = config.get("server", "AuthKey")

