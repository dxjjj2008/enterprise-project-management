# 测试框架配置指南

**版本**: v1.0  
**创建日期**: 2026-02-09  
**状态**: 已配置

---

## 1. 技术栈

### 1.1 前端测试

| 工具 | 版本 | 用途 |
|------|------|------|
| **Vitest** | ^2.0.0 | 单元测试框架 |
| **@vue/test-utils** | ^2.4.0 | Vue 3 测试工具库 |
| **happy-dom** | ^14.0.0 | 轻量级 DOM 模拟（比 jsdom 更快） |

### 1.2 后端测试

| 工具 | 版本 | 用途 |
|------|------|------|
| **pytest** | ^8.0.0 | Python 测试框架 |
| **pytest-asyncio** | ^0.24.0 | 异步测试支持 |
| **httpx** | ^0.27.0 | HTTP 客户端测试 |

---

## 2. 前端测试配置

### 2.1 安装命令

```bash
cd src/frontend
npm install -D vitest @vue/test-utils happy-dom
```

### 2.2 配置文件

创建 `vite.config.js` 测试配置：

```javascript
/// <reference types="vitest" />
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  test: {
    globals: true,
    environment: 'happy-dom',
    include: ['**/*.test.{js,ts,jsx,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        '.eslintrc.js',
        'vite.config.js'
      ]
    }
  }
})
```

### 2.3 package.json 脚本

```json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage"
  }
}
```

---

## 3. 后端测试配置

### 3.1 安装命令

```bash
cd backend
python -m pip install pytest pytest-asyncio httpx
```

### 3.2 配置文件

创建 `pytest.ini`：

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

### 3.3 conftest.py

创建 `tests/conftest.py`：

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """测试客户端"""
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    """认证请求头（需要先登录）"""
    # TODO: 实现登录获取 token
    return {"Authorization": "Bearer test_token"}
```

---

## 4. 测试用例规范

### 4.1 前端测试示例

**测试文件位置**: `src/**/*.test.js`

```javascript
// components/HelloWorld.test.js
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import HelloWorld from './HelloWorld.vue'

describe('HelloWorld', () => {
  it('renders properly', () => {
    const wrapper = mount(HelloWorld, {
      props: { msg: 'Hello Vitest' }
    })
    expect(wrapper.text()).toContain('Hello Vitest')
  })
  
  it('has correct class', () => {
    const wrapper = mount(HelloWorld)
    expect(wrapper.classes()).toContain('hello')
  })
})
```

### 4.2 后端测试示例

**测试文件位置**: `tests/test_auth.py`

```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient

def test_login_success():
    """测试正常登录"""
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

def test_login_invalid_password():
    """测试密码错误"""
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "test@example.com",
            "password": "wrong_password"
        }
    )
    assert response.status_code == 401
```

---

## 5. 测试目录结构

### 5.1 前端测试目录

```
src/
├── components/
│   ├── HelloWorld.vue
│   └── HelloWorld.test.js    ← 测试文件
├── views/
│   ├── Dashboard/
│   │   ├── Index.vue
│   │   └── Index.test.js
│   └── projects/
│       ├── List.vue
│       └── List.test.js
└── stores/
    ├── auth.js
    └── auth.test.js
```

### 5.2 后端测试目录

```
backend/
├── app/
│   ├── routers/
│   │   ├── auth.py
│   │   └── auth_test.py
│   └── models/
│       └── user_test.py
└── tests/
    ├── conftest.py
    ├── test_auth.py
    ├── test_projects.py
    └── test_tasks.py
```

---

## 6. 测试覆盖率要求

### 6.1 覆盖率目标

| 模块 | 最低覆盖率 |
|------|-----------|
| 核心业务逻辑 | 80% |
| API 接口 | 90% |
| 工具函数 | 70% |
| 整体项目 | 75% |

### 6.2 运行覆盖率报告

```bash
# 前端
npm run test:coverage

# 后端
pytest --cov=app --cov-report=html
```

---

## 7. CI/CD 集成

### 7.1 GitHub Actions

创建 `.github/workflows/test.yml`：

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          
      - name: Install dependencies
        run: npm ci
        working-directory: ./src/frontend
        
      - name: Run frontend tests
        run: npm run test:run
        working-directory: ./src/frontend
        
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Run backend tests
        run: pytest
        working-directory: ./backend
```

---

## 8. 最佳实践

### 8.1 编写测试原则

1. **测试行为，而非实现**
   ```javascript
   // ❌ 错误：测试实现细节
   expect(wrapper.vm.count).toBe(0)
   
   // ✅ 正确：测试用户可见的行为
   expect(wrapper.text()).toContain('Count: 0')
   ```

2. **保持测试独立**
   - 每个测试应该能够独立运行
   - 使用 `beforeEach` 重置状态

3. **使用有意义的测试名**
   ```python
   # ❌ 错误
   def test_1():
       ...
   
   # ✅ 正确
   def test_login_with_valid_credentials_returns_token():
       ...
   ```

4. **遵循 AAA 模式**
   - **Arrange**: 准备测试数据
   - **Act**: 执行被测函数
   - **Assert**: 验证结果

### 8.2 测试数据管理

- 使用工厂模式创建测试数据
- 避免硬编码的测试数据
- 使用 `fixture` 复用测试数据

---

## 9. 常见问题

### Q1: Vitest找不到测试文件？
确保 `vite.config.js` 中配置了 `include` 路径：
```javascript
test: {
  include: ['**/*.test.{js,ts}']
}
```

### Q2: 异步测试失败？
使用 `async/await` 和 `vi.waitFor`：
```javascript
it('updates async', async () => {
  await wrapper.vm.fetchData()
  expect(wrapper.vm.data).toBeDefined()
})
```

### Q3: 后端测试数据库？
使用测试数据库或内存数据库：
```python
@pytest.fixture
def test_db():
    # 使用 SQLite 内存数据库测试
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
```

---

## 10. 相关文档

- [开发计划](./plans/2026-02-08-development-plan.md)
- [后端 API 计划](./plans/2026-02-08-backend-api-plan.md)
- [API 接口文档](../api/2026-02-08-api.md)
