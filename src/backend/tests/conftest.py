# 企业项目管理系统 - API测试配置
"""
测试配置和 fixtures
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from app.models.database import Base, get_db
from app.core.security import get_password_hash
from app.models import User, UserRole, Project, ProjectMember, Task, TaskStatus

# 测试数据库引擎
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # 清理测试数据
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    """创建测试用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
        role=UserRole.MEMBER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_project(db_session, test_user):
    """创建测试项目"""
    project = Project(
        name="Test Project",
        key="TST",
        description="A test project",
        owner_id=test_user.id,
        status="planning"
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    
    # 添加项目成员
    member = ProjectMember(
        project_id=project.id,
        user_id=test_user.id,
        role=UserRole.ADMIN
    )
    db_session.add(member)
    db_session.commit()
    
    return project


@pytest.fixture(scope="function")
def auth_token(test_user):
    """生成认证令牌"""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": str(test_user.id), "username": test_user.username})
    return token


@pytest.fixture(scope="function")
def auth_headers(auth_token):
    """生成认证请求头"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="function")
def other_user(db_session):
    """创建另一个测试用户"""
    user = User(
        username="otheruser",
        email="other@example.com",
        hashed_password=get_password_hash("otherpassword"),
        full_name="Other User",
        role=UserRole.MEMBER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
