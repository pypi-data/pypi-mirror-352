from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import requests


class AdminServer(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        admin_secret: str,
        base_url: str = "http://127.0.0.1:8769",
        *args,
        **kwargs,
    ):
        super().__init__(app, *args, **kwargs)
        self.base_url = base_url
        self.secret = admin_secret

    async def dispatch(self, request, call_next):
        # 请求前的处理
        # 获取当前用户的信息，根据其状态处理
        request_id = None  # 请求id默认为空
        if hasattr(request.state, "payload"):
            # 上传用户请求信息，并且获取用户最新状态
            user_state_response = requests.post(
                url=self.base_url + "/api/v1/admin/requests",
                headers={"Authorization": f"Bearer {self.secret}"},
                data={"user": request.state.payload},
            )
            if user_state_response.status_code == 200:
                # 用户状态正常，继续处理请求
                user_state = user_state_response.json()
                request.state.user_state = user_state
                if user_state["state"]["value"] == "blacklist":
                    return JSONResponse(
                        status_code=403,
                        content={"message": user_state["state"]["message"]},
                    )
                request_id = user_state["id"]

        response = await call_next(request)

        # 请求后的处理
        # 将响应保存到admin server中

        if request_id:
            requests.post(
                url=self.base_url + "/api/v1/admin/requests",
                headers={"Authorization": f"Bearer {self.secret}"},
                data={
                    "user": request.state.payload,
                    "request_id": request_id,
                    "request": request,
                    "response": response,
                },
            )

        return response
