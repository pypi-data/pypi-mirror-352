from .oauth2 import api_get_access_token_and_openid, api_get_user_info
from .oauth2 import AccessTokenAndOpenId, UserInfo
from .message import (
    api_send_message_by_sms_base,
    api_send_message_by_weixin_base,
    api_send_message_by_weixin_super,
    api_send_message_by_sms_super,
)
from .message import Data

from starlette.middleware.base import BaseHTTPMiddleware
from .fastapi.oauth_henau import HenauAuthMiddleware
from functools import partial
from typing import Literal

policy_enum = Literal["super_auth", "auth", "permission"]


class HenauAuth:
    def __init__(
        self, app_id: str, app_secret: str, base_url: str = "https://oauth.henau.edu.cn"
    ):
        """_summary_

        Args:
            app_id (str): APP ID
            app_secret (str): APP Secret
            base_url (_type_, optional): oauth2 地址. Defaults to "https://oauth.henau.edu.cn".
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = base_url

    def get_access_token_and_open_id(self, code: str) -> AccessTokenAndOpenId:
        """_summary_

        Args:
            code (str): 前端获取的code

        Returns:
            dict[str , str]: 包含access_token和henau_openid的字典
        """
        data = api_get_access_token_and_openid(
            self.app_id, self.app_secret, code, host=self.base_url
        )
        return data

    def get_user_info_by_access_token(
        self, access_token: str, henau_openid: str
    ) -> UserInfo:
        """_summary_

        Args:
            access_token (str): 通行令牌
            henau_openid (str): 用户唯一标识

        Returns:
            dict[str , str]: 用户信息
        """
        access_token_and_open_id = api_get_user_info(
            access_token, henau_openid, host=self.base_url
        )
        return access_token_and_open_id

    def get_user_info_super(self, code: str) -> UserInfo:
        """_summary_

        Args:
            code (_type_): 前端获得的code

        Returns:
            UserInfo: 获得的用户信息
        """
        access_token_and_open_id = self.get_access_token_and_open_id(code)
        user_info = self.get_user_info_by_access_token(
            access_token_and_open_id["access_token"],
            access_token_and_open_id["henau_openid"],
        )
        return user_info

    def send_message_by_weixin(
        self, henau_openid: str, template_number: str, jump_link: str, data: Data
    ) -> bool:
        """_summary_

        Args:
            henau_openid (str): 用户唯一标识
            template_number (str): 消息模版编号
            jump_link (str): 跳转链接
            data (Data): 数据载体

        Returns:
            bool: 是否成功
        """
        res = api_send_message_by_weixin_base(
            app_id=self.app_id,
            app_secret=self.app_secret,
            henau_openid=henau_openid,
            data=data,
            template_number=template_number,
            jump_link=jump_link,
            host=self.base_url,
        )
        return res

    def send_message_by_sms(
        self, henau_openid: str, template_number: str, data: Data
    ) -> bool:
        """_summary_

        Args:
            henau_openid (str): 用户唯一标识
            template_number (str): 短信模版编号
            data (Data): 数据载体

        Returns:
            bool: 是否成功
        """

        res = api_send_message_by_sms_base(
            app_id=self.app_id,
            app_secret=self.app_secret,
            henau_openid=henau_openid,
            data=data,
            template_number=template_number,
            host=self.base_url,
        )
        return res

    def send_message_by_weixin_super(
        self,
        name: str,
        henau_number: str,
        template_number: str,
        jump_link: str,
        data: Data,
    ) -> bool:
        """_summary_

        Args:
            name (str): 发送目标用户的名字
            henau_number (str): 发送目标用户的学工号
            template_number (str): 发送信息的模版编号
            jump_link (str): 跳转链接
            data (Data): 参数

        Returns:
            bool: 是否发送成功
        """
        res = api_send_message_by_weixin_super(
            app_id=self.app_id,
            app_secret=self.app_secret,
            name=name,
            henau_number=henau_number,
            data=data,
            template_number=template_number,
            jump_link=jump_link,
            host=self.base_url,
        )
        return res

    def send_message_by_sms_super(
        self, name: str, henau_number: str, template_number: str, data: Data
    ) -> bool:
        """_summary_

        Args:
            name (str): 发送目标用户的名字
            henau_number (str): 发送目标用户的学工号
            template_number (str): 发送信息的模版编号
            data (Data): 参数

        Returns:
            bool : 是否发送成功
        """
        res = api_send_message_by_sms_super(
            app_id=self.app_id,
            app_secret=self.app_secret,
            name=name,
            henau_number=henau_number,
            data=data,
            template_number=template_number,
            host=self.base_url,
        )
        return res

    def get_fastapi_middleware(
        self, policy: policy_enum = "super_auth"
    ) -> BaseHTTPMiddleware:
        """_summary_

        Returns:
            FastAPI Middleware: 返回一个FastAPI中间件,自动完成鉴权，令牌分发，令牌校验
        """
        get_user_funcs = {"super_auth": self.get_user_info_super}
        return partial(HenauAuthMiddleware, oauth2_user_func=get_user_funcs[policy])

    def get_fastapi_admin_server_middleware(self) -> BaseHTTPMiddleware:
        """
        admin server 是一个公共管理后台，目前仅可以管理用户和日志，开发者仅仅需要简单配置此中间件
        就可以在admin server中管理该应用 有关admin_server 的功能大致如下
        - 用户管理, 用户查看，自定义用户状态
        - 日志管理
        - 数据仪表盘
        - 数据管理
        """
        pass
