# 企业项目管理系统 - 任务API测试
"""
任务管理和协作API测试用例
"""

import pytest
from fastapi.testclient import TestClient

from app.models import User, Project, Task, TaskStatus, TaskPriority


class TestTaskAPI:
    """任务API测试类"""

    def test_create_task(self, client, db_session, test_user, auth_headers, test_project):
        """测试创建任务"""
        response = client.post(
            f"/api/v1/projects/{test_project.id}/tasks",
            params={
                "title": "Test Task",
                "description": "A test task",
                "priority": "high"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Task created successfully"
        assert data["task"]["title"] == "Test Task"
        assert data["task"]["status"] == "todo"
        assert data["task"]["priority"] == "high"

    def test_create_task_with_assignee(self, client, db_session, test_user, other_user, auth_headers, test_project):
        """测试创建任务并指派成员"""
        # 先将 other_user 添加为项目成员
        client.post(
            f"/api/v1/projects/{test_project.id}/members",
            params={"user_id": other_user.id},
            headers=auth_headers
        )

        response = client.post(
            f"/api/v1/projects/{test_project.id}/tasks",
            params={
                "title": "Assigned Task",
                "assignee_id": other_user.id
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["task"]["assignee_id"] == other_user.id

    def test_get_tasks(self, client, db_session, test_user, auth_headers, test_project):
        """测试获取任务列表"""
        # 创建任务
        client.post(
            f"/api/v1/projects/{test_project.id}/tasks",
            params={"title": "Task 1"},
            headers=auth_headers
        )
        client.post(
            f"/api/v1/projects/{test_project.id}/tasks",
            params={"title": "Task 2"},
            headers=auth_headers
        )

        response = client.get(f"/api/v1/projects/{test_project.id}/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 2

    def test_get_tasks_with_filter(self, client, db_session, test_user, auth_headers, test_project):
        """测试过滤任务列表"""
        # 创建不同优先级的任务
        client.post(
            f"/api/v1/projects/{test_project.id}/tasks",
            params={"title": "High Priority Task", "priority": "high"},
            headers=auth_headers
        )
        client.post(
            f"/api/v1/projects/{test_project.id}/tasks",
            params={"title": "Low Priority Task", "priority": "low"},
            headers=auth_headers
        )

        # 过滤高优先级
        response = client.get(
            f"/api/v1/projects/{test_project.id}/tasks",
            params={"priority": "high"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        for task in data["items"]:
            assert task["priority"] == "high"

    def test_get_task_detail(self, client, db_session, test_user, auth_headers, test_project):
        """测试获取任务详情"""
        # 创建任务
        create_resp = client.post(
            f"/api/v1/projects/{test_project.id}/tasks",
            params={"title": "Detail Task"},
            headers=auth_headers
        )
        task_id = create_resp.json()["task"]["id"]

        response = client.get(
            f"/api/v1/projects/{test_project.id}/tasks/{task_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["task"]["title"] == "Detail Task"
        assert "subtasks" in data
        assert "comments" in data
        assert "labels" in data

    def test_update_task(self, client, db_session, test_user, auth_headers, test_project):
        """测试更新任务"""
        # 创建任务
        create_resp = client.post(
            f"/api/v1/projects/{test_project.id}/tasks",
            params={"title": "Update Test Task"},
            headers=auth_headers
        )
        task_id = create_resp.json()["task"]["id"]

        response = client.put(
            f"/api/v1/projects/{test_project.id}/tasks/{task_id}",
            params={"title": "Updated Title", "status": "in_progress"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["task"]["title"] == "Updated Title"
        assert data["task"]["status"] == "in_progress"

    def test_complete_task(self, client, db_session, test_user, auth_headers, test_project):
        """测试完成任务"""
        # 创建任务
        create_resp = client.post(
            f"/api/v1/projects/{test_project.id}/tasks",
            params={"title": "Complete Test"},
            headers=auth_headers
        )
        task_id = create_resp.json()["task"]["id"]

        response = client.put(
            f"/api/v1/projects/{test_project.id}/tasks/{task_id}",
            params={"status": "done"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["task"]["status"] == "done"

    def test_delete_task(self, client, db_session, test_user, auth_headers, test_project):
        """测试删除任务"""
        # 创建任务
        create_resp = client.post(
            f"/api/v1/projects/{test_project.id}/tasks",
            params={"title": "Delete Test"},
            headers=auth_headers
        )
        task_id = create_resp.json()["task"]["id"]

        response = client.delete(
            f"/api/v1/projects/{test_project.id}/tasks/{task_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Task deleted successfully"

        # 验证任务已删除
        get_resp = client.get(
            f"/api/v1/projects/{test_project.id}/tasks/{task_id}",
            headers=auth_headers
        )
        assert get_resp.status_code == 404

    def test_create_subtask(self, client, db_session, test_user, auth_headers, test_project):
        """测试创建子任务"""
        # 创建父任务
        parent_resp = client.post(
            f"/api/v1/projects/{test_project.id}/tasks",
            params={"title": "Parent Task"},
            headers=auth_headers
        )
        parent_id = parent_resp.json()["task"]["id"]

        # 创建子任务
        response = client.post(
            f"/api/v1/projects/{test_project.id}/tasks",
            params={"title": "Subtask", "parent_id": parent_id},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["task"]["parent_id"] == parent_id


class TestTaskCommentAPI:
    """任务评论API测试"""

    def test_add_comment(self, client, db_session, test_user, auth_headers, test_project):
        """测试添加评论"""
        # 创建任务
        task_resp = client.post(
            f"/api/v1/projects/{test_project.id}/tasks",
            params={"title": "Task for Comment"},
            headers=auth_headers
        )
        task_id = task_resp.json()["task"]["id"]

        response = client.post(
            f"/api/v1/projects/{test_project.id}/tasks/{task_id}/comments",
            params={"content": "This is a test comment"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["comment"]["content"] == "This is a test comment"

    def test_get_comments(self, client, db_session, test_user, auth_headers, test_project):
        """测试获取评论列表"""
        # 创建任务
        task_resp = client.post(
            f"/api/v1/projects/{test_project.id}/tasks",
            params={"title": "Task for Comments"},
            headers=auth_headers
        )
        task_id = task_resp.json()["task"]["id"]

        # 添加评论
        client.post(
            f"/api/v1/projects/{test_project.id}/tasks/{task_id}/comments",
            params={"content": "Comment 1"},
            headers=auth_headers
        )
        client.post(
            f"/api/v1/projects/{test_project.id}/tasks/{task_id}/comments",
            params={"content": "Comment 2"},
            headers=auth_headers
        )

        response = client.get(
            f"/api/v1/projects/{test_project.id}/tasks/{task_id}/comments",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2


class TestTaskLabelAPI:
    """任务标签API测试"""

    def test_create_label(self, client, db_session, test_user, auth_headers, test_project):
        """测试创建标签"""
        response = client.post(
            f"/api/v1/projects/{test_project.id}/labels",
            params={"name": "Bug", "color": "#ff0000"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["label"]["name"] == "Bug"
        assert data["label"]["color"] == "#ff0000"

    def test_get_labels(self, client, db_session, test_user, auth_headers, test_project):
        """测试获取标签列表"""
        # 创建标签
        client.post(
            f"/api/v1/projects/{test_project.id}/labels",
            params={"name": "Feature"},
            headers=auth_headers
        )

        response = client.get(f"/api/v1/projects/{test_project.id}/labels", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1
