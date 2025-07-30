import json
import requests
from typing import TypedDict, Optional


class DataValue(TypedDict):
    value: str


class Data(TypedDict):
    keyword1: Optional[DataValue]
    keyword2: Optional[DataValue]
    keyword3: Optional[DataValue]
    keyword4: Optional[DataValue]
    keyword5: Optional[DataValue]


def api_send_message_by_weixin_base(
    app_id: str,
    app_secret: str,
    henau_openid: str,
    template_number: str,
    jump_link: str,
    data: Data,
    host: str = "https://oauth.henau.edu.cn",
):
    try:
        url = f"{host}/oauth2_server/message?appid={app_id}&secret={app_secret}"

        response = requests.post(
            url,
            data=json.dumps(
                {
                    "henau_openid": henau_openid,
                    "template_number": template_number,
                    "url": jump_link,
                    "data": data,
                }
            ),
        )
        if response.json()["status"] != "error":
            return True

    except Exception as e:
        print(e)
        return False


def api_send_message_by_sms_base(
    app_id: str,
    app_secret: str,
    henau_openid: str,
    template_number: str,
    data: Data,
    host: str = "https://oauth.henau.edu.cn",
):
    try:
        url = f"{host}/oauth2_server/sendsms?appid={app_id}&secret={app_secret}"

        response = requests.post(
            url,
            data=json.dumps(
                {
                    "henau_openid": henau_openid,
                    "sms_template_number": template_number,
                    "data": data,
                }
            ),
        )

        if response.json()["status"] != "error":
            return True

    except Exception as e:
        print(e)
        return False
