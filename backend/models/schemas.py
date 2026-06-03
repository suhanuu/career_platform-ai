"""
「职引未来」Pydantic 数据模型
定义所有 API 的请求/响应结构
"""
from pydantic import BaseModel, Field
from typing import List, Optional


# 技能相关模型

class SkillResponse(BaseModel):
    """返回给前端的技能对象"""
    id: int
    name: str
    category: str   # hard / soft

    class Config:
        from_attributes = True


# 岗位相关模型

class JobSkillDetail(BaseModel):
    """岗位要求中的单个技能详情"""
    skill_id: int
    skill_name: str
    importance: int    # 1-5

    class Config:
        from_attributes = True


class JobResponse(BaseModel):
    """返回给前端的岗位对象"""
    id: int
    title: str
    description: str
    industry: str
    salary_min: int
    salary_max: int
    education: str
    experience: str
    skills: List[JobSkillDetail] = []   # 岗位要求的技能列表

    class Config:
        from_attributes = True


# AI对话模型

class ChatRequest(BaseModel):
    """AI对话请求"""
    message: str = Field(..., min_length=1, max_length=2000, description="用户输入的消息")
    history: List[dict] = Field(default=[], description="对话历史，格式: [{\"role\":\"user/assistant\",\"content\":\"...\"}]")


class ChatResponse(BaseModel):
    """AI对话响应"""
    reply: str = Field(..., description="AI回复内容")
    model: str = Field(default="deepseek-chat", description="使用的模型名称")


# 技能匹配模型

class MatchRequest(BaseModel):
    """技能匹配请求"""
    skill_ids: List[int] = Field(..., min_length=1, description="用户选中的技能ID列表")


class SkillGap(BaseModel):
    """技能差距详情"""
    skill_name: str
    importance: int       # 岗位对该技能的重要度 1-5
    user_has: bool        # 用户是否拥有该技能


class MatchResult(BaseModel):
    """单个岗位的匹配结果"""
    job: JobResponse
    match_rate: float = Field(..., ge=0, le=100, description="匹配度百分比")
    radar_data: dict = Field(..., description="雷达图数据: {\"labels\":[...], \"user_values\":[...], \"job_values\":[...]}")
    skill_gaps: List[SkillGap] = Field(..., description="技能差距分析")


class MatchResponse(BaseModel):
    """技能匹配完整响应"""
    results: List[MatchResult] = Field(..., description="匹配结果列表（Top5，按匹配度降序）")


# 通用响应模型

class APIResponse(BaseModel):
    """通用API响应包装"""
    success: bool = True
    message: str = "ok"
    data: Optional[dict] = None


# ========================================
# 认证相关模型
# ========================================

class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    email: str = Field(default="", max_length=100, description="邮箱(选填)")


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=1, description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class AuthResponse(BaseModel):
    """认证响应（含token和用户信息）"""
    token: str
    user: dict


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: str = ""
    created_at: str = ""
