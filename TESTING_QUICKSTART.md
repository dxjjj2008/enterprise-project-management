# 测试框架快速入门

**创建日期**: 2026-02-09  
**状态**: ✅ 已配置完成

---

## ✅ 已安装的测试框架

### 前端 (Vitest)

| 工具 | 版本 | 用途 |
|------|------|------|
| **vitest** | ^4.0.18 | 单元测试框架 |
| **@vue/test-utils** | ^2.4.6 | Vue 3 测试工具 |
| **happy-dom** | ^20.5.0 | 轻量级 DOM 模拟 |

### 后端 (待安装)

| 工具 | 版本 | 用途 |
|------|------|------|
| **pytest** | 待安装 | Python 测试框架 |
| **pytest-asyncio** | 待安装 | 异步测试支持 |

---

## 🚀 快速开始

### 前端测试

```bash
# 运行所有测试
cd src/frontend
npm test

# 运行一次并退出
npm run test:run

# 生成覆盖率报告
npm run test:coverage
```

### 后端测试

```bash
# 安装依赖
cd backend
python -m pip install pytest pytest-asyncio httpx

# 运行测试
pytest
```

---

## 📁 测试文件位置

### 前端测试

```
src/frontend/src/views/
├── dashboard/
│   ├── Index.vue
│   └── Index.test.js      ← 仪表盘测试 (✅ 已创建)
├── tasks/
│   ├── Board.vue
│   └── Board.test.js      ← 任务看板测试 (✅ 已创建)
├── demo.test.js           ← 入门示例测试 (✅ 已创建，2026-02-09)
└── README.test.md         ← 测试说明文档
```

### 后端测试

```
backend/
├── app/
│   └── routers/
│       └── auth_test.py   ← 待创建
└── tests/
    ├── conftest.py        ← pytest 配置 (待创建)
    └── README.md         ← 测试说明文档 (✅ 已创建)
```

---

## ✅ 已完成的测试

### 前端 (15 个测试全部通过)

| 测试文件 | 测试数量 | 状态 | 说明 |
|---------|---------|------|------|
| `dashboard/Index.test.js` | 3 | ✅ 通过 | 仪表盘页面测试 |
| `tasks/Board.test.js` | 5 | ✅ 通过 | 任务看板测试 |
| `demo.test.js` | 7 | ✅ 通过 | 入门示例测试 |

### 测试覆盖

- ✅ 仪表盘标题渲染
- ✅ 统计卡片结构
- ✅ 任务卡片渲染
- ✅ 状态筛选功能
- ✅ 关键词搜索逻辑
- ✅ 看板列结构
- ✅ 基本断言用法 (demo.test.js)
- ✅ 数组/对象/条件测试 (demo.test.js)

---

## 📊 测试覆盖率

运行 `npm run test:coverage` 后：

```
覆盖率报告位置: coverage/index.html
```

---

## 🛠️ 常用命令

```bash
# 监控模式（文件变化自动重测）
npm test

# 运行所有测试一次
npm run test:run

# 运行指定测试文件
npm run test:run -- src/views/dashboard/Index.test.js

# 生成 HTML 覆盖率报告
npm run test:coverage
```

---

## 📝 添加新测试

### 1. 创建测试文件

```javascript
// src/views/your-component/YourComponent.test.js
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

describe('YourComponent', () => {
  it('renders properly', () => {
    const wrapper = mount({
      template: '<div>Hello</div>'
    })
    expect(wrapper.text()).toBe('Hello')
  })
})
```

### 2. 运行测试

```bash
npm test
```

---

## ⚠️ 已知问题

### Element Plus 组件警告

测试时会出现 `Failed to resolve component: el-col` 警告。

**原因**: 测试环境未全局注册 Element Plus。

**解决方案**: 在测试中使用 mock 组件，或在测试配置中全局注册。

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'

describe('YourComponent', () => {
  it('uses Element Plus', () => {
    const wrapper = mount({
      template: '<el-button>Test</el-button>'
    }, {
      global: {
        plugins: [ElementPlus]
      }
    })
  })
})
```

---

## 📚 相关文档

- [测试框架配置指南](../../docs/testing/2026-02-09-testing-guide.md)
- [后端测试配置](../../backend/tests/README.md)
- [开发计划](../../docs/plans/2026-02-08-development-plan.md)

---

**下一步**: 安装后端测试框架 (pytest) 并创建 API 测试用例
