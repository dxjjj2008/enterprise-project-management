# 企业项目管理系统 - 设计方案

**版本**: v1.1  
**创建日期**: 2026-02-08  
**状态**: 设计阶段

---

## 1. 项目概述

| 项目 | 描述 |
|------|------|
| **系统名称** | 企业项目管理系统 |
| **目标用户** | 10-100人中小企业 |
| **交付周期** | 30天 |
| **开发模式** | 1人 + AI辅助 |
| **协作方式** | 前后端分离 |

---

## 2. 技术栈

| 层级 | 技术选择 |
|------|----------|
| **前端** | Vue 3 |
| **后端** | Python FastAPI |
| **数据库** | SQLite |
| **部署** | Docker + Docker Compose |
| **反向代理** | Nginx |

---

## 3. 系统架构

```
┌─────────────────────────────────────────────────────┐
│                  Docker Compose                     │
│                                                     │
│  ┌─────────────┐    ┌─────────────┐              │
│  │   Nginx      │    │  Vue3 SPA    │              │
│  │  (反向代理)   │    │  (静态资源)   │              │
│  └──────┬──────┘    └─────────────┘              │
│         │                                           │
│         ▼                                           │
│  ┌─────────────────────────────────┐               │
│  │        FastAPI 后端              │               │
│  │  - API 接口                      │               │
│  │  - 业务逻辑                      │               │
│  │  - JWT 认证                      │               │
│  └────────────┬────────────────────┘               │
│               │                                     │
│               ▼                                     │
│  ┌─────────────────────────────────┐               │
│  │         SQLite 数据库            │               │
│  │  (users, projects, tasks,       │               │
│  │   documents, comments, etc.)    │               │
│  └─────────────────────────────────┘               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 3.1 安全机制

### 密码安全
- **加密算法**: bcrypt (自动加盐，work factor=12)
- **最小密码长度**: 8 位
- **强度要求**: 需包含大小写字母+数字+特殊字符

### JWT Token
- **算法**: HS256
- **Access Token 有效期**: 2 小时
- **Refresh Token 有效期**: 7 天（存储在数据库）

### 权限中间件
```
1. 验证 JWT Token 有效性
2. 检查用户 is_active 状态
3. 验证用户属于请求的组织
4. 检查接口权限（基于 project_roles）
5. 返回 403 如果无权限
```

### 全局通用字段（所有表）
```
is_deleted: Boolean, default=False  [软删除]
deleted_at: DateTime, nullable      [删除时间]
deleted_by: Integer, nullable       [删除人]
created_at: DateTime
updated_at: DateTime
```

---

## 3.2 API 响应格式规范

### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": { /* 业务数据 */ },
  "meta": { "page": 1, "per_page": 20, "total": 100 }
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "Validation Error",
  "errors": [{ "field": "email", "message": "邮箱格式不正确" }]
}
```

### 状态码定义
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

## 4. 数据库设计

### 4.1 组织表 (organizations)
```
id: Integer, PK
parent_id: Integer, FK(organizations.id)  [父级组织，NULL=顶级公司]
name: String(100)                        [公司/部门/团队名称]
slug: String(50), 唯一                   [URL友好标识]
type: String(20)                         [company/department/team]
logo: String(255)
plan: String(20)                         [free/pro/enterprise]
owner_id: Integer, FK(users.id)          [组织负责人]
settings: JSON                            [自定义设置]
is_deleted: Boolean, default=False
created_at: DateTime
updated_at: DateTime
```

### 4.2 用户表 (users)
```
id: Integer, PK
organization_id: Integer, FK(organizations.id)  [用户主组织]
username: String(50)
email: String(100), 唯一
password_hash: String(255)
name: String(100)                               [真实姓名]
role: String(20)                                [admin/member/viewer]
avatar: String(255)
is_active: Boolean
last_login: DateTime
is_deleted: Boolean, default=False
created_at: DateTime
updated_at: DateTime
```

### 4.3 项目表 (projects)
```
id: Integer, PK
organization_id: Integer, FK(organizations.id)  [项目属于组织]
name: String(100)
description: Text
status: String(20)                               [planning/active/completed/archived]
start_date: Date
end_date: Date
owner_id: Integer, FK(users.id)                 [项目负责人]
is_deleted: Boolean, default=False
created_at: DateTime
updated_at: DateTime
```

