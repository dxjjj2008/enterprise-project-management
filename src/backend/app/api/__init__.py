# 企业项目管理系统 - API模块
"""
API路由模块初始化
"""

from fastapi import APIRouter

# 创建主API路由器
api_router = APIRouter()

# 导入并注册各模块路由
from app.api.v1 import auth, projects, tasks, resources, planning, reports, approvals

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

api_router.include_router(
    resources.router,
    prefix="/v1/resources",
    tags=["资源管理"]
)

api_router.include_router(
    planning.router,
    prefix="/v1",
    tags=["计划管理"]
)

api_router.include_router(
    reports.router,
    prefix="/v1",
    tags=["报表统计"]
)

api_router.include_router(
    approvals.router,
    prefix="/v1",
    tags=["审批管理"]
)

__all__ = ["api_router"]
