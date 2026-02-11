# 甘特图模块详细设计文档

> **版本**: v2.0  
> **创建日期**: 2026-02-08  
> **最后更新**: 2026-02-11  
> **状态**: ✅ 已完成

## 1. 功能概述

甘特图模块提供项目任务的时间轴可视化展示，支持任务依赖关系展示、拖拽调整日期、进度追踪等功能。

### 1.1 核心功能

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 时间轴视图 | 支持日/周/月三种视图模式 | P0 |
| 任务条渲染 | 展示任务名称、进度、优先级 | P0 |
| 依赖关系线 | 绘制任务间的依赖关系 | P1 |
| 拖拽调整 | 拖拽任务条调整日期 | P1 |
| 缩放控制 | 调整时间轴缩放级别 | P2 |
| 里程碑标记 | 特殊标记重要节点 | P1 |
| 今日线 | 高亮当前日期位置 | P2 |
| 导出功能 | 导出PNG/PDF/Excel | P2 |

### 1.2 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Gantt Container                         │
│  ┌─────────────┬──────────────────────────────────────────┐ │
│  │   Toolbar  │  时间轴头部 (月份/日期显示)              │ │
│  ├─────────────┼──────────────────────────────────────────┤ │
│  │  任务名称   │  甘特图图表区                            │ │
│  │    列表    │  ┌────────────────────────────────────┐ │ │
│  │             │  │  时间网格 + 任务条 + 依赖线 + 今日线 │ │ │
│  │             │  └────────────────────────────────────┘ │ │
│  └─────────────┴──────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                     底部统计栏                              │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 2. 组件结构

### 2.1 文件结构

```
src/frontend/src/
├── views/projects/
│   ├── Gantt.vue                    # 甘特图主组件 (778行)
│   └── GanttDialog.vue              # 任务创建/编辑对话框
├── api/
│   └── gantt.ts                     # 甘特图 API 客户端
└── types/
    └── gantt.ts                     # TypeScript 类型定义

src/backend/app/api/v1/
└── gantt.py                        # 甘特图后端 API
```

### 2.2 组件职责

| 组件 | 职责 |
|------|------|
| Gantt.vue | 主容器，协调各模块 |
| GanttToolbar | 工具栏（项目选择、视图切换、缩放控制） |
| GanttHeader | 时间轴头部 |
| GanttBody | 任务列表和图表区 |
| GanttTaskRow | 单个任务行 |
| GanttTaskBar | 任务条渲染 |
| GanttDependencyLines | 依赖关系线 |
| GanttTodayLine | 今日位置线 |

## 3. 数据结构

### 3.1 GanttTask 接口

```typescript
interface GanttTask {
  // 基础信息
  id: number
  project_id: number
  parent_id: number | null
  title: string
  description?: string

  // 状态信息
  status: 'todo' | 'in_progress' | 'review' | 'done' | 'archived'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  progress: number  // 0-100

  // 时间信息
  start_date: string | null  // ISO格式
  due_date: string | null
  completed_at?: string

  // 关系信息
  assignee_id?: number
  assignee_name?: string
  assignee_avatar?: string
  dependencies: number[]  // 依赖的任务ID列表

  // 类型标识
  is_milestone: boolean
  is_group: boolean

  // UI状态
  expanded?: boolean
  selected?: boolean
  children?: GanttTask[]
}
```

### 3.2 GanttConfig 配置

```typescript
interface GanttConfig {
  view_mode: 'day' | 'week' | 'month'
  day_width: number        // 默认40px
  row_height: number       // 默认48px
  show_weekends: boolean   // 是否显示周末
  show_today: boolean     // 是否显示今日线
  show_progress: boolean  // 是否显示进度
  show_dependencies: boolean  // 是否显示依赖线
}
```

## 4. API 接口设计

### 4.1 RESTful API

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/projects/{id}/gantt | 获取甘特图任务列表 |
| GET | /api/v1/projects/{id}/gantt/config | 获取甘特图配置 |
| PUT | /api/v1/projects/{id}/gantt/config | 更新甘特图配置 |
| GET | /api/v1/projects/{id}/gantt/stats | 获取甘特图统计 |
| PUT | /api/v1/projects/{id}/tasks/{task_id}/dates | 更新任务日期 |
| PUT | /api/v1/projects/{id}/tasks/{task_id}/progress | 更新任务进度 |
| POST | /api/v1/projects/{id}/tasks/{task_id}/dependencies | 添加任务依赖 |
| DELETE | /api/v1/projects/{id}/tasks/{task_id}/dependencies/{dep_id} | 删除任务依赖 |
| GET | /api/v1/projects/{id}/milestones | 获取里程碑 |
| GET | /api/v1/projects/{id}/gantt/export | 导出甘特图 |

### 4.2 请求/响应示例

#### 获取甘特图任务

```json
// GET /api/v1/projects/1/gantt

Response 200:
{
  "items": [
    {
      "id": 1,
      "title": "需求分析",
      "status": "done",
      "priority": "high",
      "progress": 100,
      "start_date": "2026-02-01",
      "due_date": "2026-02-05",
      "dependencies": [],
      "is_milestone": false,
      "is_group": true,
      "expanded": true
    }
  ]
}
```

## 5. 功能实现详情

### 5.1 时间轴计算

```typescript
// 计算可见日期范围
const visibleDays = computed(() => {
  const days = []
  const start = new Date('2026-02-01')
  const end = new Date('2026-03-15')

  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    days.push({
      date: d.toISOString().split('T')[0],
      day: d.getDate(),
      isWeekend: d.getDay() === 0 || d.getDay() === 6
    })
  }
  return days
})

// 计算月份分组
const visibleMonths = computed(() => {
  const months = []
  const monthMap = new Map()

  visibleDays.value.forEach(day => {
    const [year, month] = day.date.split('-')
    const key = `${year}-${month}`
    if (!monthMap.has(key)) {
      monthMap.set(key, { key, label: `${month}月`, days: 0 })
    }
    monthMap.get(key).days++
  })

  monthMap.forEach(value => months.push(value))
  return months
})
```

