"""
计划管理 API 测试
"""
import pytest
from datetime import date


class TestPlanAPI:
    """计划管理 API 测试类"""

    def test_create_plan(self, client, db_session, test_user, auth_headers, test_project):
        """测试创建计划"""
        response = client.post(
            "/api/v1/plans",
            json={
                "name": "Q1 项目计划",
                "project_id": test_project.id,
                "description": "2024年第一季度项目实施计划",
                "start_date": "2024-01-01",
                "end_date": "2024-03-31"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Q1 项目计划"
        assert data["project_id"] == test_project.id

    def test_get_plans_list(self, client, db_session, test_user, auth_headers, test_plan):
        """测试获取计划列表"""
        response = client.get("/api/v1/plans", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_plan_detail(self, client, db_session, test_user, auth_headers, test_plan):
        """测试获取计划详情"""
        response = client.get(f"/api/v1/plans/{test_plan.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_plan.id

    def test_update_plan(self, client, db_session, test_user, auth_headers, test_plan):
        """测试更新计划"""
        response = client.put(
            f"/api/v1/plans/{test_plan.id}",
            json={"name": "更新后的计划名称"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "更新后的计划名称"

    def test_delete_plan(self, client, db_session, test_user, auth_headers, test_plan):
        """测试删除计划"""
        response = client.delete(f"/api/v1/plans/{test_plan.id}", headers=auth_headers)
        assert response.status_code == 200


class TestWBSTaskAPI:
    """WBS任务 API 测试类"""

    def test_get_wbs_tasks(self, client, db_session, test_user, auth_headers, test_plan):
        """测试获取WBS任务列表"""
        response = client.get(f"/api/v1/plans/{test_plan.id}/wbs", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_create_wbs_task(self, client, db_session, test_user, auth_headers, test_plan):
        """测试创建WBS任务"""
        response = client.post(
            f"/api/v1/plans/{test_plan.id}/wbs",
            json={
                "name": "需求分析",
                "level": 1,
                "planned_start": "2024-01-01",
                "planned_end": "2024-01-15",
                "planned_duration": 10,
                "progress": 0,
                "status": "pending"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "需求分析"

    def test_update_wbs_task(self, client, db_session, test_user, auth_headers, test_plan, test_wbs_task):
        """测试更新WBS任务"""
        response = client.put(
            f"/api/v1/plans/{test_plan.id}/wbs/{test_wbs_task.id}",
            json={"progress": 50, "status": "in_progress"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        # API returns simplified response
        assert data.get("progress") == 50

    def test_delete_wbs_task(self, client, db_session, test_user, auth_headers, test_plan, test_wbs_task):
        """测试删除WBS任务"""
        response = client.delete(f"/api/v1/plans/{test_plan.id}/wbs/{test_wbs_task.id}", headers=auth_headers)
        assert response.status_code == 200


class TestPlanMilestoneAPI:
    """计划里程碑 API 测试类"""

    def test_get_milestones(self, client, db_session, test_user, auth_headers, test_plan):
        """测试获取里程碑列表"""
        response = client.get(f"/api/v1/plans/{test_plan.id}/milestones", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data


class TestProjectListAPI:
    """项目列表 API 测试类"""

    def test_get_project_list(self, client, db_session, test_user, auth_headers, test_project):
        """测试获取项目列表（下拉框用）"""
        response = client.get("/api/v1/projects/list", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
