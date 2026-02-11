# 企业项目管理系统 - API测试配置
"""
测试配置和fixtures
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, date
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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


@pytest.fixture(scope="function")
def test_user_token(auth_token):
    """生成认证令牌（兼容旧测试写法）"""
    return auth_token


@pytest.fixture(scope="function")
def test_plan(db_session, test_project, test_user):
    """创建测试计划"""
    from app.models import Plan, PlanStatus
    plan = Plan(
        name="Test Plan",
        project_id=test_project.id,
        description="A test plan",
        status=PlanStatus.DRAFT,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 3, 31),
        owner_id=test_user.id
    )
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)
    return plan


@pytest.fixture(scope="function")
def test_plan_id(test_plan):
    """返回测试计划ID"""
    return test_plan.id


@pytest.fixture(scope="function")
def test_wbs_task(db_session, test_plan):
    """创建测试WBS任务"""
    from app.models import WBSTask
    task = WBSTask(
        name="Test WBS Task",
        plan_id=test_plan.id,
        level=1,
        sort_order=0,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 15),
        duration=10,
        progress=0,
        status="pending"
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


@pytest.fixture(scope="function")
def test_task_id(test_wbs_task):
    """返回测试WBS任务ID"""
    return test_wbs_task.id


@pytest.fixture(scope="function")
def test_approval(db_session, test_user):
    """创建测试审批"""
    from app.models import Approval, ApprovalType, ApprovalStatus
    approval = Approval(
        type=ApprovalType.LEAVE,
        title="Test Leave Approval",
        description="Test approval for leave",
        applicant_id=test_user.id,
        status=ApprovalStatus.PENDING,
        form_data={"reason": "Test"}
    )
    db_session.add(approval)
    db_session.commit()
    db_session.refresh(approval)
    return approval


@pytest.fixture(scope="function")
def test_approval_id(test_approval):
    """返回测试审批ID"""
    return test_approval.id
