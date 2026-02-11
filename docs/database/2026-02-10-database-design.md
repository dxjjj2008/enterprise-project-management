# 数据库设计文档

**版本**: v1.0  
**更新日期**: 2026-02-10  
**数据库**: SQLite / PostgreSQL / MySQL

---

## 📊 数据库概览

| 表名 | 中文名 | 说明 | 状态 |
|------|--------|------|------|
| users | 用户表 | 系统用户信息 | ✅ 完整 |
| projects | 项目表 | 项目主数据 | ✅ 完整 |
| project_members | 项目成员表 | 项目-用户关联 | ✅ 完整 |
| milestones | 里程碑表 | 项目里程碑 | ⚠️ 待完善 |
| tasks | 任务表 | 任务主数据 | ✅ 完整 |
| comments | 评论表 | 任务评论 | ✅ 完整 |
| attachments | 附件表 | 任务附件 | ✅ 完整 |
| labels | 标签表 | 任务标签 | ✅ 完整 |
| task_labels | 任务标签关联表 | 多对多关系 | ✅ 完整 |

---

## 🔍 详细表结构

### 1. 用户表 (users)

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  full_name VARCHAR(100),
  phone VARCHAR(20),
  avatar VARCHAR(500),
  role VARCHAR(20) DEFAULT 'member',
  is_active BOOLEAN DEFAULT TRUE,
  is_superuser BOOLEAN DEFAULT FALSE,
  created_at DATETIME,
  updated_at DATETIME,
  last_login DATETIME
);
```

| 字段 | 类型 | 说明 | 建议 |
|------|------|------|------|
| id | Integer | 主键 | ✅ |
| username | String(50) | 用户名 | ✅ |
| email | String(100) | 邮箱 | ✅ |
| hashed_password | String(255) | 加密密码 | ✅ |
| full_name | String(100) | 真实姓名 | ✅ |
| phone | String(20) | 电话 | ✅ 可选 |
| avatar | String(500) | 头像URL | ✅ |
| role | Enum | 角色 | ✅ |
| is_active | Boolean | 是否激活 | ✅ |
| is_superuser | Boolean | 超级管理员 | ✅ |
| created_at | DateTime | 创建时间 | ✅ |
| updated_at | DateTime | 更新时间 | ✅ |
| last_login | DateTime | 最后登录 | ✅ |

**优化建议**:
- ⭐ 添加 `department` 部门字段（资源分配需要）
- ⭐ 添加 `job_title` 职位字段
- ⭐ 添加 `skills` 技能字段（JSON格式）

---

### 2. 项目表 (projects)

```sql
CREATE TABLE projects (
  id INTEGER PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  description TEXT,
  key VARCHAR(10) UNIQUE NOT NULL,  -- 项目标识
  status VARCHAR(20) DEFAULT 'planning',
  owner_id INTEGER REFERENCES users(id),
  start_date DATETIME,
  end_date DATETIME,
  created_at DATETIME,
  updated_at DATETIME,
  is_deleted BOOLEAN DEFAULT FALSE
);
```

| 字段 | 类型 | 说明 | 建议 |
|------|------|------|------|
| id | Integer | 主键 | ✅ |
| name | String(200) | 项目名称 | ✅ |
| description | Text | 项目描述 | ✅ |
| key | String(10) | 项目标识 | ✅ |
| status | Enum | 状态 | ✅ |
| owner_id | Integer | 负责人ID | ✅ |
| start_date | DateTime | 开始日期 | ✅ |
| end_date | DateTime | 结束日期 | ✅ |
| created_at | DateTime | 创建时间 | ✅ |
| updated_at | DateTime | 更新时间 | ✅ |
| is_deleted | Boolean | 软删除 | ✅ |

**优化建议**:
- ⭐ 添加 `budget` 预算字段
- ⭐ 添加 `currency` 币种字段
- ⭐ 添加 `progress` 进度字段（0-100）
- ⭐ 添加 `visibility` 可见性（公开/私密）
- ⭐ 添加 `category` 项目分类

---

### 3. 项目成员表 (project_members)

```sql
CREATE TABLE project_members (
  id INTEGER PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id),
  user_id INTEGER REFERENCES users(id),
  role VARCHAR(20) DEFAULT 'member',
  joined_at DATETIME,
  UNIQUE(project_id, user_id)
);
```

| 字段 | 类型 | 说明 | 建议 |
|------|------|------|------|
| id | Integer | 主键 | ✅ |
| project_id | Integer | 项目ID | ✅ |
| user_id | Integer | 用户ID | ✅ |
| role | Enum | 角色 | ✅ |
| joined_at | DateTime | 加入时间 | ✅ |

**优化建议**:
- ⭐ 添加 `joined_date` 加入日期（冗余，可删除）
- ⭐ 添加 `left_date` 离开日期
- ⭐ 添加 `workload` 工作量分配（百分比）
- ⭐ 添加 `hourly_rate` 时薪（成本核算）

---

### 4. 里程碑表 (milestones)

```sql
CREATE TABLE milestones (
  id INTEGER PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id),
  name VARCHAR(200) NOT NULL,
  description TEXT,
  due_date DATETIME,
  status VARCHAR(20) DEFAULT 'pending',
  completed_at DATETIME,
  created_at DATETIME
);
```

| 字段 | 类型 | 说明 | 建议 |
|------|------|------|------|
| id | Integer | 主键 | ✅ |
| project_id | Integer | 项目ID | ✅ |
| name | String(200) | 里程碑名称 | ✅ |
| description | Text | 描述 | ✅ |
| due_date | DateTime | 计划日期 | ✅ |
| status | String(20) | 状态 | ✅ 待完善 |
| completed_at | DateTime | 完成时间 | ✅ |
| created_at | DateTime | 创建时间 | ✅ |

**优化建议**:
- ⭐ `status` 改为 Enum 类型
- ⭐ 添加 `actual_date` 实际完成日期
- ⭐ 添加 `deliverables` 交付物（JSON）
- ⭐ 添加 `completed_by` 完成人ID
- ⭐ 添加 `order` 排序字段

---

### 5. 任务表 (tasks)

```sql
CREATE TABLE tasks (
  id INTEGER PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id),
  parent_id INTEGER REFERENCES tasks(id),  -- 父任务
  title VARCHAR(500) NOT NULL,
  description TEXT,
  status VARCHAR(20) DEFAULT 'todo',
  priority VARCHAR(20) DEFAULT 'medium',
  assignee_id INTEGER REFERENCES users(id),
  created_by_id INTEGER REFERENCES users(id),
  start_date DATETIME,
  due_date DATETIME,
  completed_at DATETIME,
  estimated_hours INTEGER,
  actual_hours INTEGER,
  progress INTEGER DEFAULT 0,
  created_at DATETIME,
  updated_at DATETIME,
  is_deleted BOOLEAN DEFAULT FALSE
);
```

| 字段 | 类型 | 说明 | 建议 |
|------|------|------|------|
| id | Integer | 主键 | ✅ |
| project_id | Integer | 项目ID | ✅ |
| parent_id | Integer | 父任务ID | ✅ |
| title | String(500) | 任务标题 | ✅ |
| description | Text | 描述 | ✅ |
| status | Enum | 状态 | ✅ |
| priority | Enum | 优先级 | ✅ |
| assignee_id | Integer | 指派人ID | ✅ |
| created_by_id | Integer | 创建人ID | ✅ |
| start_date | DateTime | 开始日期 | ✅ |
| due_date | DateTime | 截止日期 | ✅ |
| completed_at | DateTime | 完成时间 | ✅ |
| estimated_hours | Integer | 预估工时 | ✅ |
| actual_hours | Integer | 实际工时 | ✅ |
| progress | Integer | 进度 | ✅ |
| created_at | DateTime | 创建时间 | ✅ |
| updated_at | DateTime | 更新时间 | ✅ |
| is_deleted | Boolean | 软删除 | ✅ |

**优化建议**:
- ⭐ 添加 `task_number` 任务编号（如 T-001）
- ⭐ 添加 `task_type` 类型（任务/子任务/Bug/需求）
- ⭐ 添加 `severity` 严重程度（Bug专用）
- ⭐ 添加 `milestone_id` 关联里程碑
- ⭐ 添加 `blocked_by` 阻塞任务ID
- ⭐ 添加 `blocks` 被阻塞任务（JSON数组）
- ⭐ 添加 `is_milestone` 是否里程碑任务
- ⭐ 添加 `story_points` 故事点（敏捷）
- ⭐ 添加 `sprint_id` 关联Sprint

---

### 6. 评论表 (comments)

```sql
CREATE TABLE comments (
  id INTEGER PRIMARY KEY,
  task_id INTEGER REFERENCES tasks(id),
  author_id INTEGER REFERENCES users(id),
  content TEXT NOT NULL,
  created_at DATETIME,
  updated_at DATETIME,
  is_deleted BOOLEAN DEFAULT FALSE
);
```

**优化建议**:
- ⭐ 添加 `parent_id` 支持回复评论
- ⭐ 添加 `mention_ids` @提及用户（JSON）
- ⭐ 添加 `attachments` 附件列表（JSON）
- ⭐ 添加 `is_resolved` 是否已解决（针对问题类评论）

---

### 7. 附件表 (attachments)

```sql
CREATE TABLE attachments (
  id INTEGER PRIMARY KEY,
  task_id INTEGER REFERENCES tasks(id),
  filename VARCHAR(255) NOT NULL,
  file_path VARCHAR(500) NOT NULL,
  file_size INTEGER,
  file_type VARCHAR(100),
  uploaded_by_id INTEGER REFERENCES users(id),
  created_at DATETIME,
  is_deleted BOOLEAN DEFAULT FALSE
);
```

**优化建议**:
- ⭐ 添加 `file_category` 文件分类（文档/图片/代码/其他）
- ⭐ 添加 `description` 文件描述
- ⭐ 添加 `download_count` 下载次数
- ⭐ 添加 `thumbnail_path` 缩略图路径
- ⭐ 添加 `md5_hash` 文件MD5（去重）

---

### 8. 标签表 (labels)

```sql
CREATE TABLE labels (
  id INTEGER PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL,
  color VARCHAR(20) DEFAULT '#0079bf',
  project_id INTEGER REFERENCES projects(id),
  created_at DATETIME
);
```

**优化建议**:
- ⭐ 添加 `label_type` 标签类型（全局/项目）
- ⭐ 添加 `description` 标签描述
- ⭐ 添加 `icon` 标签图标
- ⭐ 添加 `sort_order` 排序

---

## 🎯 待新增的表

### 9. 审批流程表 (approvals)

```sql
CREATE TABLE approvals (
  id INTEGER PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id),
  type VARCHAR(50) NOT NULL,  -- approval_type: budget/change/milestone/deliverable
  title VARCHAR(200) NOT NULL,
  description TEXT,
  status VARCHAR(20) DEFAULT 'pending',  -- pending/approved/rejected
  applicant_id INTEGER REFERENCES users(id),
  approver_id INTEGER REFERENCES users(id),
  submitted_at DATETIME,
  decided_at DATETIME,
  comments TEXT,
  created_at DATETIME,
  updated_at DATETIME
);
```

### 10. 审批明细表 (approval_items)

```sql
CREATE TABLE approval_items (
  id INTEGER PRIMARY KEY,
  approval_id INTEGER REFERENCES approvals(id),
  item_type VARCHAR(50),  -- task/milestone/deliverable
  item_id INTEGER,
  old_value TEXT,
  new_value TEXT,
  created_at DATETIME
);
```

### 11. 工时记录表 (time_logs)

```sql
CREATE TABLE time_logs (
  id INTEGER PRIMARY KEY,
  task_id INTEGER REFERENCES tasks(id),
  user_id INTEGER REFERENCES users(id),
  date DATE NOT NULL,
  hours DECIMAL(4,2) NOT NULL,
  description TEXT,
  created_at DATETIME,
  updated_at DATETIME
);
```

### 12. 风险表 (risks)

```sql
CREATE TABLE risks (
  id INTEGER PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id),
  title VARCHAR(200) NOT NULL,
  description TEXT,
  probability VARCHAR(20),  -- high/medium/low
  impact VARCHAR(20),  -- high/medium/low
  status VARCHAR(20) DEFAULT 'identified',  -- identified/mitigated/occurred/closed
  mitigation TEXT,  -- 应对措施
  owner_id INTEGER REFERENCES users(id),
  identified_at DATETIME,
  due_date DATETIME,
  resolved_at DATETIME,
  created_at DATETIME,
  updated_at DATETIME
);
```

### 13. 问题表 (issues)

```sql
CREATE TABLE issues (
  id INTEGER PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id),
  task_id INTEGER REFERENCES tasks(id),
  title VARCHAR(200) NOT NULL,
  description TEXT,
  status VARCHAR(20) DEFAULT 'open',  -- open/in_progress/resolved/closed
  priority VARCHAR(20) DEFAULT 'medium',
  severity VARCHAR(20) DEFAULT 'normal',
  assignee_id INTEGER REFERENCES users(id),
  reported_by_id INTEGER REFERENCES users(id),
  due_date DATETIME,
  resolved_at DATETIME,
  created_at DATETIME,
  updated_at DATETIME
);
```

### 14. 资源分配表 (resource_allocations)

```sql
CREATE TABLE resource_allocations (
  id INTEGER PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  project_id INTEGER REFERENCES projects(id),
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  allocation_percent INTEGER DEFAULT 100,  -- 分配百分比
  role VARCHAR(50),
  notes TEXT,
  created_at DATETIME,
  updated_at DATETIME,
  UNIQUE(user_id, project_id, start_date)
);
```

---

## 📈 索引优化

建议添加以下索引：

```sql
-- tasks表索引
CREATE INDEX idx_tasks_project_status ON tasks(project_id, status);
CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_priority ON tasks(priority);

