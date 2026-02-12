# 企业项目管理系统 - 后端

**版本**: v2.1
**最后更新**: 2026-02-12

## 技术栈

- **FastAPI**: Python Web 框架
- **SQLite**: 轻量级数据库
- **SQLAlchemy**: ORM 工具
- **Pydantic**: 数据验证
- **JWT**: 身份认证
- **pytest**: 测试框架

## 目录结构

```
backend/
├── app/
│   ├── main.py              ← 主应用入口
│   ├── core/
│   │   ├── database.py      ← 数据库配置
│   │   └── init_db.py       ← 数据库初始化
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          ← 用户模型
│   │   └── project.py       ← 项目和任务模型
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          ← 认证路由 ✅
│   │   ├── projects.py      ← 项目管理路由 ✅
│   │   ├── tasks.py         ← 任务管理路由 ✅
│   │   ├── gantt.py         ← 甘特图路由 ✅
│   │   ├── planning.py      ← 计划管理路由 ✅
│   │   ├── resources.py     ← 资源管理路由 ✅
│   │   ├── issues.py        ← 问题跟踪路由 ✅
│   │   ├── risks.py        ← 风险管理路由 ✅
│   │   ├── approvals.py     ← 审批流程路由 ✅
│   │   └── reports.py       ← 报表统计路由 ✅
│   └── schemas/
│       ├── __init__.py
│       ├── user.py          ← 用户 Pydantic 模型
│       ├── project.py       ← 项目/任务 Pydantic 模型
│       └── common.py        ← 通用响应模型
├── requirements.txt       ← 依赖列表
├── start.sh               ← 启动脚本
└── tests/                 ← 测试目录
    └── README.md
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
python -m app.core.init_db
```

### 3. 启动服务

```bash
bash start.sh
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## API 端点

### 认证模块 `/api/v1/auth`
| 方法 | 端点 | 描述 | 状态 |
|------|------|------|------|
| POST | `/login` | 用户登录 | ✅ |
| POST | `/register` | 用户注册 | ✅ |
| GET | `/me` | 获取当前用户 | ✅ |
| POST | `/refresh` | 刷新令牌 | ✅ |

### 项目管理 `/api/v1/projects`
| 方法 | 端点 | 描述 | 状态 |
|------|------|------|------|
| GET | `/` | 获取项目列表 | ✅ |
| POST | `/` | 创建项目 | ✅ |
| GET | `/{id}` | 获取项目详情 | ✅ |
| PUT | `/{id}` | 更新项目 | ✅ |
| DELETE | `/{id}` | 删除项目 | ✅ |

### 任务管理 `/api/v1/tasks`
| 方法 | 端点 | 描述 | 状态 |
|------|------|------|------|
| GET | `/board` | 获取任务看板 | ✅ |
| GET | `/` | 获取任务列表 | ✅ |
| POST | `/` | 创建任务 | ✅ |
| PUT | `/{id}` | 更新任务 | ✅ |
| PUT | `/{id}/status` | 更新任务状态 | ✅ |
| DELETE | `/{id}` | 删除任务 | ✅ |

### 资源管理 `/api/v1/resources`
| 方法 | 端点 | 描述 | 状态 |
|------|------|------|------|
| GET | `/` | 获取资源列表 | ✅ |
| GET | `/{id}` | 获取资源详情 | ✅ |
| GET | `/users` | 获取用户列表 | ✅ |
| GET | `/workload` | 获取工作负载 | ✅ |
| GET | `/utilization` | 获取利用率 | ✅ |

### 甘特图 `/api/v1/gantt`
| 方法 | 端点 | 描述 | 状态 |
|------|------|------|------|
| GET | `/` | 获取甘特图数据 | ✅ |
| GET | `/{project_id}` | 获取项目甘特图 | ✅ |

### 计划管理 `/api/v1/planning`
| 方法 | 端点 | 描述 | 状态 |
|------|------|------|------|
| GET | `/` | 获取计划列表 | ✅ |
| POST | `/` | 创建计划 | ✅ |
| GET | `/{id}` | 获取计划详情 | ✅ |
| PUT | `/{id}` | 更新计划 | ✅ |
| DELETE | `/{id}` | 删除计划 | ✅ |

### 问题跟踪 `/api/v1/issues`
| 方法 | 端点 | 描述 | 状态 |
|------|------|------|------|
| GET | `/` | 获取问题列表 | ✅ |
| POST | `/` | 创建问题 | ✅ |
| GET | `/{id}` | 获取问题详情 | ✅ |
| PUT | `/{id}` | 更新问题 | ✅ |
| DELETE | `/{id}` | 删除问题 | ✅ |

### 风险管理 `/api/v1/risks`
| 方法 | 端点 | 描述 | 状态 |
|------|------|------|------|
| GET | `/` | 获取风险列表 | ✅ |
| POST | `/` | 创建风险 | ✅ |
| GET | `/{id}` | 获取风险详情 | ✅ |
| PUT | `/{id}` | 更新风险 | ✅ |
| DELETE | `/{id}` | 删除风险 | ✅ |
| GET | `/matrix` | 获取风险矩阵 | ✅ |

### 审批流程 `/api/v1/approvals`
| 方法 | 端点 | 描述 | 状态 |
|------|------|------|------|
| GET | `/` | 获取审批列表 | ✅ |
| POST | `/` | 创建审批 | ✅ |
| GET | `/{id}` | 获取审批详情 | ✅ |
| POST | `/{id}/approve` | 审批通过 | ✅ |
| POST | `/{id}/reject` | 审批拒绝 | ✅ |

### 报表统计 `/api/v1/reports`
| 方法 | 端点 | 描述 | 状态 |
|------|------|------|------|
| GET | `/projects` | 项目报表 | ✅ |
| GET | `/tasks` | 任务报表 | ✅ |
| GET | `/resources` | 资源报表 | ✅ |

## 响应格式

### 通用响应 (ResponseModel)
```json
{
  "success": true,
  "message": "操作成功",
  "data": {...},
  "count": null
}
```

### 分页响应 (PaginationResponse)
```json
{
  "success": true,
  "message": "操作成功",
  "data": [...],
  "total": 100,
  "page": 1,
  "page_size": 10
}
```

## 开发指南

- 所有路由都放在 `app/routers/` 目录下
- 数据模型定义在 `app/models/` 目录下
- 数据库配置在 `app/core/database.py`
- 使用 Pydantic 模型进行数据验证在 `app/schemas/` 目录中
- 遵循 RESTful API 设计规范
- 响应格式使用 `ResponseModel` 和 `PaginationResponse` 包装
- 支持 JWT Token 认证

## 最近更新 (v2.1)

### 2026-02-12 更新
1. **登录 API 增强**
   - 同时支持 JSON 和表单格式请求
   - 解决前端 axios 发送 JSON 导致的认证问题

2. **任务看板 API**
   - 添加全局 `/api/v1/tasks/board` 端点
   - 支持不按项目分组获取所有任务

---

**版本**: v2.1
**最后更新**: 2026-02-12
