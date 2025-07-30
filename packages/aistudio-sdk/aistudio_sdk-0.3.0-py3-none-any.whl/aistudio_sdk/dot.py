"""
dot
"""
import time
import hashlib
import requests
import json
from aistudio_sdk.config import STUDIO_MODEL_API_URL_PREFIX_DEFAULT, SALT

def generate_api_key(salt: str, api_time) -> str:
    """get param"""
    raw = f"{api_time}_{salt}"
    print(raw)
    md5 = hashlib.md5(raw.encode()).hexdigest()  # MD5 加密
    return md5


def post_repo_statistic(
    repo_id: str,
    revision: str,
    action: dict,
) -> requests.Response:
    """post info"""
    address = STUDIO_MODEL_API_URL_PREFIX_DEFAULT
    url = f"{address}/modelcenter/v2/statistic/repo"
    api_time = int(time.time() * 1000)
    api_key = generate_api_key(SALT, api_time)
    payload = {
        "biz_id": "model",
        "repo_id": repo_id,
        "ac_type": "download",
        "client_type": "sdk",
        "revision": revision,
        "action": json.dumps(action),  # 序列化为 JSON 字符串
        "api_time": api_time,
        "api_key": api_key
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response