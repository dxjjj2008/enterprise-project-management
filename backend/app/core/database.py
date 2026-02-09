from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

# 数据库 URL 配置（SQLite）
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 特定配置
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基础模型类
Base = declarative_base()

# 数据库会话依赖
def get_db() -> Generator:
    """
    获取数据库会话的依赖函数
    
    用于 FastAPI 的依赖注入系统
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