### 4.4 项目角色表 (project_roles)
```
id: Integer, PK
project_id: Integer, FK(projects.id)            [角色属于项目]
name: String(50)                                [角色名称]
slug: String(50)                                [角色标识]
is_preset: Boolean                              [是否为系统预设角色]
permissions: JSON                               [权限配置]
is_deleted: Boolean, default=False
created_at: DateTime
updated_at: DateTime
```

**预设角色**：
| 角色标识 | 角色名称 | 权限 |
|---------|---------|------|
| project_manager | 项目经理 | 全权限 |
| project_assistant | 项目助理 | 协助管理 |
| developer | 开发人员 | 普通权限 |
| tester | 测试人员 | 查看+报bug |
| viewer | 查看者 | 只读 |

### 4.5 项目成员表 (project_members)
```
id: Integer, PK
project_id: Integer, FK(projects.id)
user_id: Integer, FK(users.id)
role_id: Integer, FK(project_roles.id)          [关联角色]
joined_at: DateTime
is_deleted: Boolean, default=False
created_at: DateTime
updated_at: DateTime
```

### 4.6 任务表 (tasks)
```
id: Integer, PK
project_id: Integer, FK(projects.id)
organization_id: Integer, FK(organizations.id)  [数据隔离]
parent_id: Integer, FK(tasks.id)                [支持子任务]
title: String(200)
description: Text
status: String(20)                               [todo/in_progress/review/done]
priority: String(20)                            [low/medium/high/urgent]
assignee_id: Integer, FK(users.id)              [任务负责人]
start_date: Date
due_date: Date
estimated_hours: Float
actual_hours: Float
progress: Integer [0-100]
is_deleted: Boolean, default=False
created_at: DateTime
updated_at: DateTime
```

### 4.7 任务依赖表 (task_dependencies)
```
id: Integer, PK
project_id: Integer, FK(projects.id)            [冗余存储，方便查询]
predecessor_id: Integer, FK(tasks.id)           [前置任务]
successor_id: Integer, FK(tasks.id)             [后置任务]
dependency_type: String(20)
├── finish_to_start (FS) - 前置完成才能开始后置
├── start_to_start (SS) - 前置开始才能开始后置
├── finish_to_finish (FF) - 前置完成才能完成后置
└── start_to_finish (SF) - 前置开始才能完成后置
created_at: DateTime
```

### 4.8 评论表 (comments)
```
id: Integer, PK
task_id: Integer, FK(tasks.id)
user_id: Integer, FK(users.id)
organization_id: Integer, FK(organizations.id)
content: Text
is_deleted: Boolean, default=False
created_at: DateTime
updated_at: DateTime
```

### 4.9 文档表 (documents)
```
id: Integer, PK
project_id: Integer, FK(projects.id)
organization_id: Integer, FK(organizations.id)
name: String(255)
file_path: String(500)
file_type: String(50)
file_size: Integer
version: Integer
uploaded_by: Integer, FK(users.id)
is_deleted: Boolean, default=False
created_at: DateTime
updated_at: DateTime
```

### 4.10 通知表 (notifications)
```
id: Integer, PK
user_id: Integer, FK(users.id)
organization_id: Integer, FK(organizations.id)
type: String(50)                                [task_assigned/comment/mention/deadline]
title: String(200)
content: Text
is_read: Boolean
related_type: String(20)                       [task/project/comment]
related_id: Integer
is_deleted: Boolean, default=False
created_at: DateTime
```

### 4.11 项目目标表 (project_goals)
```
id: Integer, PK
project_id: Integer, FK(projects.id)
organization_id: Integer, FK(organizations.id)
title: String(200)                              [目标标题]
description: Text                                [目标描述]
metrics: JSON                                    [成功指标]
target_date: Date                                [目标日期]
status: String(20)                               [pending/in_progress/achieved/cancelled]
progress: Integer [0-100]
is_deleted: Boolean, default=False
created_at: DateTime
updated_at: DateTime
```

