# 企业项目管理系统 - FastAPI配置
"""
应用程序配置管理
支持环境变量覆盖和多种数据库类型
"""

import os
from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基本信息
    APP_NAME: str = "企业项目管理系统"
    APP_DESCRIPTION: str = "企业级项目管理和任务协作平台"
    APP_VERSION: str = "1.0.0"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True  # 开发模式默认开启
    API_PREFIX: str = "/api"
    
    # 数据库配置 - 默认使用SQLite
    DATABASE_TYPE: str = "sqlite"  # sqlite, postgresql, mysql
    DATABASE_URL: str = "sqlite:///./app.db"
    DATABASE_ECHO: bool = False  # 是否打印SQL语句
    
    # PostgreSQL配置（如果使用PostgreSQL）
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "enterprise_project_management"
    
    # SQLite配置
    SQLITE_DB_PATH: str = "./app.db"
    
    # CORS配置
    ALLOWED_ORIGINS: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://localhost:3006",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:3006"
        ]
    )
    
    # JWT认证配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30天
    
    # Redis配置（缓存）
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    class Config:
        """Pydantic配置"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取应用配置（单例模式）"""
    return Settings()


# 全局配置实例
settings = get_settings()


def get_database_url() -> str:
    """获取数据库URL"""
    if settings.DATABASE_TYPE == "sqlite":
        # SQLite: sqlite:///./app.db (相对路径) 或 sqlite:////absolute/path/app.db (绝对路径)
        db_path = settings.SQLITE_DB_PATH
        if not os.path.isabs(db_path):
            # 转换为绝对路径
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                db_path
            )
        return f"sqlite:///{db_path}"
    
    elif settings.DATABASE_TYPE == "postgresql":
        # PostgreSQL: postgresql://user:password@host:port/dbname
        return (
            f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )
    
    elif settings.DATABASE_TYPE == "mysql":
        # MySQL: mysql://user:password@host:port/dbname
        return (
            f"mysql+pymysql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )
    
    else:
        # 默认使用SQLite
        return f"sqlite:///./app.db"


# 导出配置
__all__ = ["Settings", "get_settings", "settings", "get_database_url"]
