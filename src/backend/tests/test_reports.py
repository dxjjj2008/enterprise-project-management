"""
报表统计 API 测试
"""


class TestReportsAPI:
    """报表统计 API 测试类"""

    def test_get_core_stats(self, client, db_session, test_user, auth_headers, test_project):
        """测试获取核心统计数据"""
        response = client.get("/api/v1/reports/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # API returns overview wrapped in "overview" key
        assert "overview" in data or "project_total" in data

    def test_get_project_rankings(self, client, db_session, test_user, auth_headers):
        """测试获取项目排名"""
        response = client.get("/api/v1/reports/project-rank", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_get_task_statistics(self, client, db_session, test_user, auth_headers):
        """测试获取任务统计"""
        response = client.get("/api/v1/reports/task-stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or "by_status" in data

    def test_get_resource_utilization(self, client, db_session, test_user, auth_headers):
        """测试获取资源利用率"""
        response = client.get("/api/v1/reports/resource-usage", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_get_export_report(self, client, db_session, test_user, auth_headers):
        """测试导出报表"""
        response = client.get(
            "/api/v1/reports/export",
            headers=auth_headers,
            params={"report_type": "projects", "format": "xlsx"}
        )
        assert response.status_code == 200

    def test_get_report_templates(self, client, db_session, test_user, auth_headers):
        """测试获取报表模板"""
        response = client.get("/api/v1/reports/templates", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_get_project_timeline(self, client, db_session, test_user, auth_headers):
        """测试获取项目时间线"""
        response = client.get("/api/v1/reports/timeline", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_get_burndown_chart(self, client, db_session, test_user, auth_headers):
        """测试获取燃尽图数据"""
        response = client.get(
            "/api/v1/reports/burndown",
            headers=auth_headers,
            params={"project_id": 1}
        )
        assert response.status_code == 200

    def test_get_workload_distribution(self, client, db_session, test_user, auth_headers):
        """测试获取工作量分布"""
        response = client.get("/api/v1/reports/workload", headers=auth_headers)
        assert response.status_code == 200
