# 企业项目管理系统 - API模块
"""
API路由模块初始化
"""

from fastapi import APIRouter

# 创建主API路由器
api_router = APIRouter()

# 导入并注册各模块路由
from app.api.v1 import auth, projects, tasks

api_router.include_router(
    auth.router,
    prefix="/v1/auth",
    tags=["认证接口"]
)

api_router.include_router(
    projects.router,
    prefix="/v1/projects",
    tags=["项目管理"]
)

api_router.include_router(
    tasks.router,
    prefix="/v1/projects",
    tags=["任务管理"]
)

__all__ = ["api_router"]
