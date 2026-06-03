"""
============================================
认证服务
bcrypt密码哈希 + JWT签发/校验
============================================
"""
from datetime import datetime, timedelta
import bcrypt
from jose import jwt, JWTError
from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_HOURS


def hash_password(password: str) -> str:
    """对密码做 bcrypt 哈希"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_token(user_id: int, username: str) -> str:
    """签发 JWT 令牌"""
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    """校验并解析 JWT，失败返回 None"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
