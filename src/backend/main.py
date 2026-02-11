# 企业项目管理系统 - FastAPI应用入口

"""
企业项目管理系统后端API
Version: 1.0
Author: Development Team
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.models.database import init_db, close_db
from app.api.v1 import auth, projects, tasks, resources, planning, reports, approvals, gantt, risks, issues
from app.core.security import create_access_token


# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    print("🚀 启动应用...")
    init_db()
    print("✅ 数据库初始化完成")

    yield

    # 关闭时清理
    print("🛑 关闭应用...")
    close_db()
    print("✅ 数据库连接已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["认证接口"]
)

app.include_router(
    projects.router,
    prefix="/api/v1/projects",
    tags=["项目管理"]
)

app.include_router(
    tasks.router,
    prefix="/api/v1/projects",
    tags=["任务管理"]
)

app.include_router(
    resources.router,
    prefix="/api/v1/resources",
    tags=["资源管理"]
)

app.include_router(
    planning.router,
    prefix="/api/v1",
    tags=["计划管理"]
)

app.include_router(
    reports.router,
    prefix="/api/v1",
    tags=["报表统计"]
)

app.include_router(
    approvals.router,
    prefix="/api/v1",
    tags=["审批管理"]
)

app.include_router(
    gantt.router,
    prefix="/api/v1",
    tags=["甘特图"]
)

app.include_router(
    risks.router,
    prefix="/api/v1",
    tags=["风险管理"]
)

app.include_router(
    issues.router,
    prefix="/api/v1",
    tags=["问题跟踪"]
)


# 通用错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "Internal Server Error",
            "data": None,
            "error": str(exc)
        }
    )


# 根路径
@app.get("/", tags=["根路径"])
async def root():
    """应用根路径"""
    return {
        "message": "企业项目管理系统 API",
        "version": settings.APP_VERSION,
        "status": "running"
    }


# 健康检查
@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "database": "connected"
    }


# API信息
@app.get("/api", tags=["API信息"])
async def api_info():
    """API基本信息"""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs_url": "/api/docs",
        "endpoints": {
            "auth": "/api/v1/auth",
            "projects": "/api/v1/projects",
            "tasks": "/api/v1/projects/{project_id}/tasks"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
