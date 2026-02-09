# 企业项目管理系统 - 后端

## 技术栈

- **FastAPI**: Python Web 框架
- **SQLite**: 轻量级数据库
- **SQLAlchemy**: ORM 工具
- **Pydantic**: 数据验证
- **JWT**: 身份认证

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
│   │   ├── auth.py          ← 认证路由
│   │   └── projects.py      ← 项目管理路由
│   └── schemas/
│       └── __init__.py      ← Pydantic 数据模型
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

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 根端点，返回欢迎信息 |
| `/health` | GET | 健康检查 |
| `/api/v1/auth/login` | POST | 用户登录（占位） |
| `/api/v1/auth/me` | GET | 获取当前用户信息（占位） |
| `/api/v1/projects` | GET | 获取项目列表（占位） |
| `/api/v1/projects` | POST | 创建新项目（占位） |

## 开发指南

- 所有路由都放在 `app/routers/` 目录下
- 数据模型定义在 `app/models/` 目录下
- 数据库配置在 `app/core/database.py`
- 使用 Pydantic 模型进行数据验证（将在 `app/schemas/` 中添加）

---

**版本**: v1.0
**最后更新**: 2026-02-09
