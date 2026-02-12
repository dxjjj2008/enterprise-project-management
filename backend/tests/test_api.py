"""
企业项目管理系统 - 后端 API 测试

测试所有 API 端点的基本功能
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import Base, get_db
from app.models.project import Project, Task
from app.models.issue import Issue, IssueComment
from app.models.risk import Risk
from app.models.approval import Approval, ApprovalHistory
from app.models.plan import Plan, Milestone
from app.models.resource import Resource, Label

# 导入所有模型以确保它们已注册到 Base.metadata
from app.models import *


# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_project(db_session):
    project = Project(
        name="测试项目",
        description="测试项目描述",
        status="active"
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture(scope="function")
def test_task(db_session, test_project):
    task = Task(
        project_id=test_project.id,
        title="测试任务",
        description="测试任务描述",
        status="todo",
        priority="high",
        assigned_to="张三"
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


class TestHealthEndpoints:
    """测试健康检查端点"""
    
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "欢迎使用企业项目管理系统 API" in response.json()["message"]


class TestProjectsAPI:
    """测试项目管理 API"""
    
    def test_get_projects_empty(self, client):
        response = client.get("/api/v1/projects")
        assert response.status_code == 200
    
    def test_create_project(self, client):
        response = client.post(
            "/api/v1/projects",
            json={
                "name": "新项目",
                "description": "项目描述",
                "status": "draft"
            }
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "新项目"


class TestTasksAPI:
    """测试任务管理 API"""
    
    def test_get_tasks(self, client, test_project):
        response = client.get(f"/api/v1/projects/{test_project.id}/tasks")
        assert response.status_code == 200
    
    def test_create_task(self, client, test_project):
        response = client.post(
            f"/api/v1/projects/{test_project.id}/tasks",
            json={
                "title": "新任务",
                "description": "任务描述",
                "priority": "high"
            }
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["title"] == "新任务"
        assert data["status"] == "todo"
    
    def test_get_task_board(self, client, test_project, test_task):
        response = client.get(f"/api/v1/projects/{test_project.id}/tasks/board")
        assert response.status_code == 200
        data = response.json()["data"]
        assert "columns" in data
        assert "todo" in data["columns"]
    
    def test_update_task_status(self, client, test_project, test_task):
        response = client.put(
            f"/api/v1/projects/{test_project.id}/tasks/{test_task.id}/status",
            params={"status": "in_progress"}
        )
        assert response.status_code == 200
    
    def test_delete_task(self, client, test_project, test_task):
        response = client.delete(
            f"/api/v1/projects/{test_project.id}/tasks/{test_task.id}"
        )
        assert response.status_code == 200


class TestIssuesAPI:
    """测试问题跟踪 API"""
    
    def test_get_issues(self, client, test_project):
        response = client.get(f"/api/v1/projects/{test_project.id}/issues")
        assert response.status_code == 200
    
    def test_create_issue(self, client, test_project):
        response = client.post(
            f"/api/v1/projects/{test_project.id}/issues",
            params={
                "title": "新问题",
                "description": "问题描述",
                "priority": "high",
                "reporter": "张三"
            }
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["title"] == "新问题"


class TestRisksAPI:
    """测试风险管理 API"""
    
    def test_get_risks(self, client, test_project):
        response = client.get(f"/api/v1/projects/{test_project.id}/risks")
        assert response.status_code == 200
    
    def test_create_risk(self, client, test_project):
        response = client.post(
            f"/api/v1/projects/{test_project.id}/risks",
            params={
                "title": "新风险",
                "description": "风险描述",
                "level": "high",
                "probability": "medium"
            }
        )
        assert response.status_code == 200
    
    def test_get_risk_matrix(self, client, test_project):
        response = client.get(f"/api/v1/projects/{test_project.id}/risks/matrix")
        assert response.status_code == 200


class TestApprovalsAPI:
    """测试审批流程 API"""
    
    def test_get_approvals(self, client):
        response = client.get("/api/v1/approvals")
        assert response.status_code == 200
    
    def test_create_approval(self, client):
        response = client.post(
            "/api/v1/approvals",
            params={
                "title": "新审批",
                "description": "审批描述",
                "approval_type": "project",
                "applicant": "张三",
                "approver": "李四"
            }
        )
        assert response.status_code == 200
    
    def test_approve_approval(self, client):
        # 先创建审批
        response = client.post(
            "/api/v1/approvals",
            params={
                "title": "测试审批",
                "description": "测试",
                "approval_type": "budget",
                "applicant": "张三",
                "approver": "李四"
            }
        )
        approval_id = response.json()["data"]["id"]
        
        # 审批通过
        response = client.post(
            f"/api/v1/approvals/{approval_id}/approve",
            params={"comment": "测试通过"}
        )
        assert response.status_code == 200


class TestPlanningAPI:
    """测试计划管理 API"""
    
    def test_get_plans(self, client):
        response = client.get("/api/v1/planning")
        assert response.status_code == 200
    
    def test_create_plan(self, client):
        response = client.post(
            "/api/v1/planning",
            params={
                "title": "新计划",
                "description": "计划描述",
                "owner": "张三"
            }
        )
        assert response.status_code == 200
    
    def test_add_milestone(self, client):
        # 先创建计划
        response = client.post(
            "/api/v1/planning",
            params={
                "title": "测试计划",
                "description": "测试"
            }
        )
        plan_id = response.json()["data"]["id"]
        
        # 添加里程碑
        response = client.post(
            f"/api/v1/planning/{plan_id}/milestones",
            params={
                "title": "里程碑1",
                "date": "2026-03-01"
            }
        )
        assert response.status_code == 200


class TestResourcesAPI:
    """测试资源管理 API"""
    
    def test_get_resources(self, client):
        response = client.get("/api/v1/resources")
        assert response.status_code == 200
    
    def test_get_utilization(self, client):
        response = client.get("/api/v1/resources/utilization")
        assert response.status_code == 200
    
    def test_get_departments(self, client):
        response = client.get("/api/v1/resources/departments")
        assert response.status_code == 200


class TestReportsAPI:
    """测试报表统计 API"""
    
    def test_get_project_report(self, client):
        response = client.get("/api/v1/reports/projects")
        assert response.status_code == 200
    
    def test_get_task_report(self, client):
        response = client.get("/api/v1/reports/tasks")
        assert response.status_code == 200
    
    def test_get_resource_report(self, client):
        response = client.get("/api/v1/reports/resources")
        assert response.status_code == 200
    
    def test_get_overview_report(self, client):
        response = client.get("/api/v1/reports/overview")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