-- comments表索引
CREATE INDEX idx_comments_task ON comments(task_id);
CREATE INDEX idx_comments_author ON comments(author_id);

-- time_logs表索引
CREATE INDEX idx_time_logs_task_user_date ON time_logs(task_id, user_id, date);
```

---

## 🔗 关系图

```
users (用户)
  │
  ├── owned_projects (创建的项目)
  │
  ├── project_memberships (参与的项目)
  │    │
  │    └── project_members
  │         │
  │         └── projects (项目)
  │              │
  │              ├── milestones (里程碑)
  │              │
  │              ├── tasks (任务)
  │              │    ├── comments (评论)
  │              │    ├── attachments (附件)
  │              │    ├── task_labels (标签)
  │              │    └── time_logs (工时)
  │              │
  │              ├── risks (风险)
  │              │
  │              └── issues (问题)
  │
  ├── created_tasks (创建的任务)
  │
  └── assigned_tasks (指派的任务)
```

---

## 📝 下一步行动

| 优先级 | 任务 | 说明 |
|--------|------|------|
| P0 | 完善里程碑表 | 添加状态枚举、交付物等 |
| P0 | 新增审批流程表 | 支持审批流程 |
| P1 | 新增工时记录表 | 资源分配需要 |
| P1 | 新增风险表 | 项目风险管理 |
| P1 | 新增问题表 | 问题跟踪 |
| P2 | 新增资源分配表 | 人员调度 |
| P2 | 添加字段优化 | 预算、部门、职位等 |

---

**文档版本**: v1.0  
**最后更新**: 2026-02-10
