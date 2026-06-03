"""
AI对话接口路由 (需登录)
POST /api/chat          — 发消息 + 自动保存历史
GET  /api/chat/history  — 获取历史记录
DELETE /api/chat/history — 清空历史记录
"""
import aiomysql
from fastapi import APIRouter, HTTPException, Header
from models.schemas import ChatRequest, ChatResponse
from services.llm_service import chat_with_deepseek
from services.auth_service import decode_token

router = APIRouter()


def _get_user_id(authorization: str) -> int:
    """从JWT中提取user_id"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="请先登录")
    payload = decode_token(authorization[7:])
    if payload is None:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    return payload["user_id"]


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(req: ChatRequest, authorization: str = Header(default="")):
    """AI对话，自动保存到数据库"""
    user_id = _get_user_id(authorization)

    if not req.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")

    try:
        reply = await chat_with_deepseek(req.message, req.history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI服务异常: {str(e)}")

    # 保存到数据库
    from database import get_pool
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO chat_history (user_id, role, content) VALUES (%s, 'user', %s)",
                (user_id, req.message),
            )
            await cur.execute(
                "INSERT INTO chat_history (user_id, role, content) VALUES (%s, 'assistant', %s)",
                (user_id, reply),
            )

    return ChatResponse(reply=reply)


@router.get("/chat/history")
async def get_history(authorization: str = Header(default="")):
    """获取当前用户的对话历史"""
    user_id = _get_user_id(authorization)

    from database import get_pool
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT role, content FROM chat_history WHERE user_id = %s ORDER BY created_at ASC",
                (user_id,),
            )
            rows = await cur.fetchall()

    return {"history": [{"role": r["role"], "content": r["content"]} for r in rows]}


@router.delete("/chat/history")
async def clear_history(authorization: str = Header(default="")):
    """清空当前用户的对话历史"""
    user_id = _get_user_id(authorization)

    from database import get_pool
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM chat_history WHERE user_id = %s", (user_id,)
            )

    return {"success": True, "message": "对话记录已清空"}
