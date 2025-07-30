import requests
from typing import TypedDict


class AccessTokenAndOpenId(TypedDict):
    access_token: str
    henau_openid: str


def api_get_access_token_and_openid(
    app_id, app_secret, code, host: str = "https://oauth.henau.edu.cn"
) -> AccessTokenAndOpenId:
    url = (
        f"{host}"
        f"/oauth2_server"
        f"/access_token"
        f"?appid={app_id}"
        f"&secret={app_secret}"
        f"&code={code}"
        f"&grant_type=authorization_code"
    )

    response = requests.request("GET", url)

    if response.json()["status"] != "error":
        data = response.json().get("data")
        return {
            "access_token": data.get("access_token"),
            "henau_openid": data.get("henau_openid"),
        }
    else:
        raise Exception("code失效，获取access_token , openid失败")


class UserInfo(TypedDict):
    henau_openid: str
    user_name: str
    user_number: str
    user_section: str
    user_phone: str | None  # 如需该字段，请向信息化办公室单独申请
    user_nickname: str | None  # 如需该字段，请向信息化办公室单独申请
    user_avatar_url: str | None  # 如需该字段，请向信息化办公室单独申请
    user_status: int


def api_get_user_info(
    access_token: str, henau_openid: str, host: str = "https://oauth.henau.edu.cn"
) -> UserInfo:
    url = (
        f"{host}"
        f"/oauth2_server/userinfo"
        f"?access_token={access_token}"
        f"&henau_openid={henau_openid}"
    )

    response = requests.request("GET", url)

    if response.status_code == 200:
        data = response.json().get("data")
        return data
    else:
        raise Exception("获取信息失败")
