"""
数据接口路由
GET /api/skills  — 获取技能列表
GET /api/jobs    — 获取岗位列表
"""
import aiomysql
from fastapi import APIRouter, HTTPException
from database import get_pool

router = APIRouter()


@router.get("/skills")
async def get_skills():
    """获取全部技能列表（供前端标签云使用）"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT id, name, category FROM skills ORDER BY category, id"
            )
            skills = await cur.fetchall()

    return {"success": True, "data": skills, "total": len(skills)}


@router.get("/jobs")
async def get_jobs():
    """获取全部岗位列表"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM jobs ORDER BY id")
            jobs = await cur.fetchall()

    return {"success": True, "data": jobs, "total": len(jobs)}
