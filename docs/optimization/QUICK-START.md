# 快速恢复工作指南

**最后工作位置**: 第2步（创建后端核心文件）

---

## 🚀 快速开始

### 1. 进入项目目录
```bash
cd /home/du/.openclaw/workspace/enterprise-project-management
```

### 2. 查看当前进度
```bash
cat docs/optimization/WORK-STATUS-2026-02-09.md
```

### 3. 检查已完成的文件
```bash
ls -la src/backend/
cat src/backend/main.py
cat src/backend/requirements.txt
```

### 4. 继续创建后端核心文件

#### 步骤1: 创建配置文件
```bash
vim src/backend/app/core/config.py
```

```python
# 配置文件内容（从main.py中引入的settings）

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "企业项目管理系统"
    APP_DESCRIPTION: str = "企业级项目管理平台"
    APP_VERSION: str = "1.0.0"

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./data/project_management.db"
    DATABASE_DIR: str = "./data"
    DATABASE_FILE: str = "project_management.db"

    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS配置
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

#### 步骤2: 创建安全工具
```bash
vim src/backend/app/core/security.py
```

```python
# 安全工具（JWT和密码哈希）

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """验证令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
```

#### 步骤3: 创建数据库配置
```bash
vim src/backend/app/models/database.py
```

```python
# 数据库配置

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = "sqlite:///./data/project_management.db"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite特殊配置
    echo=settings.DEBUG
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()


def init_db():
    """初始化数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表已创建")


def close_db():
    """关闭数据库连接"""
    engine.dispose()


def get_db():
    """获取数据库会话（依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 📂 已完成文件清单

### 文档
- ✅ `docs/optimization/docs-consistency-report.md` - 文档一致性检查报告
- ✅ `docs/design/2026-02-09-architecture-updated.md` - 更新架构设计
- ✅ `docs/design/2026-02-09-database-design.md` - 数据库设计
- ✅ `docs/optimization/WORK-STATUS-2026-02-09.md` - 工作状态记录
- ✅ `docs/optimization/optimization-plan.md` - 优化实施计划

### 后端代码
- ✅ `src/backend/requirements.txt` - Python依赖
- ✅ `src/backend/main.py` - FastAPI应用入口

---

## 🎯 下一步任务清单

### 立即执行（今天）
- [ ] 创建 `app/core/config.py`
- [ ] 创建 `app/core/security.py`
- [ ] 创建 `app/models/database.py`
- [ ] 创建 `app/models/base.py`
- [ ] 创建 `app/models/organization.py`

### 今天完成
- [ ] 创建 `app/models/user.py`
- [ ] 创建 `app/models/project.py`
- [ ] 创建 `app/models/task.py`
- [ ] 创建 `app/api/v1/auth.py`

### 明天完成
- [ ] 创建 `app/api/v1/projects.py`
- [ ] 创建 `app/api/v1/tasks.py`
- [ ] 创建 `app/schemas/` 目录和文件
- [ ] 创建 `.env.example` 文件

---

## 💻 快速测试命令

### 1. 安装依赖
```bash
cd src/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 启动应用
```bash
cd src/backend
python main.py
```

### 3. 访问API文档
打开浏览器访问: http://localhost:8000/api/docs

### 4. 测试健康检查
```bash
curl http://localhost:8000/health
```

### 5. 停止应用
```bash
Ctrl + C
```

---

## 📊 进度跟踪

### 当前状态
- **开始时间**: 2026-02-09
- **完成时间**: 2026-02-09 00:47
- **工作时长**: 约3小时
- **完成度**: 40%

### 下次开始时间
- **预计**: 2026-02-10（明天）
- **预计时长**: 6-8小时

### 下次目标
完成所有核心后端文件（预计2-3天）

---

**准备好开始了吗？从步骤4开始！** 🚀
