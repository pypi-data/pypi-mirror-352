import jwt
from datetime import datetime, timedelta


# 验证令牌是否有效
def verify_token(token: str, jwt_secret: str = None, jwt_algorithm: str = "HS256"):
    """_summary_

    Args:
        token (str): 令牌
        jwt_secret (str, optional): JWT 秘钥. Defaults to None.
        jwt_algorithm (str, optional): JWT加密算法. Defaults to "HS256".

    Returns:
        dict: 解密后的数据
    """
    payload = jwt.decode(token, jwt_secret, algorithms=jwt_algorithm)
    return payload


# 生成 JWT 令牌的函数
def create_access_token(
    data: dict,
    expires_delta: int = 300,
    jwt_secret: str = None,
    jwt_algorithm: str = "HS256",
) -> str:
    """_summary_

    Args:
        data (dict): 数据载体
        expires_delta (int, optional): 过期时间单位分钟. Defaults to 300.
        jwt_secret (str, optional): JWT秘钥. Defaults to None.
        jwt_algorithm (str, optional): JWT加密算法. Defaults to "HS256".

    Returns:
        str : 加密后的令牌
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)

    to_encode.update({"exp": expire})  # 在令牌中加入过期时间
    encoded_jwt = jwt.encode(to_encode, jwt_secret, algorithm=jwt_algorithm)  # 加密令牌
    return encoded_jwt
