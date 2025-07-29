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


def api_send_message_by_weixin_super(
    app_id: str,
    app_secret: str,
    name: str,
    henau_number: str,
    template_number: str,
    jump_link: str,
    data: Data,
    host: str = "https://oauth.henau.edu.cn",
) -> bool:
    try:
        url = f"{host}/oauth2_server/messagepro?appid={app_id}&secret={app_secret}"

        response = requests.post(
            url,
            data=json.dumps(
                {
                    "user_name": name,
                    "user_number": henau_number,
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


def api_send_message_by_sms_super(
    app_id: str,
    app_secret: str,
    name: str,
    henau_number: str,
    template_number: str,
    data: Data,
    host: str = "https://oauth.henau.edu.cn",
):
    try:
        url = f"{host}/oauth2_server/sendsmspro?appid={app_id}&secret={app_secret}"

        response = requests.post(
            url,
            data=json.dumps(
                {
                    "user_name": name,
                    "user_number": henau_number,
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
