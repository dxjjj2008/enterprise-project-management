# 后端 API 实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan.

**目标：** 实现 FastAPI 后端基础架构和用户认证 API

**架构：** RESTful API + JWT 认证 + SQLite/PostgreSQL

**技术栈：** Python, FastAPI, SQLAlchemy, JWT, SQLite

---

## 任务概览

| 任务ID | 任务名称 | 工时 | 优先级 |
|--------|----------|------|--------|
| T1 | FastAPI 项目初始化 | 1人天 | P0 |
| T2 | 数据库模型定义 | 2人天 | P0 |
| T3 | JWT 认证系统 | 2人天 | P0 |
| T4 | 用户 API 开发 | 2人天 | P0 |
| T5 | 项目 API 开发 | 2人天 | P1 |
| T6 | 任务 API 开发 | 3人天 | P1 |

---

## 详细任务

### Task 1: FastAPI 项目初始化

**文件：**
- 创建: `backend/app/main.py`
- 创建: `backend/app/config.py`
- 创建: `backend/requirements.txt`
- 创建: `backend/Dockerfile`
- 测试: `backend/tests/test_main.py`

**Step 1: 创建项目目录结构**

```bash
mkdir -p backend/app/{routers,models,schemas,services,utils}
mkdir -p backend/tests
```

**Step 2: 创建主应用入口**

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.config import settings
from app.routers import auth, users, projects, tasks

app = FastAPI(
    title="Enterprise Project Management API",
    description="企业项目管理系统后端 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["项目"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["任务"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

**Step 3: 创建配置文件**

```python
# backend/app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Enterprise Project Management"
    DEBUG: bool = True
    
    # 数据库
    DATABASE_URL: str = "sqlite:///./data.db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000"]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
```

**Step 4: 创建依赖文件**

```txt
# backend/requirements.txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
 alembic==1.13.1
aiosqlite==0.19.0
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0
```

**Step 5: 创建测试**

```python
# backend/tests/test_main.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
```

**Commands:**

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest tests/test_main.py -v
```

**Expected Output:**

```
collected 2 items

tests/test_main.py::test_health_check PASSED
tests/test_main.py::test_read_main PASSED
```

**Step 6: 提交代码**

```bash
git add backend/
git commit -m "feat(backend): initialize FastAPI project structure"
```

---

### Task 2: 数据库模型定义

**文件：**
- 创建: `backend/app/models/base.py`
- 创建: `backend/app/models/user.py`
- 创建: `backend/app/models/project.py`
- 创建: `backend/app/models/task.py`
- 创建: `backend/app/database.py`
- 测试: `backend/tests/test_models.py`

**Step 1: 创建数据库连接**

```python
# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Step 2: 创建基础模型**

```python
# backend/app/models/base.py
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from typing import Optional


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None
```

**Step 3: 创建用户模型**

```python
# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    avatar_url = Column(String(500), nullable=True)
```

**Step 4: 创建项目模型**

```python
# backend/app/models/project.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class Project(Base, TimestampMixin):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="planning")  # planning, active, completed, on_hold
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    progress = Column(Float, default=0.0)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # 关系
    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project")
```

**Step 5: 创建任务模型**

```python
# backend/app/models/task.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="todo")  # todo, in_progress, done
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    
    # 时间和进度
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    progress = Column(Float, default=0.0)
    
    # 关系
    project_id = Column(Integer, ForeignKey("projects.id"))
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    parent_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks")
    parent = relationship("Task", remote_side=[id], back_populates="subtasks")
    subtasks = relationship("Task", back_populates="parent")
    dependencies = Column(JSON, default=list)  # 依赖任务 ID 列表
```

**Step 6: 测试模型**

```python
# backend/tests/test_models.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Project, Task
from app.database import get_db


def test_create_user():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    user = User(username="test", email="test@test.com", hashed_password="hash")
    session.add(user)
    session.commit()
    
    assert user.id is not None
    assert user.username == "test"
    session.close()
```

**Commands:**

```bash
cd backend
pytest tests/test_models.py -v
```

**Expected Output:**

```
PASSED tests/test_models.py::test_create_user
```

**Step 7: 提交代码**

```bash
git add backend/app/models/ backend/app/database.py
git commit -m "feat(backend): add database models"
```

---

### Task 3: JWT 认证系统

**文件：**
- 创建: `backend/app/core/security.py`
- 创建: `backend/app/schemas/token.py`
- 创建: `backend/app/schemas/user.py`
- 修改: `backend/app/models/user.py`
- 测试: `backend/tests/test_auth.py`

**Step 1: 创建安全工具**

```python
# backend/app/core/security.py
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = decode_token(token)
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
```

**Step 2: 创建 Token Schema**

```python
# backend/app/schemas/token.py
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str = None
```

**Step 3: 创建 User Schema**

```python
# backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    avatar_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
```

**Step 4: 更新 User 模型**

```python
# backend/app/models/user.py 添加
def verify_password(self, password: str) -> bool:
    return verify_password(password, self.hashed_password)

def set_password(self, password: str):
    self.hashed_password = get_password_hash(password)
```

**Step 5: 编写认证测试**

```python
# backend/tests/test_auth.py
from datetime import timedelta
from app.core.security import create_access_token, decode_token


def test_create_token():
    data = {"sub": "testuser"}
    token = create_access_token(data, expires_delta=timedelta(minutes=30))
    payload = decode_token(token)
    assert payload["sub"] == "testuser"
    assert "exp" in payload
```

**Commands:**

```bash
cd backend
pytest tests/test_auth.py -v
```

**Expected Output:**

```
PASSED tests/test_auth.py::test_create_token
```

**Step 6: 提交代码**

```bash
git add backend/app/core/ backend/app/schemas/
git commit -m "feat(backend): add JWT authentication system"
```

---

### Task 4: 用户 API 开发

**文件：**
- 创建: `backend/app/routers/users.py`
- 创建: `backend/app/services/user_service.py`
- 测试: `backend/tests/test_users.py`

**Step 1: 创建用户服务**

```python
# backend/app/services/user_service.py
from sqlalchemy.orm import Session
from app.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserService:
    @staticmethod
    def create(db: Session, user_data: UserCreate) -> User:
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_by_username(db: Session, username: str) -> User:
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User:
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def update(db: Session, user: User, user_data: UserUpdate) -> User:
        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        db.commit()
        db.refresh(user)
        return user
```

**Step 2: 创建用户路由**

```python
# backend/app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.core.security import get_current_user
from app.schemas.user import UserUpdate, UserResponse
from app.services import user_service

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return user_service.UserService.update(db, current_user, user_data)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = user_service.UserService.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

**Step 3: 创建认证路由**

```python
# backend/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models import User
from app.core.security import verify_password, create_access_token, get_current_user
from app.schemas.token import Token
from app.config import settings
from app.services import user_service

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = user_service.UserService.get_by_username(db, form_data.username)
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=Token)
async def register(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # 检查用户是否存在
    existing = user_service.UserService.get_by_username(db, form_data.username)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # 创建用户
    user = user_service.UserService.create(db, {
        "username": form_data.username,
        "email": f"{form_data.username}@example.com",
        "password": form_data.password
    })
    
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=dict)
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }
```

**Step 4: 编写用户测试**

```python
# backend/tests/test_users.py
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.models import User
from app.core.security import get_password_hash