### 4.12 交付物表 (deliverables)
```
id: Integer, PK
project_id: Integer, FK(projects.id)
organization_id: Integer, FK(organizations.id)
name: String(200)                               [交付物名称]
description: Text                                [交付物描述]
type: String(50)                                [document/code/design/report/sample]
version: String(50)
status: String(20)                              [pending/in_review/approved/rejected]
due_date: Date                                   [计划交付日期]
delivered_at: DateTime, nullable                 [实际交付日期]
reviewed_by: Integer, FK(users.id), nullable     [审核人]
reviewed_at: DateTime, nullable                  [审核时间]
review_comment: Text, nullable                   [审核意见]
file_id: Integer, FK(documents.id), nullable    [关联文档]
created_by: Integer, FK(users.id)
is_deleted: Boolean, default=False
created_at: DateTime
updated_at: DateTime
```

### 4.13 项目里程碑表 (project_milestones)
```
id: Integer, PK
project_id: Integer, FK(projects.id)
organization_id: Integer, FK(organizations.id)
name: String(100)                               [里程碑名称]
description: Text
planned_date: Date                               [计划日期]
actual_date: Date, nullable                      [实际完成日期]
status: String(20)                              [upcoming/in_progress/completed/delayed]
completion_rate: Integer [0-100]
is_deleted: Boolean, default=False
created_at: DateTime
updated_at: DateTime
```

### 4.14 项目风险表 (project_risks)
```
id: Integer, PK
project_id: Integer, FK(projects.id)
organization_id: Integer, FK(organizations.id)
title: String(200)                              [风险标题]
description: Text                                [风险描述]
category: String(50)                            [technical/resource/schedule/external]
probability: Integer [1-5]                       [发生概率 1-5]
impact: Integer [1-5]                           [影响程度 1-5]
risk_level: Integer [1-25]                      [风险等级 = probability × impact]
status: String(20)                              [identified/mitigated/occurred/closed]
mitigation: Text                                 [应对措施]
owner_id: Integer, FK(users.id)                 [风险负责人]
identified_date: Date
occurred_date: Date, nullable
closed_date: Date, nullable
is_deleted: Boolean, default=False
created_at: DateTime
updated_at: DateTime
```

### 4.15 项目问题表 (project_issues)
```
id: Integer, PK
project_id: Integer, FK(projects.id)
organization_id: Integer, FK(organizations.id)
task_id: Integer, FK(tasks.id), nullable        [关联任务]
title: String(200)                              [问题标题]
description: Text                                [问题描述]
type: String(50)                                [bug/question/improvement]
priority: String(20)                            [low/medium/high/critical]
status: String(20)                              [open/in_progress/resolved/closed]
assignee_id: Integer, FK(users.id), nullable    [处理人]
due_date: Date, nullable                        [解决期限]
resolved_at: DateTime, nullable                  [解决时间]
resolution: Text, nullable                      [解决方案]
closed_by: Integer, FK(users.id), nullable      [关闭人]
closed_at: DateTime, nullable                   [关闭时间]
created_by: Integer, FK(users.id)
is_deleted: Boolean, default=False
created_at: DateTime
updated_at: DateTime
```

### 4.16 项目活动日志表 (project_activities)
```
id: Integer, PK
project_id: Integer, FK(projects.id)
organization_id: Integer, FK(organizations.id)
user_id: Integer, FK(users.id)
action: String(50)                              [create/update/delete/status_change]
entity_type: String(50)                         [task/project/member/deliverable]
entity_id: Integer
old_value: JSON, nullable                       [变更前]
new_value: JSON, nullable                       [变更后]
ip_address: String(45)
created_at: DateTime
```

### 4.17 系统配置表 (system_settings)
```
id: Integer, PK
organization_id: Integer, FK(organizations.id), nullable  [NULL=全局配置]
key: String(100)                                [配置键]
value: Text                                     [配置值]
type: String(20)                                [string/integer/json/list/boolean]
description: String(255)
created_at: DateTime
updated_at: DateTime
```

---

## 5. API 接口设计

