# 后端测试框架配置

**版本**: v1.0  
**创建日期**: 2026-02-09  
**状态**: 待配置

---

## 1. 技术栈

| 工具 | 版本 | 用途 |
|------|------|------|
| **pytest** | ^8.0.0 | Python 测试框架 |
| **pytest-asyncio** | ^0.24.0 | 异步测试支持 |
| **httpx** | ^0.27.0 | HTTP 客户端 |
| **SQLAlchemy** | ^2.0.0 | ORM 测试 |

---

## 2. 安装

```bash
cd backend
python -m pip install pytest pytest-asyncio httpx
```

---

## 3. 目录结构

```
backend/
├── app/
│   ├── main.py
│   ├── routers/
│   │   ├── auth.py
│   │   └── auth_test.py      ← 测试文件
│   └── models/
│       └── user_test.py
└── tests/
    ├── conftest.py           ← pytest 配置
    ├── test_auth.py
    ├── test_projects.py
    └── test_tasks.py
```

---

## 4. 快速开始

### 4.1 创建 conftest.py

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """测试客户端"""
    return TestClient(app)

@pytest.fixture
def auth_token():
    """获取测试令牌"""
    # TODO: 实现登录逻辑
    return "test_token"
```

### 4.2 创建测试文件

```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient

def test_health_check():
    """健康检查测试"""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_login():
    """登录测试"""
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "test@example.com",
            "password": "test123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

---

## 5. 运行测试

```bash
# 运行所有测试
pytest

# 运行并显示详细信息
pytest -v

# 运行指定文件
pytest tests/test_auth.py

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

---

## 6. 相关文档

- [测试指南](../testing/2026-02-09-testing-guide.md)
- [API 接口文档](../api/2026-02-08-api.md)
- [后端 API 计划](../plans/2026-02-08-backend-api-plan.md)
