"""
技能匹配接口路由 (需登录)
POST /api/match
"""
from fastapi import APIRouter, HTTPException, Header
from models.schemas import MatchRequest, MatchResponse
from services.match_service import calculate_match
from services.auth_service import decode_token

router = APIRouter()


@router.post("/match", response_model=MatchResponse)
async def skill_match(req: MatchRequest, authorization: str = Header(default="")):
    """技能-岗位智能匹配，需携带 JWT"""
    # 验证登录
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="请先登录")
    payload = decode_token(authorization[7:])
    if payload is None:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")

    if not req.skill_ids:
        raise HTTPException(status_code=400, detail="请至少选择1个技能")
    if len(req.skill_ids) > 20:
        raise HTTPException(status_code=400, detail="最多选择20个技能")

    try:
        results = await calculate_match(req.skill_ids)
        return MatchResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"匹配服务异常: {str(e)}")