### 5.1 认证模块 (Auth)
```
POST   /api/auth/register       # 用户注册
POST   /api/auth/login          # 用户登录
POST   /api/auth/logout         # 退出登录
POST   /api/auth/refresh        # 刷新Token
POST   /api/auth/forgot-password # 忘记密码
PUT    /api/auth/reset-password # 重置密码
```

### 5.2 组织模块 (Organizations)
```
GET    /api/organizations              # 获取我的组织列表
POST   /api/organizations              # 创建组织
GET    /api/organizations/{id}         # 获取组织详情
PUT    /api/organizations/{id}         # 更新组织
DELETE /api/organizations/{id}         # 删除组织
GET    /api/organizations/{id}/tree    # 获取组织树
GET    /api/organizations/{id}/members # 获取组织成员
POST   /api/organizations/{id}/members # 添加成员
DELETE /api/organizations/{id}/members/{user_id} # 移除成员
```

### 5.3 用户模块 (Users)
```
GET    /api/users/me                   # 获取当前用户信息
PUT    /api/users/me                   # 更新当前用户
POST   /api/users/me/avatar            # 上传头像
GET    /api/users/{id}                  # 获取用户详情
GET    /api/users                      # 获取用户列表
PUT    /api/users/{id}/role            # 更新用户角色
```

### 5.4 项目模块 (Projects)
```
GET    /api/projects                   # 获取项目列表
POST   /api/projects                   # 创建项目
GET    /api/projects/{id}              # 获取项目详情
PUT    /api/projects/{id}              # 更新项目
DELETE /api/projects/{id}              # 删除项目
PUT    /api/projects/{id}/status       # 更新项目状态
```

### 5.5 项目角色模块 (Project Roles)
```
GET    /api/projects/{id}/roles              # 获取所有角色
POST   /api/projects/{id}/roles               # 创建自定义角色
PUT    /api/projects/{id}/roles/{role_id}   # 更新角色
DELETE /api/projects/{id}/roles/{role_id}   # 删除自定义角色
```

### 5.6 项目成员模块 (Project Members)
```
GET    /api/projects/{id}/members            # 获取项目成员
POST   /api/projects/{id}/members             # 添加成员
DELETE /api/projects/{id}/members/{user_id}  # 移除成员
PUT    /api/projects/{id}/members/{user_id}/role  # 分配角色
```

### 5.7 任务模块 (Tasks)
```
GET    /api/projects/{id}/tasks              # 获取任务列表
POST   /api/projects/{id}/tasks              # 创建任务
GET    /api/tasks/{id}                        # 获取任务详情
PUT    /api/tasks/{id}                        # 更新任务
DELETE /api/tasks/{id}                        # 删除任务
PUT    /api/tasks/{id}/status                # 更新状态
PUT    /api/tasks/{id}/assignee              # 指派负责人
GET    /api/tasks/{id}/subtasks              # 获取子任务
POST   /api/tasks/{id}/subtasks              # 创建子任务
```

### 5.8 任务依赖模块 (Task Dependencies)
```
GET    /api/tasks/{id}/dependencies        # 获取前置/后置依赖
POST   /api/tasks/{id}/dependencies        # 添加依赖
DELETE /api/tasks/{id}/dependencies/{dep_id} # 删除依赖
```

### 5.9 任务看板视图 (Task Board)
```
GET    /api/projects/{id}/board             # 获取看板数据
PUT    /api/projects/{id}/board/tasks/{task_id}/status  # 拖拽更新状态
PUT    /api/projects/{id}/board/tasks/{task_id}/order   # 更新排序
```

### 5.10 任务甘特图 (Task Gantt)
```
GET    /api/projects/{id}/gantt             # 获取甘特图数据
PUT    /api/tasks/{id}/dates                # 更新日期
PUT    /api/tasks/{id}/progress             # 更新进度
```

### 5.11 评论模块 (Comments)
```
GET    /api/tasks/{id}/comments             # 获取评论列表
POST   /api/tasks/{id}/comments              # 添加评论
PUT    /api/comments/{id}                    # 更新评论
DELETE /api/comments/{id}                    # 删除评论
```

