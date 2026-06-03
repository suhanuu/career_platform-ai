"""
「职引未来」FastAPI 启动入口
包含: 应用创建 + 中间件 + 数据库连接 + 路由注册
"""
import sys
from pathlib import Path

# 确保 backend 目录在 Python 路径中
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from config import APP_TITLE, APP_VERSION, CORS_ORIGINS
from database import create_pool, close_pool, init_database


# 应用生命周期 (启动/关闭钩子)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 启动 & 关闭时执行"""
    # 启动时: 初始化数据库连接 + 建表 + 种子数据
    print(f"\n{'='*50}")
    print(f"  {APP_TITLE} v{APP_VERSION}")
    print(f"{'='*50}")
    await create_pool()
    await init_database()
    print(f"  服务已启动: http://localhost:8000")
    print(f"  API文档:    http://localhost:8000/docs")
    print(f"{'='*50}\n")
    yield
    # 关闭时: 释放连接池
    print("[服务] 正在关闭...")
    await close_pool()
    print("[服务] 已关闭")


# 创建 FastAPI 应用

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="AI驱动的大学生职业规划与技能匹配平台",
    lifespan=lifespan,
)

# 跨域中间件 (允许前端页面调用后端API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册 API 路由

from routes.chat import router as chat_router
from routes.match import router as match_router
from routes.data import router as data_router
from routes.auth import router as auth_router

app.include_router(chat_router, prefix="/api", tags=["AI对话"])
app.include_router(match_router, prefix="/api", tags=["技能匹配"])
app.include_router(data_router, prefix="/api", tags=["数据接口"])
app.include_router(auth_router, prefix="/api", tags=["用户认证"])


# 挂载前端静态文件 (最后注册, 避免拦截API路由)

frontend_path = Path(__file__).parent.parent / "frontend"

if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

    @app.get("/")
    async def serve_frontend():
        """返回前端首页"""
        return FileResponse(str(frontend_path / "index.html"))
else:
    @app.get("/")
    async def root():
        return {"message": "Frontend not found", "api_docs": "/docs"}


# 直接运行入口 (python main.py)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,        # 代码修改后自动重启
        log_level="info",
    )
