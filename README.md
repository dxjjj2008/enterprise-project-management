# 企业项目管理系统

**版本**: v1.0  
**创建日期**: 2026-02-08  
**最后更新**: 2026-02-09

## 项目简介

企业项目管理系统是一个集项目、任务、计划、资源、风险、问题于一体的综合管理平台，帮助团队高效协作、科学管理项目。

## 技术栈

### 前端 ✅ 已完成
- **Vue 3** - 渐进式 JavaScript 框架
- **Element Plus** - Vue 3 UI 组件库
- **Vite** - 构建工具
- **Vue Router** - 路由管理
- **Pinia** - 状态管理
- **SortableJS** - 拖拽功能
- **Vitest** - 单元测试框架 ⭐ **新增**

### 后端 ✅ 已初始化
- **FastAPI** - Python Web 框架
- **SQLite** - 轻量级数据库
- **JWT** - 身份认证
- **pytest** - Python 测试框架 ⭐ **已配置**

## 项目结构

```
enterprise-project-management/
├── 📁 docs/                   # 项目文档
│   ├── README.md             ← 文档索引
│   ├── 📁 requirements/      # 需求文档
│   ├── 📁 design/            # 设计文档
│   │   └── 📁 pages/          # 页面设计
│   ├── 📁 api/               # API 文档
│   └── 📁 manual/            # 用户手册
│
├── 📁 src/                   # 源代码
│   ├── 📁 frontend/          # Vue 3 前端
│   │   ├── 📁 tests/         # 测试用例
│   │   │   ├── 📁 e2e/       # E2E 测试
│   │   │   └── 📁 unit/      # 单元测试
│   │   └── 📁 src/views/      # 页面组件
│   └── 📁 backend/            # FastAPI 后端 ✅ 已完成
│       ├── 📁 tests/         # 后端测试
│       └── 📁 app/api/v1/    # API 端点
│
├── 📁 deployment/            # 部署配置
│   └── 📁 docker/            # Docker 配置
└── 📁 docker-compose.yml      # Docker Compose 部署 ⭐ 新增

## 已开发功能

### ✅ 完成
| 模块 | 功能 | 位置 |
|------|------|------|
| 首页仪表盘 | 8 统计卡片、项目统计 | `src/frontend/src/views/dashboard/` |
| 侧边栏 | 导航菜单、可拖拽宽度 | `src/frontend/src/views/layout/` |
| 文档中心 | 6 类文档、markdown 渲染 | `src/frontend/src/views/docs/` |
| 任务看板 | 3 列看板、拖拽、筛选、搜索 | `src/frontend/src/views/tasks/` |
| 甘特图 | 时间轴视图、任务依赖、里程碑 | `src/frontend/src/views/projects/Gantt.vue` |
| 资源管理 | 用户列表、工作量、利用率 | `src/frontend/src/views/resources/` |
| 问题跟踪 | 问题列表、状态流转、评论 | `src/frontend/src/views/issues/` |
| 风险管理 | 风险矩阵、应对措施、监控 | `src/frontend/src/views/risks/` |
| 审批流程 | 审批列表、流程管理、状态流转 | `src/frontend/src/views/approvals/` |
| 报表统计 | 项目报表、任务统计、资源报表 | `src/frontend/src/views/reports/` |
| **测试框架** | Vitest + Pytest | `src/frontend/tests/` / `src/backend/tests/` |

### ⏳ 待开发
| 模块 | 说明 |
|------|------|
| Docker 部署 | Docker Compose 一键部署 |
| CI/CD | GitHub Actions 自动部署 |
| Redis 缓存 | API 响应优化 |
| PostgreSQL | 生产环境数据库切换 |

## 快速开始

### 前端
```bash
cd src/frontend
npm install
npm run dev
```

### 后端
```bash
cd backend
pip install -r requirements.txt
python -m app.core.init_db
bash start.sh
```

### 运行测试
```bash
cd src/frontend
npm test              # 监控模式
npm run test:run      # 运行一次
npm run test:coverage # 生成覆盖率报告
```

### 访问地址
- **开发服务器**: http://localhost:3001/
- **文档中心**: http://localhost:3001/docs

## 文档导航

| 类型 | 文档 | 说明 |
|------|------|------|
| 需求 | [docs/requirements/2026-02-08-requirements.md](./docs/requirements/2026-02-08-requirements.md) | 用户故事、功能需求 |
| UI/UX | [docs/design/ui-ux/2026-02-08-ui-ux-design.md](./docs/design/ui-ux/2026-02-08-ui-ux-design.md) | 设计规范 |
| 架构 | [docs/design/architecture/2026-02-08-project-management-system-design.md](./docs/design/architecture/2026-02-08-project-management-system-design.md) | 技术架构 |
| API | [docs/api/2026-02-08-api.md](./docs/api/2026-02-08-api.md) | 接口文档 |
| 手册 | [docs/manual/2026-02-08-user-manual.md](./docs/manual/2026-02-08-user-manual.md) | 用户手册 |
| ⭐ 测试 | [TESTING_QUICKSTART.md](./TESTING_QUICKSTART.md) | 测试框架快速入门 |
| ⭐ 测试 | [docs/testing/2026-02-09-testing-guide.md](./docs/testing/2026-02-09-testing-guide.md) | 测试配置指南 |

## 页面设计文档

| 文档 | 说明 |
|------|------|
| [docs/design/pages/2026-02-08-task-board-plan.md](./docs/design/pages/2026-02-08-task-board-plan.md) | 任务看板开发计划 |
| [docs/design/pages/2026-02-08-task-board-design.md](./docs/design/pages/2026-02-08-task-board-design.md) | 任务看板详细设计 |
| [docs/design/pages/2026-02-10-approvals-design.md](./docs/design/pages/2026-02-10-approvals-design.md) | 审批流程设计 |
| [docs/design/pages/2026-02-10-planning-design.md](./docs/design/pages/2026-02-10-planning-design.md) | 计划管理设计 |
| [docs/design/pages/2026-02-10-reports-design.md](./docs/design/pages/2026-02-10-reports-design.md) | 报表统计设计 |
| [docs/design/pages/2026-02-10-resource-management.md](./docs/design/pages/2026-02-10-resource-management.md) | 资源管理设计 |
| [docs/design/pages/2026-02-11-gantt-chart-design.md](./docs/design/pages/2026-02-11-gantt-chart-design.md) | 甘特图设计 |
| [docs/design/pages/2026-02-11-issues-design.md](./docs/design/pages/2026-02-11-issues-design.md) | 问题跟踪设计 |
| [docs/design/pages/2026-02-11-risks-design.md](./docs/design/pages/2026-02-11-risks-design.md) | 风险管理设计 |

## 变更记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-02-08 | v1.0 | 初始版本 |
| 2026-02-08 | v1.1 | 新增仪表盘 |
| 2026-02-08 | v1.2 | 新增文档中心 |
| 2026-02-08 | v1.3 | 新增任务看板 |
| 2026-02-08 | v1.4 | 完善任务看板功能 |
| 2026-02-10 | v1.5 | 新增审批流程、计划管理、报表统计 |
| 2026-02-11 | v1.6 | 新增甘特图、问题跟踪、风险管理 |
| 2026-02-11 | v1.7 | 新增 Docker Compose 部署配置 |

## 许可证

MIT License
