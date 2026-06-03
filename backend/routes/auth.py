"""
认证接口路由
POST /api/auth/register — 注册
POST /api/auth/login    — 登录
GET  /api/auth/me        — 获取当前用户
"""
import aiomysql
from fastapi import APIRouter, HTTPException, Header
from models.schemas import RegisterRequest, LoginRequest, AuthResponse
from services.auth_service import hash_password, verify_password, create_token, decode_token
from database import get_pool

router = APIRouter()


@router.post("/auth/register")
async def register(req: RegisterRequest):
    """用户注册"""
    pool = await get_pool()

    # 检查用户名是否已存在
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT id FROM users WHERE username = %s", (req.username,)
            )
            if await cur.fetchone():
                raise HTTPException(status_code=409, detail="用户名已存在")

    # 创建用户
    password_hash = hash_password(req.password)
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)",
                (req.username, password_hash, req.email or ""),
            )
            user_id = cur.lastrowid

    # 签发 token
    token = create_token(user_id, req.username)

    return AuthResponse(
        token=token,
        user={"id": user_id, "username": req.username, "email": req.email or ""},
    )


@router.post("/auth/login")
async def login(req: LoginRequest):
    """用户登录"""
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT id, username, password_hash, email, created_at FROM users WHERE username = %s",
                (req.username,),
            )
            user = await cur.fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_token(user["id"], user["username"])

    return AuthResponse(
        token=token,
        user={
            "id": user["id"],
            "username": user["username"],
            "email": user["email"] or "",
        },
    )


@router.get("/auth/me")
async def get_current_user(authorization: str = Header(default="")):
    """获取当前登录用户信息"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")

    token = authorization[7:]  # 去掉 "Bearer " 前缀
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")

    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT id, username, email, created_at FROM users WHERE id = %s",
                (payload["user_id"],),
            )
            user = await cur.fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"] or "",
        "created_at": str(user["created_at"]),
    }
