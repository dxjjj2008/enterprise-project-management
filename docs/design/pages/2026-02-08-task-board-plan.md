# 任务看板实现计划

## 1. 概述

### 1.1 目标
实现任务看板页面，支持看板视图、任务拖拽、任务管理等功能。

### 1.2 页面位置
- 路由：`/tasks/board`
- 文件：`/views/tasks/Board.vue`

### 1.3 设计规范
- 品牌蓝：`#1E5EB8`
- 圆角：`8px`
- 字体：`Inter`
- 卡片高度自适应

---

## 2. 功能需求

### 2.1 看板列
| 列名 | 状态值 | 说明 |
|------|--------|------|
| 待办 | todo | 新建任务默认状态 |
| 进行中 | in_progress | 正在执行的任务 |
| 已完成 | done | 已完成的任务 |

### 2.2 任务卡片
- 标题
- 优先级标签（高/中/低）
- 截止日期
- 负责人头像
- 标签/分类

### 2.3 交互功能
- 拖拽移动任务（列间/列内）
- 点击查看详情
- 新建任务按钮
- 筛选功能

---

## 3. 组件结构

```
Board.vue
├── 页面头部
│   ├── 标题 "任务看板"
│   └── 操作栏
│       ├── 项目选择器
│       └── 新建任务按钮
├── 看板主体
│   └── 看板列 × 3
│       ├── 列头部
│       │   ├── 列标题
│       │   └── 任务数量
│       └── 任务卡片列表
│           └── 任务卡片 × N
└── 任务详情弹窗
    ├── 基本信息
    ├── 子任务
    ├── 评论区
    └── 活动历史
```

---

## 4. Mock 数据

### 4.1 任务数据结构
```javascript
{
  id: 1,
  title: '完成用户认证模块',
  description: '实现登录、注册、找回密码功能',
  status: 'in_progress',
  priority: 'high',  // high/medium/low
  assignee: {
    id: 1,
    name: '张经理',
    avatar: '...'
  },
  dueDate: '2026-02-15',
  tags: ['开发', '后端'],
  subtasks: [
    { id: 1, title: '设计数据库', completed: true },
    { id: 2, title: '编写API', completed: false }
  ],
  comments: [
    { id: 1, user: '李开发', content: 'API已提交测试', time: '2小时前' }
  ]
}
```

### 4.2 看板列结构
```javascript
const columns = [
  { id: 'todo', title: '待办', status: 'todo' },
  { id: 'in_progress', title: '进行中', status: 'in_progress' },
  { id: 'done', title: '已完成', status: 'done' }
]
```

---

## 5. 实施步骤

### Step 1: 创建基础页面结构
- [ ] 创建 Board.vue 模板
- [ ] 定义路由
- [ ] 添加到侧边栏

### Step 2: 实现看板布局
- [ ] 看板列样式
- [ ] 卡片样式
- [ ] 响应式适配

### Step 3: 实现拖拽功能
- [ ] 使用 Element Plus 的 Sortable
- [ ] 拖拽逻辑
- [ ] 状态更新

### Step 4: 实现任务详情弹窗
- [ ] 弹窗布局
- [ ] 详情展示
- [ ] 子任务管理

### Step 5: 实现新建/编辑功能
- [ ] 新建任务表单
- [ ] 编辑任务表单
- [ ] 表单验证

---

## 6. 依赖

- Element Plus Sortable（需要安装 `sortablejs`）
- 或使用 Element Plus 的 `el-draggable-plus`

```bash
npm install sortablejs --break-system-packages
```

---

## 7. 验收标准

- [ ] 页面布局符合设计规范
- [ ] 任务卡片可拖拽
- [ ] 拖拽后状态正确更新
- [ ] 新建任务功能正常
- [ ] 点击任务显示详情
- [ ] 响应式适配移动端

---

## 8. 预计工时

- 基础布局：2 小时
- 拖拽功能：3 小时
- 详情弹窗：2 小时
- 新建/编辑：2 小时
- 测试修复：1 小时

**总计：约 10 小时**
