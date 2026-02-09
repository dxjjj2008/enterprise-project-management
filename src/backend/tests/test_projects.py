# 企业项目管理系统 - 项目API测试
"""
项目管理和成员管理API测试用例
"""

import pytest
from fastapi.testclient import TestClient

from app.models import User, Project, ProjectMember, Milestone, UserRole, ProjectStatus


class TestProjectAPI:
    """项目API测试类"""

    def test_create_project(self, client, db_session, test_user, auth_headers):
        """测试创建项目"""
        response = client.post(
            "/api/v1/projects",
            params={
                "name": "Test Project",
                "key": "TEST",
                "description": "A test project"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Project created successfully"
        assert data["project"]["name"] == "Test Project"
        assert data["project"]["key"] == "TEST"
        assert data["project"]["owner_id"] == test_user.id

    def test_create_duplicate_key(self, client, db_session, test_user, auth_headers):
        """测试重复项目Key"""
        # 创建第一个项目
        client.post(
            "/api/v1/projects",
            params={"name": "Project 1", "key": "DUPKEY"},
            headers=auth_headers
        )

        # 创建重复Key项目
        response = client.post(
            "/api/v1/projects",
            params={"name": "Project 2", "key": "DUPKEY"},
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "Project key already exists" in response.json()["detail"]

    def test_get_projects(self, client, db_session, test_user, auth_headers):
        """测试获取项目列表"""
        # 创建项目
        client.post(
            "/api/v1/projects",
            params={"name": "My Project", "key": "MYPROJ"},
            headers=auth_headers
        )

        response = client.get("/api/v1/projects", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1

    def test_get_project_detail(self, client, db_session, test_user, auth_headers):
        """测试获取项目详情"""
        # 创建项目
        create_resp = client.post(
            "/api/v1/projects",
            params={"name": "Detail Project", "key": "DETAIL"},
            headers=auth_headers
        )
        project_id = create_resp.json()["project"]["id"]

        response = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["project"]["name"] == "Detail Project"
        assert "stats" in data

    def test_get_project_not_member(self, client, db_session, test_user, other_user, auth_headers):
        """测试非成员访问项目"""
        # 创建项目
        create_resp = client.post(
            "/api/v1/projects",
            params={"name": "Private Project", "key": "PRIV"},
            headers=auth_headers
        )
        project_id = create_resp.json()["project"]["id"]

        # 使用其他用户的token访问
        from app.core.security import create_access_token
        other_token = create_access_token(data={"sub": str(other_user.id), "username": other_user.username})
        other_headers = {"Authorization": f"Bearer {other_token}"}

        response = client.get(f"/api/v1/projects/{project_id}", headers=other_headers)
        assert response.status_code == 404

    def test_update_project(self, client, db_session, test_user, auth_headers):
        """测试更新项目"""
        # 创建项目
        create_resp = client.post(
            "/api/v1/projects",
            params={"name": "Update Test", "key": "UPD"},
            headers=auth_headers
        )
        project_id = create_resp.json()["project"]["id"]

        response = client.put(
            f"/api/v1/projects/{project_id}",
            params={"name": "Updated Name", "description": "New description"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["project"]["name"] == "Updated Name"

    def test_delete_project(self, client, db_session, test_user, auth_headers):
        """测试删除项目"""
        # 创建项目
        create_resp = client.post(
            "/api/v1/projects",
            params={"name": "Delete Test", "key": "DEL"},
            headers=auth_headers
        )
        project_id = create_resp.json()["project"]["id"]

        response = client.delete(f"/api/v1/projects/{project_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Project deleted successfully"

        # 验证项目已删除
        get_resp = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
        assert get_resp.status_code == 404


class TestProjectMemberAPI:
    """项目成员管理API测试"""

    def test_get_project_members(self, client, db_session, test_user, auth_headers):
        """测试获取项目成员"""
        # 创建项目
        create_resp = client.post(
            "/api/v1/projects",
            params={"name": "Members Test", "key": "MEMB"},
            headers=auth_headers
        )
        project_id = create_resp.json()["project"]["id"]

        response = client.get(f"/api/v1/projects/{project_id}/members", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1  # 创建者是成员

    def test_add_member(self, client, db_session, test_user, other_user, auth_headers):
        """测试添加项目成员"""
        # 创建项目
        create_resp = client.post(
            "/api/v1/projects",
            params={"name": "Add Member Test", "key": "ADDMEM"},
            headers=auth_headers
        )
        project_id = create_resp.json()["project"]["id"]

        response = client.post(
            f"/api/v1/projects/{project_id}/members",
            params={"user_id": other_user.id},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["member"]["user_id"] == other_user.id

    def test_add_duplicate_member(self, client, db_session, test_user, auth_headers):
        """测试添加重复成员"""
        # 创建项目
        create_resp = client.post(
            "/api/v1/projects",
            params={"name": "Dup Member Test", "key": "DUPMEM"},
            headers=auth_headers
        )
        project_id = create_resp.json()["project"]["id"]

        # 添加成员两次
        client.post(
            f"/api/v1/projects/{project_id}/members",
            params={"user_id": test_user.id},
            headers=auth_headers
        )

        response = client.post(
            f"/api/v1/projects/{project_id}/members",
            params={"user_id": test_user.id},
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "already a member" in response.json()["detail"]

    def test_remove_member(self, client, db_session, test_user, other_user, auth_headers):
        """测试移除项目成员"""
        # 创建项目
        create_resp = client.post(
            "/api/v1/projects",
            params={"name": "Remove Member Test", "key": "REMMEM"},
            headers=auth_headers
        )
        project_id = create_resp.json()["project"]["id"]

        # 添加成员
        client.post(
            f"/api/v1/projects/{project_id}/members",
            params={"user_id": other_user.id},
            headers=auth_headers
        )

        # 移除成员
        response = client.delete(
            f"/api/v1/projects/{project_id}/members/{other_user.id}",
            headers=auth_headers
        )
        assert response.status_code == 200


class TestMilestoneAPI:
    """项目里程碑API测试"""

    def test_create_milestone(self, client, db_session, test_user, auth_headers):
        """测试创建里程碑"""
        # 创建项目
        create_resp = client.post(
            "/api/v1/projects",
            params={"name": "Milestone Test", "key": "MILES"},
            headers=auth_headers
        )
        project_id = create_resp.json()["project"]["id"]

        response = client.post(
            f"/api/v1/projects/{project_id}/milestones",
            params={"name": "v1.0 Release", "description": "First release"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["milestone"]["name"] == "v1.0 Release"

    def test_get_milestones(self, client, db_session, test_user, auth_headers):
        """测试获取里程碑列表"""
        # 创建项目
        create_resp = client.post(
            "/api/v1/projects",
            params={"name": "Get Miles Test", "key": "GETMIL"},
            headers=auth_headers
        )
        project_id = create_resp.json()["project"]["id"]

        # 创建里程碑
        client.post(
            f"/api/v1/projects/{project_id}/milestones",
            params={"name": "Milestone 1"},
            headers=auth_headers
        )

        response = client.get(f"/api/v1/projects/{project_id}/milestones", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1
