# 企业项目管理系统 - API v1模块
"""
各业务模块API路由
"""

from app.api.v1 import auth, projects, tasks, resources, planning, reports, approvals, gantt, risks, issues

__all__ = [
    "auth",
    "projects",
    "tasks",
    "resources",
    "planning",
    "reports",
    "approvals",
    "gantt",
    "risks",
    "issues"
]
