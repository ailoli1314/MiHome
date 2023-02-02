from typing import Optional
from werkzeug.exceptions import HTTPException
from flask import Flask, request, jsonify
from functools import wraps
from config.config_parser import auth_key
from MiApi import MiService
from MiApi.service import Device
import json

app = Flask(__name__)
service = MiService()
devices = []


def locate_device(device_id: str, device_name=None) -> Optional[Device]:
    if device_id:
        for device in devices:
            if device[0] == device_id:
                return device[-1]
        device = service.use_device(device_id)
        devices.append((device_id, device))
        return device
    else:
        if not device_name:
            return None
        try:
            device = service.find_device(device_name)
        except Exception as e:
            return None
        return device


def auth_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        authorization = request.headers.get('Authorization')
        if not authorization == auth_key:
            return jsonify({
                "message": "Unauthorized",
                "code": 401
            }), 401
        return func(*args, **kwargs)

    return wrapper


def handle_form(req: request):
    try:
        data = request.get_json(silent=True)
    except:
        data = None
    if data is None:
        data = request.form
    return data


@app.route('/api/do_action', methods=['POST'])
def do_action():
    data = handle_form(request)
    device_id = data.get('device_id')
    device_name = data.get("device_name")
    device = locate_device(device_id, device_name)
    if device is None:
        return jsonify(code=404, message="Device not found"), 404
    sid = data.get('sid')
    aid = data.get('aid')
    action = data.get('params')
    return jsonify(device.do_action(sid, aid, action))


@app.route("/api/get_prop", methods=['POST'])
def get_prop():
    data = handle_form(request)
    device_id = data.get('device_id')
    device_name = data.get("device_name")
    device = locate_device(device_id, device_name)
    if device is None:
        return jsonify(code=404, message="Device not found"), 404
    sid = data.get('sid')
    pid = data.get('pid')
    return jsonify(device.get_device_prop(sid, pid))


@app.route("/api/get_props", methods=['POST'])
def get_props():
    data = handle_form(request)
    device_id = data.get('device_id')
    device_name = data.get("device_name")
    device = locate_device(device_id, device_name)
    if device is None:
        return jsonify(code=404, message="Device not found"), 404
    params = data.get('params')
    return jsonify(device.get_device_props(params))


@app.route("/api/set_prop", methods=['POST'])
def set_prop():
    data = handle_form(request)
    device_id = data.get('device_id')
    device_name = data.get("device_name")
    device = locate_device(device_id, device_name)
    if device is None:
        return jsonify(code=404, message="Device not found"), 404
    sid = data.get('sid')
    pid = data.get('pid')
    value = data.get("value")
    return jsonify(device.set_device_prop(sid, pid, value))


@app.route("/api/set_props", methods=['POST'])
def set_props():
    data = handle_form(request)
    device_id = data.get('device_id')
    device_name = data.get("device_name")
    device = locate_device(device_id, device_name)
    if device is None:
        return jsonify(code=404, message="Device not found"), 404
    params = data.get('params')
    return jsonify(device.set_device_props(params))


@app.route("/api/get_device_list", methods=['GET'])
def get_device_list():
    return jsonify(service.get_device_list())


# 全局错误处理
@app.errorhandler(HTTPException)
def handle_internal_server_error(e):
    response = e.get_response()
    response.data = json.dumps(
        {"code": e.code, "msg": "服务器错误",
         "data": {"http_code": e.code, "name": e.name, "description": e.description}
         }
    )
    response.content_type = "application/json"
    return response