### 5.12 文档模块 (Documents)
```
GET    /api/projects/{id}/documents          # 获取文档列表
POST   /api/projects/{id}/documents          # 上传文档
GET    /api/documents/{id}                   # 获取详情
PUT    /api/documents/{id}                   # 更新文档
DELETE /api/documents/{id}                   # 删除文档
GET    /api/documents/{id}/download          # 下载文档
```

### 5.13 通知模块 (Notifications)
```
GET    /api/notifications                    # 获取通知列表
GET    /api/notifications/unread             # 获取未读通知
PUT    /api/notifications/{id}/read          # 标记已读
PUT    /api/notifications/read-all           # 全部标记已读
DELETE /api/notifications/{id}               # 删除通知
```

### 5.14 报表模块 (Reports)
```
GET    /api/projects/{id}/stats/overview     # 项目概览统计
GET    /api/projects/{id}/stats/tasks        # 任务统计
GET    /api/projects/{id}/stats/team         # 团队工时统计
GET    /api/projects/{id}/burndown           # 燃尽图数据
GET    /api/users/{id}/workload              # 个人工作量统计
```

### 5.15 项目目标模块 (Project Goals)
```
GET    /api/projects/{id}/goals                 # 获取目标列表
POST   /api/projects/{id}/goals                # 创建目标
GET    /api/projects/{id}/goals/{goal_id}      # 获取详情
PUT    /api/projects/{id}/goals/{goal_id}      # 更新目标
DELETE /api/projects/{id}/goals/{goal_id}      # 删除目标
PUT    /api/projects/{id}/goals/{goal_id}/status  # 更新状态
```

### 5.16 交付物模块 (Deliverables)
```
GET    /api/projects/{id}/deliverables          # 获取列表
POST   /api/projects/{id}/deliverables         # 创建交付物
GET    /api/projects/{id}/deliverables/{del_id} # 获取详情
PUT    /api/projects/{id}/deliverables/{del_id} # 更新
DELETE /api/projects/{id}/deliverables/{del_id} # 删除
PUT    /api/projects/{id}/deliverables/{del_id}/review  # 审核
```

### 5.17 里程碑模块 (Milestones)
```
GET    /api/projects/{id}/milestones            # 获取列表
POST   /api/projects/{id}/milestones            # 创建里程碑
GET    /api/projects/{id}/milestones/{mil_id}   # 获取详情
PUT    /api/projects/{id}/milestones/{mil_id}   # 更新
DELETE /api/projects/{id}/milestones/{mil_id}   # 删除
PUT    /api/projects/{id}/milestones/{mil_id}/complete  # 完成
```

### 5.18 风险模块 (Risks)
```
GET    /api/projects/{id}/risks                 # 获取风险列表
POST   /api/projects/{id}/risks                # 创建风险
GET    /api/projects/{id}/risks/{risk_id}       # 获取详情
PUT    /api/projects/{id}/risks/{risk_id}       # 更新风险
DELETE /api/projects/{id}/risks/{risk_id}      # 删除风险
PUT    /api/projects/{id}/risks/{risk_id}/status  # 更新状态
PUT    /api/projects/{id}/risks/{risk_id}/mitigation  # 更新应对措施
```

### 5.19 问题模块 (Issues)
```
GET    /api/projects/{id}/issues                # 获取问题列表
POST   /api/projects/{id}/issues               # 创建问题
GET    /api/projects/{id}/issues/{issue_id}     # 获取详情
PUT    /api/projects/{id}/issues/{issue_id}    # 更新问题
DELETE /api/projects/{id}/issues/{issue_id}    # 删除问题
PUT    /api/projects/{id}/issues/{issue_id}/assignee  # 指派
PUT    /api/projects/{id}/issues/{issue_id}/resolve  # 解决
PUT    /api/projects/{id}/issues/{issue_id}/close    # 关闭
```

### 5.20 活动日志模块 (Activities)
```
GET    /api/projects/{id}/activities            # 获取项目日志
GET    /api/users/{id}/activities              # 获取用户日志
GET    /api/activities/{id}                    # 获取详情
```

### 5.21 系统配置模块 (Settings)
```
GET    /api/settings                           # 获取全局配置
PUT    /api/settings                          # 更新全局配置
GET    /api/organizations/{id}/settings       # 获取组织配置
PUT    /api/organizations/{id}/settings       # 更新组织配置
GET    /api/projects/{id}/settings            # 获取项目配置
PUT    /api/projects/{id}/settings            # 更新项目配置
```