### 5.2 任务条位置计算

```typescript
const getTaskBarStyle = (task: GanttTask) => {
  const startIndex = visibleDays.value.findIndex(d => d.date === task.start_date)
  const endIndex = visibleDays.value.findIndex(d => d.date === task.due_date)

  if (startIndex === -1) return { display: 'none' }

  const left = startIndex * dayWidth.value
  const width = Math.max((endIndex - startIndex + 1) * dayWidth.value, dayWidth.value)

  return {
    left: `${left}px`,
    width: `${width}px`
  }
}
```

### 5.3 依赖线绘制

```typescript
interface Point {
  x: number
  y: number
}

interface DependencyLine {
  from: Point
  to: Point
}

const getDependencyPath = (task: GanttTask, depId: number): string => {
  const depTask = tasks.value.find(t => t.id === depId)
  if (!depTask) return ''

  const taskIndex = tasks.value.indexOf(task)
  const depIndex = tasks.value.indexOf(depTask)

  const fromX = (new Date(task.start_date).getTime() - minDate) / dayMs * dayWidth.value
  const toX = (new Date(depTask.start_date).getTime() - minDate) / dayMs * dayWidth.value

  return `M ${fromX} ${taskIndex * 48 + 24}
          L ${fromX + 20} ${taskIndex * 48 + 24}
          L ${fromX + 20} ${depIndex * 48 + 24}
          L ${toX} ${depIndex * 48 + 24}`
}
```

## 6. 界面设计

### 6.1 工具栏布局

```
┌─────────────────────────────────────────────────────────────────────┐
│  [选择项目 ▼]   [日] [周] [月]          [🔍+] [🔎] [↓导出] [⛶]   │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2 任务条样式

```scss
.task-bar {
  position: absolute;
  top: 10px;
  height: 28px;
  border-radius: 4px;
  cursor: pointer;

  // 优先级颜色
  &.priority-high {
    background: linear-gradient(90deg, #f56c6c, #e6a23c);
  }

  &.priority-medium {
    background: linear-gradient(90deg, #409eff, #67c23a);
  }

  &.priority-low {
    background: linear-gradient(90deg, #909399, #c0c4cc);
  }

  // 里程碑样式
  &.is-milestone {
    width: 20px !important;
    height: 20px;
    transform: rotate(45deg);
    background: #f56c6c;
  }
}
```

## 7. 交互设计

### 7.1 拖拽调整

| 操作 | 效果 |
|------|------|
| 拖拽任务条左侧 | 调整开始日期 |
| 拖拽任务条右侧 | 调整结束日期 |
| 拖拽任务条中间 | 同时移动起止日期 |
| 双击任务条 | 打开编辑对话框 |

### 7.2 快捷键

| 快捷键 | 功能 |
|--------|------|
| `+` / `=` | 放大时间轴 |
| `-` | 缩小时间轴 |
| `1` | 日视图 |
| `2` | 周视图 |
| `3` | 月视图 |
| `N` | 新建任务 |
| `Delete` | 删除选中任务 |
| `Enter` | 编辑选中任务 |

## 8. 性能优化

### 8.1 虚拟滚动

对于超过1000个任务的情况，需要实现虚拟滚动：

```typescript
// 只渲染可见区域的任务
const visibleTasks = computed(() => {
  const start = Math.floor(scrollTop.value / rowHeight.value)
  const end = start + Math.ceil(containerHeight.value / rowHeight.value)
  return tasks.value.slice(start, end)
})
```

### 8.2 防抖更新

```typescript
// 拖拽结束后的防抖更新
const debouncedUpdate = debounce((task: GanttTask) => {
  updateTaskDates(task.id, {
    start_date: task.start_date,
    due_date: task.due_date
  })
}, 500)
```

## 9. 测试策略

### 9.1 测试用例

| 测试类型 | 测试内容 |
|----------|----------|
| 单元测试 | 时间轴计算、位置计算、依赖线计算 |
| 组件测试 | 任务条渲染、交互响应 |
| E2E测试 | 完整拖拽流程、API集成 |

### 9.2 测试覆盖目标

- 单元测试覆盖率 > 80%
- 组件测试覆盖主要交互
- E2E测试覆盖核心流程

## 10. 待办事项

| 任务 | 状态 | 预计工时 |
|------|------|----------|
| 甘特图组件基础框架 | ✅ 已完成 | 2h |
| 时间轴渲染 | ✅ 已完成 | 2h |
| 任务条组件 | ✅ 已完成 | 3h |
| 依赖线绘制 | 🔶 进行中 | 2h |
| 拖拽调整功能 | ⏳ 待开始 | 2h |
| API集成 | ⏳ 待开始 | 1h |
| 导出功能完善 | ⏳ 待开始 | 1h |
| 单元测试 | ⏳ 待开始 | 2h |

## 11. 相关文档

| 文档 | 链接 |
|------|------|
| 甘特图实施计划 | [2026-02-08-gantt-chart-plan.md](../../plans/2026-02-08-gantt-chart-plan.md) |
| 用户手册 | [2026-02-08-user-manual.md](../../manual/2026-02-08-user-manual.md) |
| API文档 | [2026-02-08-api.md](../../api/2026-02-08-api.md) |

---

**作者**: 开发团队  
**版本**: v2.0  
**最后更新**: 2026-02-11
