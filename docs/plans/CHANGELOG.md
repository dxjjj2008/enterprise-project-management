# Changelog

## [v1.1] - 2026-02-09

### ⭐ New Features

- **测试框架**: 安装并配置 Vitest 前端测试框架
  - 安装 vitest ^4.0.18
  - 安装 @vue/test-utils ^2.4.6
  - 安装 happy-dom ^20.5.0
  - 配置 vite.config.js 测试环境
  - 创建 2 个示例测试文件 (8 个测试全部通过)
  - 创建测试框架配置文档
  - 创建测试快速入门指南

### 🐛 Bug Fixes

- 修复任务看板 HTML 结构问题
- 修复 Dashboard 组件标签不匹配问题

### 📝 Documentation

- 新增 docs/testing/2026-02-09-testing-guide.md (测试框架配置指南)
- 新增 backend/tests/README.md (后端测试说明)
- 新增 TESTING_QUICKSTART.md (快速入门)
- 新增 src/views/README.test.md (前端测试说明)
- 更新 README.md (添加测试框架信息)

---

## [v1.0] - 2026-02-08

### Initial Release

**已完成功能**:
- 首页仪表盘（80%）
- 侧边栏导航（100%）
- 文档中心（100%）
- 任务看板（100%）
- 用户登录/注册（100%）
- 项目列表（60%）
- 项目详情（60%）

**文档**:
- 需求文档
- UI/UX 设计
- 系统架构
- 模块设计
- 页面设计（任务看板）
- API 文档
- 用户手册
- 开发规划

**技术栈**:
- Vue 3 + Element Plus + Vite
- FastAPI + SQLite（待开发）
- JWT 认证

---

## Future Releases

### v1.2 (Planned)
- 甘特图模块
- 资源分配模块
- 审批流程模块
- 报表统计模块
- 后端 API 完整实现
- pytest 后端测试框架

### v2.0 (Planned)
- 风险管理模块
- 问题跟踪模块
- 系统设置模块
- 性能优化
- 生产部署
