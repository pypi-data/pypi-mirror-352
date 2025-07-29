fastapi_template = {
    "fastapi_project": {
        "README.md": "# FastAPI Project\n\nThis is a FastAPI project generated automatically.",
        ".gitignore": "__pycache__/\n*.py[cod]\n*$py.class\n.env\n.venv\nvenv/\nENV/\n.env.local\n.env.development\n.env.test\n.env.production\n*.log\n",
        "app": {
            "__init__.py": "# Initialize app package",
            "config.py": """
            import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class Settings:
    def __init__(self, yaml_file: str = "config.yaml"):
        self._yaml_file = Path(yaml_file)
        self._load_settings()

    def _load_settings(self) -> None:
        if not self._yaml_file.exists():
            raise FileNotFoundError(f"配置文件 {self._yaml_file} 不存在")

        with open(self._yaml_file, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f) or {}

        self._set_attributes(config_data)

    def _set_attributes(self, config_data: Dict[str, Any]) -> None:
        for key, value in config_data.items():
            if isinstance(value, dict):
                # 对于嵌套字典，创建一个嵌套的 Settings 对象
                setattr(self, key, Settings._from_dict(value))
            else:
                setattr(self, key, value)

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "Settings":
        instance = cls.__new__(cls)
        instance._yaml_file = None  # 标记这不是从文件加载的实例
        instance._set_attributes(data)
        return instance

    def __repr__(self) -> str:
        attrs = []
        for key in sorted(self.__dict__.keys()):
            if not key.startswith("_"):
                value = getattr(self, key)
                attrs.append(f"{key}={repr(value)}")
        return f"Settings({', '.join(attrs)})"

    def reload(self) -> None:
        if self._yaml_file is None:
            raise RuntimeError("无法重新加载，此实例是从字典创建的")
        self._load_settings()


# 创建配置实例
settings = Settings()

            """,
            "main.py": """from fastapi import FastAPI, Request
from src.henau_auth import HenauAuth

app = FastAPI()

client = HenauAuth(
    app_id="", # 应用id
    app_secret="", # 应用密钥
    base_url="https://oauth.henau.edu.cn" # 授权服务器地址 默认为 https://oauth.henau.edu.cn
)


app.add_middleware(
    client.get_fastapi_middleware(),
    login_router="/login", # 登录接口的路由，默认为 /login
    excluded_routes=["/test"], # 排除的路由，被排除的路由不会进行鉴权，默认为 []
    jwt_secret="dasdsafdsfsregtrjukiuok", # jwt的密钥，不传值则每次动态生成一个 建议传值32位字符串即可
    expires_delta=3600, # jwt过期时间，默认为3600分钟，单位分钟
    # get_user_func = lambda payload: User.get_or_none(User.open_id == payload["henau_openid"]) 
    # 如果传入了get_user_func，则会在获取到用户信息后调用该函数，该函数可以返回一个用户对象，该用户对象会被存储在request.state.user中
)


@app.get("/login")
async def login(request: Request, code: str):
    return {"user": request.state.user, "token": request.state.token}


@app.get("/other")
async def user(request: Request):
    return {"user": request.state.user}


@app.get("/test")
async def test(request: Request, code: str = None):
    return {"code": code, "user": request.state}
""",
            "database.py": """from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()""",
            "routers": {
                "__init__.py": "",
            },
        },
        "tests": {
            "__init__.py": "",
            "test_main.py": """from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}""",
        },
    }
}
