# 企业项目管理系统 - 数据库模块
"""
数据库引擎和会话管理
支持SQLAlchemy 2.0和多种数据库类型
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from app.core.config import settings, get_database_url

# 同步数据库引擎
_engine = None
_SessionLocal = None

# 异步数据库引擎
_async_engine = None
_async_session_maker = None

# 数据库模型基类
Base = declarative_base()


def get_engine():
    """获取同步数据库引擎（单例模式）"""
    global _engine
    
    if _engine is None:
        database_url = get_database_url()
        
        # 根据数据库类型配置引擎
        if settings.DATABASE_TYPE == "sqlite":
            # SQLite配置
            _engine = create_engine(
                database_url,
                echo=settings.DATABASE_ECHO,
                poolclass=StaticPool,
                connect_args={
                    "check_same_thread": False
                }
            )
        else:
            # PostgreSQL/MySQL配置
            _engine = create_engine(
                database_url,
                echo=settings.DATABASE_ECHO,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10
            )
    
    return _engine


def get_session_local():
    """获取同步会话工厂"""
    global _SessionLocal
    
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine()
        )
    
    return _SessionLocal


def get_async_engine():
    """获取异步数据库引擎（单例模式）"""
    global _async_engine
    
    if _async_engine is None:
        database_url = get_database_url()
        
        # 异步SQLite (SQLite不支持真正的异步，这里使用线程池模拟)
        if settings.DATABASE_TYPE == "sqlite":
            _async_engine = create_async_engine(
                "sqlite+aiosqlite:///:memory:",
                echo=settings.DATABASE_ECHO,
                poolclass=StaticPool,
                connect_args={
                    "check_same_thread": False
                }
            )
        else:
            # PostgreSQL异步引擎
            async_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
            _async_engine = create_async_engine(
                async_url,
                echo=settings.DATABASE_ECHO,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10
            )
    
    return _async_engine


def get_async_session_maker():
    """获取异步会话工厂"""
    global _async_session_maker
    
    if _async_session_maker is None:
        _async_session_maker = async_sessionmaker(
            bind=get_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
    
    return _async_session_maker


def init_db():
    """初始化数据库"""
    # 延迟导入以避免循环导入
    from sqlalchemy.orm import aliased
    
    # 创建所有表
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def close_db():
    """关闭数据库连接"""
    global _engine, _SessionLocal, _async_engine, _async_session_maker
    
    if _engine is not None:
        _engine.dispose()
        _engine = None
    
    if _async_engine is not None:
        _async_engine.dispose()
        _async_engine = None
    
    _SessionLocal = None
    _async_session_maker = None


# 同步会话依赖
def get_db() -> Generator[Session, None, None]:
    """获取数据库会话（同步）"""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 异步会话依赖
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（异步）"""
    async_session_maker = get_async_session_maker()
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    """异步上下文管理器获取数据库会话"""
    async_session_maker = get_async_session_maker()
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# 导出
__all__ = [
    "Base",
    "get_engine",
    "get_session_local",
    "get_async_engine",
    "get_async_session_maker",
    "init_db",
    "close_db",
    "get_db",
    "get_async_db",
    "async_get_db"
]
