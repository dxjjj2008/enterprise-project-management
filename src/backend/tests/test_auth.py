# 企业项目管理系统 - 认证API测试
"""
认证接口测试用例
"""

import pytest
from fastapi.testclient import TestClient

from app.models import User, UserRole


class TestAuthAPI:
    """认证API测试类"""
    
    def test_health_check(self, client):
        """测试健康检查接口"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
    
    def test_root_endpoint(self, client):
        """测试根路径接口"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "企业项目管理系统 API"
        assert "version" in data
        assert "status" in data
    
    def test_register_user(self, client, db_session):
        """测试用户注册"""
        response = client.post(
            "/api/v1/auth/register",
            data={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "newpassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User registered successfully"
        assert data["user"]["username"] == "newuser"
        assert data["user"]["email"] == "newuser@example.com"
    
    def test_register_duplicate_user(self, client, db_session, test_user):
        """测试重复用户注册"""
        response = client.post(
            "/api/v1/auth/register",
            data={
                "username": test_user.username,
                "email": "another@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_login_success(self, client, db_session, test_user):
        """测试成功登录"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.username,
                "password": "testpassword"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == test_user.username
    
    def test_login_wrong_password(self, client, db_session, test_user):
        """测试错误密码登录"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.username,
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_get_current_user(self, client, db_session, test_user, auth_headers):
        """测试获取当前用户信息"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["role"] == test_user.role.value
    
    def test_get_current_user_unauthorized(self, client):
        """测试未授权访问"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    def test_refresh_token(self, client, db_session, test_user, auth_headers):
        """测试刷新令牌"""
        response = client.post("/api/v1/auth/refresh", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_update_current_user(self, client, db_session, test_user, auth_headers):
        """测试更新用户信息"""
        response = client.put(
            "/api/v1/auth/me",
            params={"full_name": "Updated Name"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["full_name"] == "Updated Name"
    
    def test_change_password(self, client, db_session, test_user, auth_headers):
        """测试更改密码"""
        response = client.post(
            "/api/v1/auth/change-password",
            data={
                "old_password": "testpassword",
                "new_password": "newpassword123"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Password changed successfully"
    
    def test_change_password_wrong_old(self, client, db_session, test_user, auth_headers):
        """测试错误旧密码更改密码"""
        response = client.post(
            "/api/v1/auth/change-password",
            data={
                "old_password": "wrongpassword",
                "new_password": "newpassword123"
            },
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "Incorrect old password" in response.json()["detail"]
