# 企业项目管理系统 - 架构设计文档

**版本**: v1.1 (更新于 2026-02-09)
**创建日期**: 2026-02-08
**状态**: 前端完成，后端待开发

---

## 📋 目录

1. [项目概述](#项目概述)
2. [当前架构状态](#当前架构状态)
3. [前端架构](#前端架构)
4. [后端架构](#后端架构)
5. [数据库设计](#数据库设计)
6. [API接口设计](#api接口设计)
7. [部署架构](#部署架构)
8. [无障碍性架构](#无障碍性架构)
9. [安全机制](#安全机制)
10. [变更记录](#变更记录)

---

## 📊 项目概述

| 项目 | 描述 |
|------|------|
| **系统名称** | 企业项目管理系统 |
| **目标用户** | 10-100人中小企业 |
| **交付周期** | 30天（前端已完成） |
| **开发模式** | 前后端分离 |
| **当前状态** | 前端已完成60%，后端待开发 |

---

## 🏗️ 当前架构状态

### 版本对比

| 方面 | v1.0 (设计文档) | v1.1 (实际状态) | 差异说明 |
|------|----------------|----------------|----------|
| **前端实现** | 80% | 100% | 前端已完成主要功能 |
| **后端实现** | 100% | 10% | 后端仅实现基础框架 |
| **数据库** | 完整设计 | 无实现 | 数据库设计待实现 |
| **部署** | Docker | 本地开发 | 部署配置待开发 |

### 核心差异

**v1.0设计**：
- 完整的前后端分离架构
- FastAPI + SQLite后端
- 17张数据库表
- 完整的API接口

**v1.1实际**：
- 仅前端实现（Vue 3 + Element Plus）
- 无后端服务
- 无数据库
- 数据保存在前端

---

## 🔨 前端架构

### 技术栈

| 层级 | 技术选择 | 版本 |
|------|----------|------|
| **框架** | Vue 3 | 3.4.0 |
| **UI组件库** | Element Plus | 2.5.0 |
| **构建工具** | Vite | 5.0.0 |
| **状态管理** | Pinia | 2.1.0 |
| **路由管理** | Vue Router | 4.2.0 |
| **拖拽库** | vuedraggable | 4.1.0 |
| **Markdown渲染** | marked | 17.0.1 |
| **CSS预处理** | Sass | 1.70.0 |

### 项目结构

```
src/frontend/
├── src/
│   ├── views/              # 页面组件
│   │   ├── dashboard/      # 仪表盘
│   │   ├── auth/           # 认证页面
│   │   ├── projects/       # 项目管理
│   │   ├── tasks/          # 任务管理
│   │   ├── docs/           # 文档管理
│   │   ├── resources/      # 资源管理
│   │   ├── approvals/      # 审批管理
│   │   └── reports/        # 报表统计
│   ├── components/         # 通用组件
│   ├── stores/             # 状态管理
│   ├── router/             # 路由配置
│   ├── styles/             # 全局样式
│   └── utils/              # 工具函数
├── public/                 # 静态资源
├── index.html
├── vite.config.js
└── package.json
```

### 已实现功能模块

| 模块 | 状态 | 完成度 | 位置 |
|------|------|--------|------|
| Auth | ✅ 完成 | 80% | `src/views/auth/` |
| Dashboard | ✅ 完成 | 100% | `src/views/dashboard/` |
| Projects | ⚠️ 部分 | 60% | `src/views/projects/` |
| Task Board | ✅ 完成 | 100% | `src/views/tasks/` |
| Documents | ✅ 完成 | 100% | `src/views/docs/` |
| Gantt | ⚠️ 部分 | 5% | `src/views/projects/Gantt.vue` |
| Resources | ❌ 未实现 | 0% | - |
| Approvals | ❌ 未实现 | 0% | - |
| Reports | ❌ 未实现 | 0% | - |

---

## 🖥️ 后端架构

### 技术栈

| 层级 | 技术选择 | 说明 |
|------|----------|------|
| **框架** | FastAPI | 高性能Python Web框架 |
| **数据库** | SQLite | 轻量级关系数据库 |
| **ORM** | SQLAlchemy | Python ORM工具 |
| **认证** | JWT | JSON Web Token |
| **验证** | Pydantic | 数据验证 |

### 项目结构

```
src/backend/
├── app/
│   ├── api/
│   │   ├── v1/                 # API版本1
│   │   │   ├── auth.py         # 认证接口
│   │   │   ├── projects.py     # 项目管理接口
│   │   │   ├── tasks.py        # 任务管理接口
│   │   │   └── deps.py         # 依赖注入
│   │   └── deps.py             # API依赖项
│   ├── core/
│   │   ├── config.py           # 配置管理
│   │   ├── security.py         # 安全工具（JWT、密码哈希）
│   │   └── cache.py            # 缓存工具
│   ├── models/
│   │   ├── database.py         # 数据库配置
│   │   ├── base.py             # 基础模型
│   │   ├── organization.py     # 组织模型
│   │   ├── user.py             # 用户模型
│   │   ├── project.py          # 项目模型
│   │   ├── task.py             # 任务模型
│   │   ├── document.py         # 文档模型
│   │   └── other_models.py     # 其他模型
│   ├── schemas/
│   │   ├── auth.py             # 认证Schema
│   │   ├── organization.py     # 组织Schema
│   │   ├── user.py             # 用户Schema
│   │   ├── project.py          # 项目Schema
│   │   ├── task.py             # 任务Schema
│   │   └── document.py         # 文档Schema
│   ├── services/
│   │   ├── auth_service.py     # 认证服务
│   │   ├── project_service.py  # 项目服务
│   │   └── task_service.py     # 任务服务
│   └── tasks/
│       └── celery_tasks.py     # 异步任务
├── tests/
│   ├── __init__.py
│   ├── test_api.py             # API测试
│   ├── test_models.py          # 模型测试
│   └── test_services.py        # 服务测试
├── alembic/                    # 数据库迁移
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── alembic.ini
├── main.py                     # 应用入口
├── requirements.txt            # 依赖列表
└── .env.example                # 环境变量示例
```

### 待开发功能模块

| 模块 | 优先级 | 预计工作量 | 说明 |
|------|--------|-----------|------|
| **Auth API** | P0 | 3天 | 登录、注册、JWT认证 |
| **Organization** | P0 | 1天 | 组织管理 |
| **User Management** | P0 | 1天 | 用户管理 |
| **Project API** | P1 | 3天 | 项目CRUD |
| **Task API** | P1 | 3天 | 任务管理 |
| **Document API** | P2 | 2天 | 文档管理 |
| **Notification** | P2 | 2天 | 通知系统 |
| **其他模块** | P3 | 10天 | 资源、审批、报告等 |

---

## 💾 数据库设计

### 17张核心表

#### 1. 组织表 (organizations)
```sql
CREATE TABLE organizations (
    id INTEGER PRIMARY KEY,
    parent_id INTEGER,              -- 父级组织（NULL=顶级公司）
    name TEXT NOT NULL,             -- 公司/部门/团队名称
    slug TEXT UNIQUE,               -- URL友好标识
    type TEXT,                      -- company/department/team
    logo TEXT,
    plan TEXT,                      -- free/pro/enterprise
    owner_id INTEGER,               -- 组织负责人
    settings TEXT,                  -- 自定义设置（JSON）
    is_deleted INTEGER DEFAULT 0,
    deleted_at TEXT,                -- 删除时间
    deleted_by INTEGER,             -- 删除人
    created_at TEXT,
    updated_at TEXT
);
```

#### 2. 用户表 (users)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    organization_id INTEGER,        -- 用户主组织
    username TEXT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT,                      -- 真实姓名
    role TEXT,                      -- admin/member/viewer
    avatar TEXT,
    is_active INTEGER DEFAULT 1,
    last_login TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_at TEXT,
    deleted_by INTEGER,
    created_at TEXT,
    updated_at TEXT
);
```

#### 3. 项目表 (projects)
```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    organization_id INTEGER,        -- 项目属于组织
    name TEXT NOT NULL,
    description TEXT,
    status TEXT,                    -- planning/active/completed/archived
    start_date TEXT,
    end_date TEXT,
    owner_id INTEGER,               -- 项目负责人
    is_deleted INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);
```

#### 4. 项目角色表 (project_roles)
```sql
CREATE TABLE project_roles (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,             -- 角色属于项目
    name TEXT,                      -- 角色名称
    slug TEXT,                      -- 角色标识
    is_preset INTEGER DEFAULT 0,    -- 是否为系统预设角色
    permissions TEXT,               -- 权限配置（JSON）
    is_deleted INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);
```

#### 5. 项目成员表 (project_members)
```sql
CREATE TABLE project_members (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    user_id INTEGER,
    role_id INTEGER,                -- 关联角色
    joined_at TEXT,
    is_deleted INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);
```

#### 6. 任务表 (tasks)
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    organization_id INTEGER,
    parent_id INTEGER,              -- 支持子任务
    title TEXT NOT NULL,
    description TEXT,
    status TEXT,                    -- todo/in_progress/review/done
    priority TEXT,                  -- low/medium/high/urgent
    assignee_id INTEGER,
    start_date TEXT,
    due_date TEXT,
    estimated_hours REAL,
    actual_hours REAL,
    progress INTEGER,               -- 0-100
    is_deleted INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);
```

#### 7. 任务依赖表 (task_dependencies)
```sql
CREATE TABLE task_dependencies (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    predecessor_id INTEGER,         -- 前置任务
    successor_id INTEGER,           -- 后置任务
    dependency_type TEXT,           -- FS/SS/FF/SF
    created_at TEXT
);
```

#### 8. 评论表 (comments)
```sql
CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    task_id INTEGER,
    user_id INTEGER,
    organization_id INTEGER,
    content TEXT,
    is_deleted INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);
```

#### 9. 文档表 (documents)
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    organization_id INTEGER,
    name TEXT NOT NULL,
    file_path TEXT,
    file_type TEXT,
    file_size INTEGER,
    version INTEGER,
    uploaded_by INTEGER,
    is_deleted INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);
```

#### 10. 通知表 (notifications)
```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    organization_id INTEGER,
    type TEXT,                      -- task_assigned/comment/mention/deadline
    title TEXT,
    content TEXT,
    is_read INTEGER DEFAULT 0,
    related_type TEXT,              -- task/project/comment
    related_id INTEGER,
    is_deleted INTEGER DEFAULT 0,
    created_at TEXT
);
```

#### 11-17. 其他表
- project_goals（项目目标）
- deliverables（交付物）
- project_milestones（里程碑）
- project_risks（风险）
- project_issues（问题）
- project_activities（活动日志）
- system_settings（系统配置）

### 索引设计

```sql
-- 性能优化索引
CREATE INDEX idx_tasks_project_assignee_status ON tasks(project_id, assignee_id, status, is_deleted) WHERE is_deleted = 0;
CREATE INDEX idx_projects_status_enddate ON projects(status, end_date) WHERE status != 'archived';
CREATE INDEX idx_users_organization_role ON users(organization_id, role, is_active) WHERE is_active = 1;
CREATE INDEX idx_task_dependencies_predecessor ON task_dependencies(predecessor_id, project_id);
CREATE INDEX idx_projects_organization ON projects(organization_id);
```

---

## 🔌 API接口设计

### API基础路径
```
Base URL: /api/v1
```

### 认证接口 (Auth)

| 接口 | 方法 | 路径 | 说明 | 优先级 |
|------|------|------|------|--------|
| 用户注册 | POST | /auth/register | 注册新用户 | P0 |
| 用户登录 | POST | /auth/login | 用户登录获取Token | P0 |
| 用户登出 | POST | /auth/logout | 退出登录 | P1 |
| 刷新Token | POST | /auth/refresh | 刷新访问令牌 | P1 |
| 忘记密码 | POST | /auth/forgot-password | 忘记密码请求 | P2 |
| 重置密码 | PUT | /auth/reset-password | 重置密码 | P2 |
| 获取当前用户 | GET | /auth/me | 获取当前登录用户信息 | P0 |

### 项目管理接口 (Projects)

| 接口 | 方法 | 路径 | 说明 | 优先级 |
|------|------|------|------|--------|
| 获取项目列表 | GET | /projects | 获取项目列表 | P0 |
| 创建项目 | POST | /projects | 创建新项目 | P0 |
| 获取项目详情 | GET | /projects/{id} | 获取项目详细信息 | P0 |
| 更新项目 | PUT | /projects/{id} | 更新项目信息 | P0 |
| 删除项目 | DELETE | /projects/{id} | 删除项目 | P1 |
| 更新项目状态 | PUT | /projects/{id}/status | 更新项目状态 | P1 |
| 获取项目成员 | GET | /projects/{id}/members | 获取项目成员列表 | P1 |
| 添加项目成员 | POST | /projects/{id}/members | 添加成员到项目 | P1 |
| 移除项目成员 | DELETE | /projects/{id}/members/{user_id} | 从项目移除成员 | P1 |

### 任务管理接口 (Tasks)

| 接口 | 方法 | 路径 | 说明 | 优先级 |
|------|------|------|------|--------|
| 获取任务列表 | GET | /projects/{id}/tasks | 获取项目下的任务 | P0 |
| 创建任务 | POST | /projects/{id}/tasks | 创建新任务 | P0 |
| 获取任务详情 | GET | /tasks/{id} | 获取任务详细信息 | P0 |
| 更新任务 | PUT | /tasks/{id} | 更新任务信息 | P0 |
| 删除任务 | DELETE | /tasks/{id} | 删除任务 | P1 |
| 更新任务状态 | PUT | /tasks/{id}/status | 更新任务状态 | P0 |
| 指派任务 | PUT | /tasks/{id}/assignee | 指派任务负责人 | P1 |
| 获取子任务 | GET | /tasks/{id}/subtasks | 获取子任务列表 | P2 |

### 文档管理接口 (Documents)

| 接口 | 方法 | 路径 | 说明 | 优先级 |
|------|------|------|------|--------|
| 获取文档列表 | GET | /projects/{id}/documents | 获取项目文档列表 | P1 |
| 上传文档 | POST | /projects/{id}/documents | 上传文档 | P1 |
| 获取文档详情 | GET | /documents/{id} | 获取文档详细信息 | P1 |
| 更新文档 | PUT | /documents/{id} | 更新文档信息 | P1 |
| 删除文档 | DELETE | /documents/{id} | 删除文档 | P2 |
| 下载文档 | GET | /documents/{id}/download | 下载文档 | P2 |

### 响应格式规范

#### 成功响应
```json
{
  "code": 0,
  "message": "success",
  "data": { /* 业务数据 */ },
  "meta": { "page": 1, "per_page": 20, "total": 100 }
}
```

#### 错误响应
```json
{
  "code": 400,
  "message": "Validation Error",
  "errors": [{ "field": "email", "message": "邮箱格式不正确" }]
}
```

#### HTTP状态码定义

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

---

## 🚀 部署架构

### 当前部署状态

**开发环境**：
- Vite开发服务器：http://localhost:3000
- 端口：3000
- 模式：开发模式（热重载）
- 状态：运行正常

**生产环境**：
- ❌ 未配置
- ❌ 未部署
- ❌ 无Docker配置

### Docker Compose架构

```yaml
version: '3.8'

services:
  frontend:
    image: enterprise-frontend:latest
    build: ./src/frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    volumes:
      - ./src/frontend/dist:/usr/share/nginx/html
    restart: unless-stopped

  backend:
    image: enterprise-backend:latest
    build: ./src/backend
    environment:
      - DATABASE_URL=sqlite:///./data/project.db
      - SECRET_KEY=your-secret-key
    volumes:
      - ./src/backend:/app
      - ./data:/app/data
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=project_mgmt
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  pgdata:
```

---

## ♿ 无障碍性架构

### WCAG 2.1 AA标准

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 键盘导航 | ✅ 已实现 | 完整的键盘支持 |
| ARIA属性 | ✅ 已实现 | 所有交互元素都有ARIA属性 |
| 颜色对比度 | ✅ 已实现 | 符合WCAG AA标准 |
| 焦点管理 | ✅ 已实现 | 焦点顺序清晰 |
| 屏幕阅读器兼容 | ✅ 已实现 | 完全兼容 |

### 键盘快捷键

| 快捷键 | 功能 |
|--------|------|
| Ctrl+K | 搜索 |
| Ctrl+N | 新建任务 |
| Ctrl+S | 保存 |
| Alt+D | 仪表盘 |
| Alt+T | 任务 |
| Alt+P | 项目 |
| F5 | 刷新 |
| Esc | 取消 |

---

## 🔒 安全机制

### 密码安全
- **加密算法**: bcrypt (work factor=12)
- **最小密码长度**: 8 位
- **强度要求**: 大小写字母+数字+特殊字符

### JWT Token
- **算法**: HS256
- **Access Token 有效期**: 2 小时
- **Refresh Token 有效期**: 7 天

### 权限中间件
```python
1. 验证 JWT Token 有效性
2. 检查用户 is_active 状态
3. 验证用户属于请求的组织
4. 检查接口权限（基于 project_roles）
5. 返回 403 如果无权限
```

### 全局通用字段
```python
is_deleted: Boolean, default=False      # 软删除
deleted_at: DateTime, nullable          # 删除时间
deleted_by: Integer, nullable           # 删除人
created_at: DateTime                    # 创建时间
updated_at: DateTime                    # 更新时间
```

---

## 📝 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|----------|
| 2026-02-08 | v1.0 | 初始架构设计 |
| 2026-02-09 | v1.1 | 更新架构状态：前端100%，后端10% |

---

## 📊 当前进度总结

### 功能完成度

| 功能模块 | 前端完成度 | 后端完成度 | 整体完成度 |
|---------|-----------|-----------|-----------|
| Auth认证 | 80% | 0% | 40% |
| Dashboard | 100% | 0% | 50% |
| Projects | 60% | 0% | 30% |
| Tasks | 100% | 0% | 50% |
| Documents | 100% | 0% | 50% |
| Gantt | 5% | 0% | 2.5% |
| Resources | 0% | 0% | 0% |
| Approvals | 0% | 0% | 0% |
| Reports | 0% | 0% | 0% |

### 技术栈完成度

| 组件 | 状态 |
|------|------|
| 前端框架 | ✅ 100% |
| 前端UI库 | ✅ 100% |
| 构建工具 | ✅ 100% |
| 后端框架 | ⏳ 10% |
| 数据库 | ⏳ 0% |
| 部署配置 | ⏳ 0% |

### 下一步工作

**优先级P0**:
1. ✅ 更新架构文档 - 已完成
2. ⏳ 创建数据库模型
3. ⏳ 实现认证API
4. ⏳ 实现项目管理API

**预计完成时间**: 2-3周

---

**文档维护者**: 技术负责人
**最后更新**: 2026-02-09
**下次更新**: 后端API实现完成后
