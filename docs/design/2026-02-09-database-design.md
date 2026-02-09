# 数据库设计文档

**版本**: v1.1
**创建日期**: 2026-02-09
**状态**: 设计完成，待实现

---

## 📋 目录

1. [数据库概述](#数据库概述)
2. [ER图](#er图)
3. [表设计](#表设计)
4. [索引设计](#索引设计)
5. [迁移计划](#迁移计划)
6. [使用指南](#使用指南)

---

## 🗄️ 数据库概述

### 数据库类型
- **类型**: SQLite
- **大小**: 轻量级，适合单机部署
- **并发**: 适合中小型应用
- **维护**: 无需数据库服务器

### 数据库配置
```python
# 数据库URL
DATABASE_URL = "sqlite:///./data/project_management.db"

# 数据库位置
PROJECT_DIR = "./data"
DATABASE_FILE = "project_management.db"
```

### 数据库初始化
```python
# 初始化脚本
import sqlite3
import os

def init_database():
    """初始化数据库和表结构"""

    # 确保数据库目录存在
    os.makedirs("./data", exist_ok=True)

    # 连接数据库
    conn = sqlite3.connect("./data/project_management.db")
    cursor = conn.cursor()

    # 创建表
    create_tables(cursor)

    # 插入初始数据
    insert_initial_data(cursor)

    # 提交更改
    conn.commit()

    # 关闭连接
    conn.close()

    print("✅ 数据库初始化完成")
```

---

## 📊 ER图

```
┌─────────────────┐       ┌─────────────────┐
│   organizations │       │      users      │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ parent_id (FK)  │───────│ organization_id │
│ name            │       │ username        │
│ slug            │       │ email           │
│ type            │       │ password_hash   │
│ logo            │       │ name            │
│ plan            │       │ role            │
│ owner_id (FK)   │       │ avatar          │
│ settings        │       │ is_active       │
│ is_deleted      │       │ is_deleted      │
│ created_at      │       │ created_at      │
└─────────────────┘       └─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│    projects     │       │  project_roles  │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ organization_id │───────│ project_id      │
│ name            │       │ name            │
│ description     │       │ slug            │
│ status          │       │ is_preset       │
│ start_date      │       │ permissions     │
│ end_date        │       │ is_deleted      │
│ owner_id        │       │ created_at      │
│ is_deleted      │       │ updated_at      │
│ created_at      │       └─────────────────┘
└─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│ project_members │       │     tasks       │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ project_id      │───────│ project_id      │
│ user_id         │       │ organization_id │
│ role_id         │       │ parent_id       │
│ joined_at       │       │ title           │
│ is_deleted      │       │ description     │
│ created_at      │       │ status          │
└─────────────────┘       │ priority        │
                          │ assignee_id     │
                          │ start_date      │
                          │ end_date        │
                          │ estimated_hours │
                          │ actual_hours    │
                          │ progress        │
                          │ is_deleted      │
                          │ created_at      │
                          └─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│ task_dependencies│───────│    comments     │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ project_id      │       │ task_id         │
│ predecessor_id  │───────│ user_id         │
│ successor_id    │       │ organization_id │
│ dependency_type │       │ content         │
│ created_at      │       │ is_deleted      │
└─────────────────┘       │ created_at      │
                          └─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│  documents      │       │  notifications  │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ project_id      │       │ user_id         │
│ organization_id │───────│ organization_id │
│ name            │       │ type            │
│ file_path       │       │ title           │
│ file_type       │       │ content         │
│ file_size       │       │ is_read         │
│ version         │       │ related_type    │
│ uploaded_by     │       │ related_id      │
│ is_deleted      │       │ is_deleted      │
│ created_at      │       │ created_at      │
└─────────────────┘       └─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│ project_goals   │       │ deliverables    │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ project_id      │       │ project_id      │
│ organization_id │       │ organization_id │
│ title           │       │ name            │
│ description     │       │ description     │
│ metrics         │       │ type            │
│ target_date     │       │ version         │
│ status          │       │ status          │
│ progress        │       │ due_date        │
│ is_deleted      │       │ delivered_at    │
│ created_at      │       │ reviewed_by     │
└─────────────────┘       │ reviewed_at     │
                          │ review_comment  │
                          │ file_id         │
                          │ created_by      │
                          │ is_deleted      │
                          │ created_at      │
                          └─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│project_milestones│     │  project_risks  │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ project_id      │       │ project_id      │
│ organization_id │       │ organization_id │
│ name            │       │ title           │
│ description     │       │ description     │
│ planned_date    │       │ category        │
│ actual_date     │       │ probability     │
│ status          │       │ impact          │
│ completion_rate │       │ risk_level      │
│ is_deleted      │       │ status          │
│ created_at      │       │ mitigation      │
└─────────────────┘       │ owner_id        │
                          │ identified_date │
                          │ occurred_date    │
                          │ closed_date     │
                          │ is_deleted      │
                          │ created_at      │
                          └─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│ project_issues  │       │project_activities│
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ project_id      │       │ project_id      │
│ organization_id │       │ organization_id │
│ task_id (FK)    │───────│ user_id         │
│ title           │       │ action          │
│ description     │       │ entity_type     │
│ type            │       │ entity_id       │
│ priority        │       │ old_value       │
│ status          │       │ new_value       │
│ assignee_id     │       │ ip_address      │
│ due_date        │       │ created_at      │
│ resolved_at     │       └─────────────────┘
│ resolution      │
│ closed_by       │
│ closed_at       │
│ created_by      │
│ is_deleted      │
│ created_at      │
└─────────────────┘

┌─────────────────┐
│ system_settings │
├─────────────────┤
│ id (PK)         │
│ organization_id │
│ key             │
│ value           │
│ type            │
│ description     │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

---

## 📝 表设计

### 1. 组织表 (organizations)

**说明**: 存储公司、部门、团队等组织结构

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | INTEGER | 是 | - | 主键 |
| parent_id | INTEGER | 否 | NULL | 父级组织 |
| name | TEXT | 是 | - | 组织名称 |
| slug | TEXT | 是 | - | URL友好标识 |
| type | TEXT | 否 | - | company/department/team |
| logo | TEXT | 否 | NULL | Logo URL |
| plan | TEXT | 否 | - | free/pro/enterprise |
| owner_id | INTEGER | 否 | NULL | 组织负责人 |
| settings | TEXT | 否 | NULL | 自定义设置（JSON） |
| is_deleted | INTEGER | 是 | 0 | 软删除标志 |
| deleted_at | TEXT | 否 | NULL | 删除时间 |
| deleted_by | INTEGER | 否 | NULL | 删除人ID |
| created_at | TEXT | 是 | - | 创建时间 |
| updated_at | TEXT | 是 | - | 更新时间 |

**索引**:
```sql
CREATE INDEX idx_organizations_parent ON organizations(parent_id) WHERE parent_id IS NOT NULL;
CREATE INDEX idx_organizations_slug ON organizations(slug) WHERE is_deleted = 0;
CREATE INDEX idx_organizations_owner ON organizations(owner_id);
```

**示例数据**:
```sql
INSERT INTO organizations (id, parent_id, name, slug, type, plan, owner_id, settings, is_deleted, created_at, updated_at)
VALUES
(1, NULL, 'XX科技有限公司', 'xx-tech', 'company', 'enterprise', 1, '{"company_code": "XT001"}', 0, datetime('now'), datetime('now')),
(2, 1, '研发部', 'rd-dept', 'department', 'enterprise', 1, '{"department_code": "RD001"}', 0, datetime('now'), datetime('now'));
```

---

### 2. 用户表 (users)

**说明**: 存储系统用户信息

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | INTEGER | 是 | - | 主键 |
| organization_id | INTEGER | 是 | - | 所属组织 |
| username | TEXT | 是 | - | 用户名 |
| email | TEXT | 是 | - | 邮箱（唯一） |
| password_hash | TEXT | 是 | - | 密码哈希 |
| name | TEXT | 否 | - | 真实姓名 |
| role | TEXT | 否 | 'member' | 角色类型 |
| avatar | TEXT | 否 | NULL | 头像URL |
| is_active | INTEGER | 是 | 1 | 激活状态 |
| last_login | TEXT | 否 | NULL | 最后登录时间 |
| is_deleted | INTEGER | 是 | 0 | 软删除标志 |
| deleted_at | TEXT | 否 | NULL | 删除时间 |
| deleted_by | INTEGER | 否 | NULL | 删除人ID |
| created_at | TEXT | 是 | - | 创建时间 |
| updated_at | TEXT | 是 | - | 更新时间 |

**索引**:
```sql
CREATE INDEX idx_users_organization ON users(organization_id, is_active) WHERE is_active = 1;
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

**示例数据**:
```sql
INSERT INTO users (id, organization_id, username, email, password_hash, name, role, avatar, is_active, created_at, updated_at)
VALUES
(1, 1, 'admin', 'admin@xx-tech.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5D5qK5qK5qK5q', '系统管理员', 'admin', NULL, 1, datetime('now'), datetime('now')),
(2, 1, 'zhangsan', 'zhangsan@xx-tech.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5D5qK5qK5qK5q', '张三', 'manager', NULL, 1, datetime('now'), datetime('now')),
(3, 1, 'lisi', 'lisi@xx-tech.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5D5qK5qK5qK5q', '李四', 'member', NULL, 1, datetime('now'), datetime('now'));
```

---

### 3. 项目表 (projects)

**说明**: 存储项目信息

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | INTEGER | 是 | - | 主键 |
| organization_id | INTEGER | 是 | - | 所属组织 |
| name | TEXT | 是 | - | 项目名称 |
| description | TEXT | 否 | - | 项目描述 |
| status | TEXT | 否 | 'planning' | 项目状态 |
| start_date | TEXT | 否 | NULL | 开始日期 |
| end_date | TEXT | 否 | NULL | 结束日期 |
| owner_id | INTEGER | 否 | - | 项目负责人 |
| is_deleted | INTEGER | 是 | 0 | 软删除标志 |
| created_at | TEXT | 是 | - | 创建时间 |
| updated_at | TEXT | 是 | - | 更新时间 |

**索引**:
```sql
CREATE INDEX idx_projects_organization ON projects(organization_id);
CREATE INDEX idx_projects_status_enddate ON projects(status, end_date) WHERE status != 'archived';
CREATE INDEX idx_projects_owner ON projects(owner_id);
```

**示例数据**:
```sql
INSERT INTO projects (id, organization_id, name, description, status, start_date, end_date, owner_id, is_deleted, created_at, updated_at)
VALUES
(1, 1, '企业项目管理系统V1.0', '开发企业级项目管理平台', 'active', '2026-01-01', '2026-03-31', 1, 0, datetime('now'), datetime('now')),
(2, 1, '移动端APP开发', 'iOS和Android应用开发', 'planning', '2026-04-01', '2026-06-30', 1, 0, datetime('now'), datetime('now'));
```

---

### 4. 项目角色表 (project_roles)

**说明**: 定义项目角色和权限

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | INTEGER | 是 | - | 主键 |
| project_id | INTEGER | 是 | - | 所属项目 |
| name | TEXT | 是 | - | 角色名称 |
| slug | TEXT | 是 | - | 角色标识 |
| is_preset | INTEGER | 是 | 0 | 是否为预设角色 |
| permissions | TEXT | 否 | NULL | 权限配置（JSON） |
| is_deleted | INTEGER | 是 | 0 | 软删除标志 |
| created_at | TEXT | 是 | - | 创建时间 |
| updated_at | TEXT | 是 | - | 更新时间 |

**预设角色**:

| 角色标识 | 角色名称 | 权限 |
|---------|---------|------|
| project_manager | 项目经理 | 全部权限 |
| project_assistant | 项目助理 | 协助管理 |
| developer | 开发人员 | 普通权限 |
| tester | 测试人员 | 查看+报bug |
| viewer | 查看者 | 只读 |

**索引**:
```sql
CREATE INDEX idx_project_roles_project ON project_roles(project_id);
```

**示例数据**:
```sql
INSERT INTO project_roles (id, project_id, name, slug, is_preset, permissions, is_deleted, created_at, updated_at)
VALUES
(1, 1, '项目经理', 'project_manager', 1, '{"read": true, "write": true, "delete": true}', 0, datetime('now'), datetime('now')),
(2, 1, '开发人员', 'developer', 1, '{"read": true, "write": true, "delete": false}', 0, datetime('now'), datetime('now')),
(3, 1, '测试人员', 'tester', 1, '{"read": true, "write": false, "delete": false}', 0, datetime('now'), datetime('now'));
```

---

### 5. 项目成员表 (project_members)

**说明**: 记录项目成员及其角色

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | INTEGER | 是 | - | 主键 |
| project_id | INTEGER | 是 | - | 所属项目 |
| user_id | INTEGER | 是 | - | 用户ID |
| role_id | INTEGER | 是 | - | 角色ID |
| joined_at | TEXT | 是 | - | 加入时间 |
| is_deleted | INTEGER | 是 | 0 | 软删除标志 |
| created_at | TEXT | 是 | - | 创建时间 |
| updated_at | TEXT | 是 | - | 更新时间 |

**索引**:
```sql
CREATE INDEX idx_project_members_project ON project_members(project_id);
CREATE INDEX idx_project_members_user ON project_members(user_id);
```

---

### 6. 任务表 (tasks)

**说明**: 存储项目任务信息

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | INTEGER | 是 | - | 主键 |
| project_id | INTEGER | 是 | - | 所属项目 |
| organization_id | INTEGER | 是 | - | 所属组织 |
| parent_id | INTEGER | 否 | NULL | 父任务ID（支持子任务） |
| title | TEXT | 是 | - | 任务标题 |
| description | TEXT | 否 | - | 任务描述 |
| status | TEXT | 是 | 'todo' | 任务状态 |
| priority | TEXT | 否 | 'medium' | 优先级 |
| assignee_id | INTEGER | 否 | NULL | 任务负责人 |
| start_date | TEXT | 否 | NULL | 开始日期 |
| due_date | TEXT | 否 | NULL | 截止日期 |
| estimated_hours | REAL | 否 | 0 | 预估工时 |
| actual_hours | REAL | 否 | 0 | 实际工时 |
| progress | INTEGER | 否 | 0 | 进度百分比 |
| is_deleted | INTEGER | 是 | 0 | 软删除标志 |
| created_at | TEXT | 是 | - | 创建时间 |
| updated_at | TEXT | 是 | - | 更新时间 |

**索引**:
```sql
CREATE INDEX idx_tasks_project_assignee_status ON tasks(project_id, assignee_id, status, is_deleted) WHERE is_deleted = 0;
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX idx_tasks_parent ON tasks(parent_id) WHERE parent_id IS NOT NULL;
```

**任务状态**:
- `todo`: 待办
- `in_progress`: 进行中
- `review`: 审核中
- `done`: 已完成

**优先级**:
- `low`: 低
- `medium`: 中
- `high`: 高
- `urgent`: 紧急

**示例数据**:
```sql
INSERT INTO tasks (id, project_id, organization_id, parent_id, title, description, status, priority, assignee_id, start_date, due_date, estimated_hours, actual_hours, progress, is_deleted, created_at, updated_at)
VALUES
(1, 1, 1, NULL, '需求分析', '完成用户需求调研和分析', 'done', 'high', 2, '2026-01-01', '2026-01-15', 40, 35, 100, 0, datetime('now'), datetime('now')),
(2, 1, 1, NULL, '系统设计', '完成系统架构和数据库设计', 'in_progress', 'high', 2, '2026-01-16', '2026-02-15', 60, 45, 75, 0, datetime('now'), datetime('now')),
(3, 1, 1, 2, '前端开发', 'Vue3前端开发', 'in_progress', 'high', 3, '2026-02-01', '2026-03-01', 80, 20, 25, 0, datetime('now'), datetime('now'));
```

---

### 7. 任务依赖表 (task_dependencies)

**说明**: 定义任务之间的依赖关系

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | INTEGER | 是 | - | 主键 |
| project_id | INTEGER | 是 | - | 所属项目 |
| predecessor_id | INTEGER | 是 | - | 前置任务ID |
| successor_id | INTEGER | 是 | - | 后置任务ID |
| dependency_type | TEXT | 是 | 'FS' | 依赖类型 |
| created_at | TEXT | 是 | - | 创建时间 |

**依赖类型**:
- `FS` (Finish-to-Start): 前置完成才能开始后置
- `SS` (Start-to-Start): 前置开始才能开始后置
- `FF` (Finish-to-Finish): 前置完成才能完成后置
- `SF` (Start-to-Finish): 前置开始才能完成后置

**索引**:
```sql
CREATE INDEX idx_task_dependencies_predecessor ON task_dependencies(predecessor_id, project_id);
CREATE INDEX idx_task_dependencies_successor ON task_dependencies(successor_id, project_id);
```

---

### 8. 评论表 (comments)

**说明**: 存储任务评论信息

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | INTEGER | 是 | - | 主键 |
| task_id | INTEGER | 是 | - | 关联任务 |
| user_id | INTEGER | 是 | - | 评论人 |
| organization_id | INTEGER | 是 | - | 所属组织 |
| content | TEXT | 是 | - | 评论内容 |
| is_deleted | INTEGER | 是 | 0 | 软删除标志 |
| created_at | TEXT | 是 | - | 创建时间 |
| updated_at | TEXT | 是 | - | 更新时间 |

**索引**:
```sql
CREATE INDEX idx_comments_task ON comments(task_id);
CREATE INDEX idx_comments_user ON comments(user_id);
```

---

### 9. 文档表 (documents)

**说明**: 存储项目文档信息

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | INTEGER | 是 | - | 主键 |
| project_id | INTEGER | 是 | - | 所属项目 |
| organization_id | INTEGER | 是 | - | 所属组织 |
| name | TEXT | 是 | - | 文档名称 |
| file_path | TEXT | 否 | - | 文件路径 |
| file_type | TEXT | 否 | - | 文件类型 |
| file_size | INTEGER | 否 | 0 | 文件大小（字节） |
| version | INTEGER | 否 | 1 | 版本号 |
| uploaded_by | INTEGER | 是 | - | 上传人 |
| is_deleted | INTEGER | 是 | 0 | 软删除标志 |
| created_at | TEXT | 是 | - | 创建时间 |
| updated_at | TEXT | 是 | - | 更新时间 |

**索引**:
```sql
CREATE INDEX idx_documents_project ON documents(project_id);
CREATE INDEX idx_documents_upload ON documents(uploaded_by);
```

---

### 10. 通知表 (notifications)

**说明**: 存储用户通知信息

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | INTEGER | 是 | - | 主键 |
| user_id | INTEGER | 是 | - | 接收用户 |
| organization_id | INTEGER | 是 | - | 所属组织 |
| type | TEXT | 是 | - | 通知类型 |
| title | TEXT | 是 | - | 通知标题 |
| content | TEXT | 否 | - | 通知内容 |
| is_read | INTEGER | 是 | 0 | 已读状态 |
| related_type | TEXT | 否 | - | 关联类型 |
| related_id | INTEGER | 否 | - | 关联ID |
| is_deleted | INTEGER | 是 | 0 | 软删除标志 |
| created_at | TEXT | 是 | - | 创建时间 |

**通知类型**:
- `task_assigned`: 任务分配
- `comment`: 任务评论
- `mention`: @提及
- `deadline`: 截止日期提醒
- `project_update`: 项目更新

**索引**:
```sql
CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);
CREATE INDEX idx_notifications_related ON notifications(related_type, related_id);
```

---

### 11-17. 其他表

#### 11. 项目目标表 (project_goals)
```sql
CREATE TABLE project_goals (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    organization_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    metrics TEXT,              -- JSON格式
    target_date TEXT,
    status TEXT,               -- pending/in_progress/achieved/cancelled
    progress INTEGER,          -- 0-100
    is_deleted INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);
```

#### 12. 交付物表 (deliverables)
```sql
CREATE TABLE deliverables (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    organization_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT,                 -- document/code/design/report/sample
    version TEXT,
    status TEXT,               -- pending/in_review/approved/rejected
    due_date TEXT,
    delivered_at TEXT,
    reviewed_by INTEGER,
    reviewed_at TEXT,
    review_comment TEXT,
    file_id INTEGER,
    created_by INTEGER,
    is_deleted INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);
```

#### 13. 里程碑表 (project_milestones)
```sql
CREATE TABLE project_milestones (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    organization_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    planned_date TEXT,
    actual_date TEXT,
    status TEXT,               -- upcoming/in_progress/completed/delayed
    completion_rate INTEGER,   -- 0-100
    is_deleted INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);
```

#### 14. 风险表 (project_risks)
```sql
CREATE TABLE project_risks (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    organization_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,             -- technical/resource/schedule/external
    probability INTEGER,       -- 1-5
    impact INTEGER,            -- 1-5
    risk_level INTEGER,        -- 1-25 (probability × impact)
    status TEXT,               -- identified/mitigated/occurred/closed
    mitigation TEXT,
    owner_id INTEGER,
    identified_date TEXT,
    occurred_date TEXT,
    closed_date TEXT,
    is_deleted INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);
```

#### 15. 问题表 (project_issues)
```sql
CREATE TABLE project_issues (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    organization_id INTEGER,
    task_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    type TEXT,                 -- bug/question/improvement
    priority TEXT,             -- low/medium/high/critical
    status TEXT,               -- open/in_progress/resolved/closed
    assignee_id INTEGER,
    due_date TEXT,
    resolved_at TEXT,
    resolution TEXT,
    closed_by INTEGER,
    closed_at TEXT,
    created_by INTEGER,
    is_deleted INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);
```

#### 16. 活动日志表 (project_activities)
```sql
CREATE TABLE project_activities (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    organization_id INTEGER,
    user_id INTEGER,
    action TEXT,               -- create/update/delete/status_change
    entity_type TEXT,          -- task/project/member/deliverable
    entity_id INTEGER,
    old_value TEXT,            -- JSON格式
    new_value TEXT,            -- JSON格式
    ip_address TEXT,
    created_at TEXT
);
```

#### 17. 系统配置表 (system_settings)
```sql
CREATE TABLE system_settings (
    id INTEGER PRIMARY KEY,
    organization_id INTEGER,   -- NULL=全局配置
    key TEXT NOT NULL,
    value TEXT,
    type TEXT,                 -- string/integer/json/list/boolean
    description TEXT,
    created_at TEXT,
    updated_at TEXT
);

-- 全局配置索引
CREATE UNIQUE INDEX idx_settings_global_key ON system_settings(organization_id, key);
```

---

## 🔍 索引设计

### 性能优化索引

```sql
-- 组织表索引
CREATE INDEX idx_organizations_parent ON organizations(parent_id) WHERE parent_id IS NOT NULL;
CREATE UNIQUE INDEX idx_organizations_slug ON organizations(slug) WHERE is_deleted = 0;
CREATE INDEX idx_organizations_owner ON organizations(owner_id);

-- 用户表索引
CREATE INDEX idx_users_organization ON users(organization_id, is_active) WHERE is_active = 1;
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- 项目表索引
CREATE INDEX idx_projects_organization ON projects(organization_id);
CREATE INDEX idx_projects_status_enddate ON projects(status, end_date) WHERE status != 'archived';
CREATE INDEX idx_projects_owner ON projects(owner_id);

-- 任务表索引
CREATE INDEX idx_tasks_project_assignee_status ON tasks(project_id, assignee_id, status, is_deleted) WHERE is_deleted = 0;
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX idx_tasks_parent ON tasks(parent_id) WHERE parent_id IS NOT NULL;

-- 任务依赖索引
CREATE INDEX idx_task_dependencies_predecessor ON task_dependencies(predecessor_id, project_id);
CREATE INDEX idx_task_dependencies_successor ON task_dependencies(successor_id, project_id);

-- 评论索引
CREATE INDEX idx_comments_task ON comments(task_id);
CREATE INDEX idx_comments_user ON comments(user_id);

-- 文档索引
CREATE INDEX idx_documents_project ON documents(project_id);
CREATE INDEX idx_documents_upload ON documents(uploaded_by);

-- 通知索引
CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);
CREATE INDEX idx_notifications_related ON notifications(related_type, related_id);

-- 系统配置索引
CREATE UNIQUE INDEX idx_settings_global_key ON system_settings(organization_id, key);
```

---

## 🔄 迁移计划

### 初始化迁移 (2026-02-09)

```python
# alembic/versions/20260209_init_database.py

from alembic import op
import sqlalchemy as sa

def upgrade():
    # 创建所有表
    op.create_table('organizations', ...)
    op.create_table('users', ...)
    op.create_table('projects', ...)
    op.create_table('project_roles', ...)
    op.create_table('project_members', ...)
    op.create_table('tasks', ...)
    op.create_table('task_dependencies', ...)
    op.create_table('comments', ...)
    op.create_table('documents', ...)
    op.create_table('notifications', ...)
    op.create_table('project_goals', ...)
    op.create_table('deliverables', ...)
    op.create_table('project_milestones', ...)
    op.create_table('project_risks', ...)
    op.create_table('project_issues', ...)
    op.create_table('project_activities', ...)
    op.create_table('system_settings', ...)

    # 创建索引
    op.create_index('idx_organizations_parent', 'organizations', ['parent_id'])
    # ... 其他索引

    # 插入初始数据
    insert_initial_data()

def downgrade():
    # 删除表
    op.drop_table('system_settings')
    # ... 其他表
```

---

## 📖 使用指南

### 基础CRUD操作

#### 创建组织
```python
def create_organization(conn, name, slug, owner_id):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO organizations (name, slug, owner_id)
        VALUES (?, ?, ?)
    """, (name, slug, owner_id))
    conn.commit()
    return cursor.lastrowid
```

#### 创建用户
```python
def create_user(conn, organization_id, email, password_hash, name, role='member'):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (organization_id, email, password_hash, name, role)
        VALUES (?, ?, ?, ?, ?)
    """, (organization_id, email, password_hash, name, role))
    conn.commit()
    return cursor.lastrowid
```

#### 创建项目
```python
def create_project(conn, organization_id, name, description, owner_id):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO projects (organization_id, name, description, owner_id, status)
        VALUES (?, ?, ?, ?, 'planning')
    """, (organization_id, name, description, owner_id))
    conn.commit()
    return cursor.lastrowid
```

#### 创建任务
```python
def create_task(conn, project_id, organization_id, title, assignee_id):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (project_id, organization_id, title, assignee_id, status, priority)
        VALUES (?, ?, ?, ?, 'todo', 'medium')
    """, (project_id, organization_id, title, assignee_id))
    conn.commit()
    return cursor.lastrowid
```

---

## 🔒 安全建议

1. **密码加密**: 使用bcrypt算法加密密码
2. **SQL注入防护**: 使用参数化查询
3. **数据验证**: 使用Pydantic进行数据验证
4. **权限控制**: 实现基于角色的访问控制
5. **数据备份**: 定期备份数据库文件

---

**文档维护者**: 数据库工程师
**最后更新**: 2026-02-09
**文档版本**: v1.1