---

## 6. 前端模块设计

| 模块 | 路由 | 功能 |
|------|------|------|
| **Auth** | /auth/* | 登录、注册、找回密码 |
| **Dashboard** | / | 首页统计、待办事项 |
| **Organizations** | /organizations/* | 组织管理、成员管理 |
| **Projects** | /projects/* | 项目列表、项目详情 |
| **Kanban** | /projects/:id/board | 看板视图 |
| **Gantt** | /projects/:id/gantt | 甘特图视图 |
| **Tasks** | /projects/:id/tasks | 任务列表 |
| **Goals** | /projects/:id/goals | 项目目标管理 |
| **Deliverables** | /projects/:id/deliverables | 交付物管理 |
| **Milestones** | /projects/:id/milestones | 里程碑管理 |
| **Risks** | /projects/:id/risks | 风险管理 |
| **Issues** | /projects/:id/issues | 问题跟踪 |
| **Documents** | /projects/:id/docs | 文档管理 |
| **Reports** | /projects/:id/reports | 报表统计 |
| **Activities** | /projects/:id/activities | 活动日志 |
| **Settings** | /settings/* | 个人设置、系统设置 |

---

## 7. 30天开发里程碑

### Week 1 (Day 1-7): 基础设施

| Day | 任务 | 输出 |
|-----|------|------|
| 1-2 | 项目初始化 | Vue3 + FastAPI + Docker 环境搭建 |
| 3-4 | 数据库设计 | SQLite 表结构创建（17张表） |
| 5-6 | 认证模块 | JWT 登录、注册、Token刷新、密码加密 |
| 7 | 组织模块 | 组织 CRUD、成员管理、层级结构 |

### Week 2 (Day 8-14): 核心功能

| Day | 任务 | 输出 |
|-----|------|------|
| 8-9 | 项目管理 | 项目 CRUD、状态流转 |
| 10-11 | 项目角色 | 角色定义、权限系统、预设角色 |
| 12-13 | 任务管理 | 任务 CRUD、子任务、状态管理 |
| 14 | 任务依赖 | 依赖关系、层级结构 |

### Week 3 (Day 15-21): 项目管理增强

| Day | 任务 | 输出 |
|-----|------|------|
| 15-16 | 项目目标/里程碑 | 目标管理、里程碑时间线 |
| 17-18 | 看板视图 | 拖拽操作、状态更新 |
| 19-20 | 交付物管理 | 文件上传、审核流程 |
| 21 | 甘特图 | 时间线展示、依赖可视化 |

### Week 4 (Day 22-28): 协作与增强

| Day | 任务 | 输出 |
|-----|------|------|
| 22-23 | 风险/问题跟踪 | 风险登记、问题跟踪、优先级 |
| 24-25 | 评论/通知 | 任务评论、@提及、站内通知 |
| 26-27 | 报表统计 | 概览、工时、燃尽图、活动日志 |
| 28 | 测试修复 | Bug 修复、性能优化 |

### Day 29-30: 部署与交付

| Day | 任务 |
|-----|------|
| 29 | Docker 镜像构建、部署脚本、Nginx 配置 |
| 30 | 部署测试、文档完善、交付验收 |

---

## 8. 部署架构

```yaml
# docker-compose.yml

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/dist:/usr/share/nginx/html
    depends_on:
      - backend

  backend:
    build: ./backend
    volumes:
      - ./backend:/app
      - uploads:/app/uploads
    environment:
      - DATABASE_URL=sqlite:///./data/project.db
      - SECRET_KEY=your-secret-key
    command: uvicorn main:app --host 0.0.0.0 --port 8000

volumes:
  uploads:
```

---

## 11. UI/UX 设计规范

### 11.1 设计策略

| 项目 | 描述 |
|------|------|
| **设计工具** | Figma（推荐）、Sketch + Zeplin |
| **设计模式** | 核心页面高保真 + 设计系统 + PC端优先 |
| **响应式断点** | xs(<576) / sm(576-768) / md(768-992) / lg(992-1200) / xl(1200-1600) / xxl(>1600) |

### 11.2 核心页面清单（18 个）

| 序号 | 页面 | 优先级 | 复杂度 |
|------|------|--------|--------|
| 1 | 登录页 | P0 | 低 |
| 2 | 注册页 | P0 | 低 |
| 3 | 首页/仪表盘 | P0 | 高 |
| 4 | 项目列表页 | P0 | 中 |
| 5 | 项目详情页 | P0 | 高 |
| 6 | 项目设置页 | P0 | 低 |
| 7 | 任务看板页 | P0 | 高 |
| 8 | 任务列表页 | P0 | 中 |
| 9 | 任务详情弹窗 | P0 | 中 |
| 10 | 任务创建/编辑弹窗 | P0 | 中 |
| 11 | 甘特图页 | P0 | 高 |
| 12 | 资源分配页 | P1 | 高 |
| 13 | 计划管理页 | P0 | 高 |
| 14 | 计划 WBS 编辑页 | P0 | 高 |
| 15 | 基线对比页 | P1 | 高 |
| 16 | 审批列表页 | P0 | 低 |
| 17 | 审批详情页 | P0 | 中 |
| 18 | 报表统计页 | P1 | 高 |

### 11.3 色彩规范

#### 主色调
```
品牌蓝（Brand Blue）: #1E5EB8
├─ 主色（Primary）: #1E5EB8
├─ 浅色（Primary Light）: #4A90E2
├─ 深色（Primary Dark）: #154A8A
└─ 悬停（Primary Hover）: #2B70D0
```

#### 语义色
```
成功（Success）: #52C41A
警告（Warning）: #FAAD14
危险（Danger）: #FF4D4F
信息（Info）: #1890FF
```

#### 状态色
```
待办（Todo）: #8C8C8C   ━━━ 灰色
进行中（In Progress）: #1890FF  ━━━ 蓝色
已完成（Done）: #52C41A   ━━━ 绿色
已逾期（Overdue）: #FF4D4F  ━━━ 红色
待审批（Pending）: #FAAD14  ━━━ 黄色
```

#### 优先级色
```
紧急（Urgent）: #FF4D4F  ━━━ 红色
高（High）: #FA8C16      ━━━ 橙色
中（Medium）: #1890FF    ━━━ 蓝色
低（Low）: #8C8C8C      ━━━ 灰色
```

### 11.4 字体规范

```
主字体: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto

字号层级:
├─ 特大标题: 32px / 40px / 600
├─ 大标题: 24px / 32px / 600
├─ 中标题: 18px / 24px / 600
├─ 小标题: 16px / 24px / 600
├─ 正文大: 15px / 24px / 400
├─ 正文: 14px / 22px / 400
├─ 小字: 12px / 20px / 400
└─ 极小字: 11px / 18px / 400
```

### 11.5 间距规范

```
基础单位: 4px
├─ xs: 4px
├─ sm: 8px
├─ md: 16px
├─ lg: 24px
├─ xl: 32px
├─ 2xl: 48px
└─ 3xl: 64px

页面边距: 24px / 32px / 48px（大屏）
卡片内边距: 24px
按钮内边距: 8px 16px
```

### 11.6 圆角与阴影

```
圆角:
├─ 小: 4px（标签、徽章）
├─ 中: 6px（按钮、输入框）
├─ 大: 8px（卡片、弹窗）
├─ XL: 12px（模态框）
└─ 圆形: 50%（头像）

阴影:
├─ SM: 0 1px 2px rgba(0,0,0,0.05)
├─ MD: 0 4px 6px rgba(0,0,0,0.07)
├─ LG: 0 10px 20px rgba(0,0,0,0.08)
├─ Hover: 0 8px 24px rgba(0,0,0,0.12)
└─ Popover: 0 12px 48px rgba(0,0,0,0.15)
```

### 11.7 组件规范

#### 按钮（Buttons）
```
主要（Primary）:
├─ 背景: #1E5EB8
├─ 文字: #FFFFFF
├─ 圆角: 6px
├─ 高度: 36px / 40px
└─ 悬停: #2B70D0

次要（Secondary）:
├─ 背景: #FFFFFF
├─ 边框: 1px solid #E8E8E8
├─ 文字: #262626
└─ 悬停: #F5F7FA

危险（Danger）: #FF4D4F
```

#### 输入框（Inputs）
```
高度: 36px / 40px
边框: 1px solid #E8E8E8
圆角: 6px
聚焦边框: #1E5EB8
聚焦阴影: 0 0 0 2px rgba(30, 94, 184, 0.1)
错误边框: #FF4D4F
```

#### 卡片（Cards）
```
背景: #FFFFFF
圆角: 8px
边框: 1px solid #F0F0F0
内边距: 24px
阴影: 0 1px 2px rgba(0,0,0,0.05)
悬浮阴影: 0 8px 24px rgba(0,0,0,0.12)
```

#### 表格（Tables）
```
表头背景: #FAFAFA
表头高度: 48px
表头字重: 600
表体行高: 52px / 56px
悬停背景: #F5F7FA
选中背景: #E6F4FF
边框: 1px solid #F0F0F0
```

### 11.8 导航规范

#### 顶部导航
```
高度: 64px
背景: #FFFFFF
边框底: 1px solid #F0F0F0
```

#### 侧边栏导航
```
宽度: 240px / 收起: 80px
背景: #FFFFFF
菜单项高度: 44px
图标大小: 20px
选中背景: #E6F4FF
选中文字: #1E5EB8
```

### 11.9 页面布局

```
┌─────────────────────────────────────────────────────────────┐
│                      顶部导航栏（64px）                      │
├──────────┬──────────────────────────────────────────────────┤
│          │                                                  │
│  侧边栏  │                   主内容区                       │
│ (240px)  │                                                  │
│          │                                                  │
│          │                                                  │
├──────────┴──────────────────────────────────────────────────┤
│                      底部版权                               │
└─────────────────────────────────────────────────────────────┘

主内容区:
├─ 面包屑导航
├─ 页面标题 + 操作按钮
├─ 筛选/搜索区域
├─ 表格/列表/看板
└─ 分页控件
```

### 11.10 响应式策略

| 断点 | 布局调整 |
|------|----------|
| xl (1200+) | 完整布局 |
| lg (992-1200) | 侧边栏收起 |
| md (768-992) | 侧边栏隐藏（汉堡菜单）、表格卡片化 |
| sm (576-768) | 单列布局 |
| xs (<576) | 简化导航、全屏抽屉 |

### 11.11 图标库

```
图标库: Ant Design Icons / Heroicons
大小: 16px / 20px / 24px / 32px
风格: 线性（导航） + 实心（选中）
颜色: #595959（默认）、#262626（hover）、#BFBFBF（禁用）
```

### 11.12 组件清单

| 组件 | 用途 |
|------|------|
| **DataTable** | 表格展示、分页、排序 |
| **KanbanBoard** | 看板视图、拖拽 |
| **GanttChart** | 甘特图、时间线 |
| **WBSTree** | WBS 树形结构 |
| **TaskCard** | 任务卡片 |
| **UserAvatar** | 用户头像 |
| **FileUpload** | 文件上传 |
| **RichTextEditor** | 富文本编辑 |
| **ResourceLoadChart** | 资源负载图 |
| **BaselineComparison** | 基线对比视图 |
| **ApprovalFlow** | 审批流程可视化 |
| **VarianceChart** | 偏差图表 |
| **NotificationCenter** | 通知中心 |

---

## 12. 待确认事项

- [ ] 是否需要移动端 APP？还是只做响应式 Web？
- [ ] 邮件通知使用什么服务？（SMTP 自建 / 阿里云邮件 / SendGrid）
- [ ] 文件存储策略？（本地存储 / 对象存储如阿里云 OSS）
- [ ] 是否支持第三方登录？（企业微信/钉钉/飞书）

---

## 13. 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-02-08 | v1.0 | 初始设计方案 |
| 2026-02-08 | v1.1 | 补充安全机制、API规范、新增项目目标/交付物/里程碑/风险/问题表 |
| 2026-02-08 | v1.2 | 补充 UI/UX 设计规范（18个核心页面、设计系统、组件规范） |
