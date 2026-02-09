# 企业项目管理系统 - Core模块
"""
核心模块初始化
提供配置、数据库、安全等基础功能
"""

from app.core.config import settings, get_settings, get_database_url

__all__ = [
    "settings",
    "get_settings",
    "get_database_url"
]