def test_create_user(client):
    response = client.post(
        "/api/v1/auth/register",
        data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_get_me(client, test_user):
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {test_user['token']}"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]
```

**Commands:**

```bash
cd backend
pytest tests/test_users.py -v
```

**Expected Output:**

```
PASSED tests/test_users.py::test_create_user
PASSED tests/test_users.py::test_get_me
```

**Step 5: 提交代码**

```bash
git add backend/app/routers/users.py backend/app/routers/auth.py backend/app/services/user_service.py
git commit -m "feat(backend): add user and auth APIs"
```

---

### Task 5: 项目 API 开发

**文件：**
- 创建: `backend/app/routers/projects.py`
- 创建: `backend/app/services/project_service.py`
- 创建: `backend/app/schemas/project.py`
- 测试: `backend/tests/test_projects.py`

**Step 1: 创建项目 Schema**

```python
# backend/app/schemas/project.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[float] = None


class ProjectResponse(ProjectBase):
    id: int
    status: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    progress: float
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
```

**Step 2: 创建项目服务**

```python
# backend/app/services/project_service.py
from sqlalchemy.orm import Session
from app.models import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    @staticmethod
    def create(db: Session, project_data: ProjectCreate, owner_id: int) -> Project:
        project = Project(
            **project_data.model_dump(),
            owner_id=owner_id
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project
    
    @staticmethod
    def get_by_id(db: Session, project_id: int) -> Project:
        return db.query(Project).filter(Project.id == project_id).first()
    
    @staticmethod
    def get_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
        return db.query(Project).filter(Project.owner_id == owner_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, project: Project, project_data: ProjectUpdate) -> Project:
        for field, value in project_data.model_dump(exclude_unset=True).items():
            setattr(project, field, value)
        db.commit()
        db.refresh(project)
        return project
    
    @staticmethod
    def delete(db: Session, project: Project):
        db.delete(project)
        db.commit()
```

**Step 3: 创建项目路由**

```python
# backend/app/routers/projects.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Project
from app.core.security import get_current_user
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services import project_service

router = APIRouter()


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return project_service.ProjectService.create(db, project_data, current_user.id)


@router.get("/", response_model=list[ProjectResponse])
async def get_projects(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return project_service.ProjectService.get_by_owner(db, current_user.id, skip, limit)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = project_service.ProjectService.get_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = project_service.ProjectService.get_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return project_service.ProjectService.update(db, project, project_data)


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = project_service.ProjectService.get_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    project_service.ProjectService.delete(db, project)
    return {"message": "Project deleted"}
```

**Step 4: 测试项目 API**

```python
# backend/tests/test_projects.py
from fastapi.testclient import TestClient


def test_create_project(client, test_user):
    response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "description": "Test description"},
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["owner_id"] == test_user["id"]
```

**Commands:**

```bash
cd backend
pytest tests/test_projects.py -v
```

**Expected Output:**

```
PASSED tests/test_projects.py::test_create_project
```

**Step 5: 提交代码**

```bash
git add backend/app/routers/projects.py backend/app/services/project_service.py backend/app/schemas/project.py
git commit -m "feat(backend): add project APIs"
```

---

### Task 6: 任务 API 开发

**文件：**
- 创建: `backend/app/routers/tasks.py`
- 创建: `backend/app/services/task_service.py`
- 创建: `backend/app/schemas/task.py`
- 测试: `backend/tests/test_tasks.py`

**Step 1: 创建任务 Schema**

```python
# backend/app/schemas/task.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"


class TaskCreate(TaskBase):
    project_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    assignee_id: Optional[int] = None
    parent_id: Optional[int] = None
    dependencies: List[int] = []


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    progress: Optional[float] = None
    assignee_id: Optional[int] = None
    dependencies: Optional[List[int]] = None


class TaskResponse(TaskBase):
    id: int
    status: str
    progress: float
    project_id: int
    assignee_id: Optional[int]
    parent_id: Optional[int]
    dependencies: List[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
```

**Step 2: 创建任务服务**

```python
# backend/app/services/task_service.py
from sqlalchemy.orm import Session
from app.models import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    @staticmethod
    def create(db: Session, task_data: TaskCreate, creator_id: int) -> Task:
        task = Task(
            **task_data.model_dump(exclude={"dependencies"}),
            dependencies=task_data.dependencies
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def get_by_id(db: Session, task_id: int) -> Task:
        return db.query(Task).filter(Task.id == task_id).first()
    
    @staticmethod
    def get_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100):
        return db.query(Task).filter(Task.project_id == project_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, task: Task, task_data: TaskUpdate) -> Task:
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def delete(db: Session, task: Task):
        db.delete(task)
        db.commit()
```

**Step 3: 创建任务路由**

```python
# backend/app/routers/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.core.security import get_current_user
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services import task_service, project_service

router = APIRouter()


@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 验证项目存在且用户有权限
    project = project_service.ProjectService.get_by_id(db, task_data.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return task_service.TaskService.create(db, task_data, current_user.id)


@router.get("/project/{project_id}", response_model=list[TaskResponse])
async def get_project_tasks(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return task_service.TaskService.get_by_project(db, project_id, skip, limit)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = task_service.TaskService.get_by_id(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = task_service.TaskService.get_by_id(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_service.TaskService.update(db, task, task_data)


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = task_service.TaskService.get_by_id(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task_service.TaskService.delete(db, task)
    return {"message": "Task deleted"}
```

**Step 4: 测试任务 API**

```python
# backend/tests/test_tasks.py
from fastapi.testclient import TestClient


def test_create_task(client, test_user, test_project):
    response = client.post(
        "/api/v1/tasks/",
        json={
            "title": "Test Task",
            "project_id": test_project["id"],
            "priority": "high"
        },
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["project_id"] == test_project["id"]


def test_update_task_status(client, test_user, test_task):
    response = client.put(
        f"/api/v1/tasks/{test_task['id']}",
        json={"status": "in_progress"},
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
```

**Commands:**

```bash
cd backend
pytest tests/test_tasks.py -v
```

**Expected Output:**

```
PASSED tests/test_tasks.py::test_create_task
PASSED tests/test_tasks.py::test_update_task_status
```

**Step 5: 提交代码**

```bash
git add backend/app/routers/tasks.py backend/app/services/task_service.py backend/app/schemas/task.py
git commit -m "feat(backend): add task APIs"
```

---

## 验收标准

- [ ] 所有 API 端点响应时间 < 200ms
- [ ] 单元测试覆盖率 > 80%
- [ ] API 文档完整（/docs）
- [ ] JWT Token 认证正常工作
- [ ] 权限控制正确
- [ ] 数据库迁移正常

## 相关文档

- [主计划文档](./2026-02-08-development-plan.md)
- [甘特图计划](./2026-02-08-gantt-chart-plan.md)
- [API 文档](../api/2026-02-08-api.md)

---

**创建时间:** 2026-02-08  
**版本:** v1.0
