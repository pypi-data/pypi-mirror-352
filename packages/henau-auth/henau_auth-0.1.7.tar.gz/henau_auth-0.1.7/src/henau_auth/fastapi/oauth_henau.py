from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from .utils.jwt import verify_token, create_access_token
from starlette.responses import Response, JSONResponse, RedirectResponse
import random


def generate_secret():
    return "".join(
        [
            random.choice(
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            )
            for i in range(32)
        ]
    )


class HenauAuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        login_router: str = "/login",
        excluded_routes: list[str] = None,
        redirect_url: str = None,
        get_user_func: callable = None,
        oauth2_user_func: callable = None,
        expires_delta: int = 3600,
        jwt_secret: str = generate_secret(),
        enable_permission_controller=True,
        *args,
        **keywords,
    ) -> None:
        """_summary_

        Args:
            app (_type_): ASGI APP 应用对象
            login_router (str, optional): 登录路由. Defaults to "/login".
            excluded_routes (list[str], optional): 排除的路由. Defaults to None.
            redirect_url (str, optional): 重定向地址. Defaults to None , 鉴权失败时自动重定向，为空则不启用.
            get_user_func (callable, optional): 获取用户方法，不传将默认使用payload. Defaults to None.
            oauth2_user_func (callable, optional): 用户授权方法，接受code 返回用户信息载体. Defaults to None.
            expires_delta (int, optional): 令牌过期时间. Defaults to 3600.
            jwt_secret (str, optional): 令牌秘钥. Defaults to "".join( [ random.choice( "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" ) for i in range(32) ] ).
            enable_permission_controller (bool, optional): 是否启用权限控制. Defaults to True 启用后 request中会携带一个casbin 权限控制对象.
        """
        super().__init__(app, *args, **keywords)
        self.login_router = login_router
        self.excluded_routes = excluded_routes if excluded_routes else []
        self.redirect_url = redirect_url
        self.get_user_func = get_user_func
        self.oauth2_user_func = oauth2_user_func
        self.jwt_secret = jwt_secret
        self.expires_delta = expires_delta
        self.enable_permission_controller = enable_permission_controller

    def auth(self, request: Request):
        if request.url.path == self.login_router:
            code = request.query_params.get("code")
            try:
                payload = self.oauth2_user_func(code)
            except Exception as e:
                return JSONResponse(status_code=401, content={"message": str(e)})
            request.state.payload = payload
            request.state.user = (
                self.get_user_func(payload) if self.get_user_func else payload
            )
            request.state.token = create_access_token(
                payload, expires_delta=self.expires_delta, jwt_secret=self.jwt_secret
            )
        else:
            if request.url.path not in self.excluded_routes:
                if request.headers.get("Authorization") is None:
                    if self.redirect_url:
                        return RedirectResponse(self.redirect_url)
                    return JSONResponse(
                        status_code=401, content={"message": "未提供令牌"}
                    )
                else:
                    token = request.headers.get("Authorization").split(" ")[1]
                    try:
                        payload = verify_token(token, jwt_secret=self.jwt_secret)
                    except Exception:
                        if self.redirect_url:
                            return RedirectResponse(self.redirect_url)
                        return JSONResponse(
                            status_code=401, content={"message": "令牌错误"}
                        )
                    request.state.payload = payload
                    request.state.user = (
                        self.get_user_func(payload) if self.get_user_func else payload
                    )

    def permission_controller(self, request: Request):
        if self.enable_permission_controller:
            from ..casbin import get_enforcer

            request.state.e = get_enforcer()

    async def dispatch(self, request: Request, call_next):
        funcs = [self.auth, self.permission_controller]
        for func in funcs:
            res = func(request)
            if isinstance(res, Response):
                return res

        return await call_next(request)
