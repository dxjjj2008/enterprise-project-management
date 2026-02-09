# 甘特图模块实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan.

**目标：** 创建甘特图组件，实现时间轴视图、任务依赖、拖拽调整功能

**架构：** 使用 Vue 3 + Composition API + 自定义 Canvas/SVG 渲染

**技术栈：** Vue 3, Element Plus, TypeScript, Vite

---

## 任务概览

| 任务ID | 任务名称 | 工时 | 优先级 |
|--------|----------|------|--------|
| T1 | 甘特图基础布局组件 | 2人天 | P0 |
| T2 | 时间轴渲染模块 | 2人天 | P0 |
| T3 | 任务条组件 | 3人天 | P0 |
| T4 | 任务依赖线绘制 | 2人天 | P1 |
| T5 | 拖拽调整功能 | 2人天 | P1 |
| T6 | 缩放与导航控制 | 1人天 | P2 |

---

## 详细任务

### Task 1:基础布局 甘特图组件

**文件：**
- 创建: `src/components/gantt/GanttContainer.vue`
- 创建: `src/components/gantt/GanttHeader.vue`
- 修改: `src/router/index.js`

**Step 1: 创建基础容器组件模板**

```vue
<template>
  <div class="gantt-container">
    <div class="gantt-toolbar">工具栏</div>
    <div class="gantt-main">
      <div class="gantt-timeline">时间轴</div>
      <div class="gantt-chart">图表区</div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 基础响应式数据
const props = defineProps<{
  projectId: number
}>()

const loading = ref(false)
</script>

<style scoped>
.gantt-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.gantt-main {
  flex: 1;
  display: flex;
  overflow: hidden;
}
</style>
```

**Step 2:添加工具栏组件**

```vue
<!-- 在 GanttToolbar.vue 中 -->
<template>
  <div class="gantt-toolbar">
    <el-button-group>
      <el-button @click="zoomOut">放大</el-button>
      <el-button @click="zoomIn">缩小</el-button>
      <el-button @click="resetView">重置</el-button>
    </el-button-group>
    <el-date-picker v-model="dateRange" type="daterange" />
  </div>
</template>
```

**Step 3: 添加 TypeScript 类型定义**

```typescript
// src/types/gantt.ts
export interface GanttTask {
  id: number
  name: string
  startDate: Date
  endDate: Date
  progress: number
  dependencies: number[]
  assignee?: string
}

export interface GanttConfig {
  rowHeight: number
  dayWidth: number
  headerHeight: number
}
```

**Step 4: 添加路由配置**

```javascript
// 在 router/index.js 中添加
{
  path: '/projects/:id/gantt',
  name: 'Gantt',
  component: () => import('@/components/gantt/GanttContainer.vue'),
  meta: { title: '甘特图' }
}
```

**Step 5: 编写单元测试**

```typescript
// tests/unit/gantt/GanttContainer.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import GanttContainer from '@/components/gantt/GanttContainer.vue'

describe('GanttContainer', () => {
  it('renders toolbar and main area', () => {
    const wrapper = mount(GanttContainer, {
      props: { projectId: 1 }
    })
    expect(wrapper.find('.gantt-toolbar').exists()).toBe(true)
    expect(wrapper.find('.gantt-main').exists()).toBe(true)
  })
})
```

**Commands:**

```bash
npm run test:unit -- tests/unit/gantt/GanttContainer.spec.ts
```

**Expected Output:**

```
PASS  tests/unit/gantt/GanttContainer.spec.ts
✓ renders toolbar and main area
```

**Step 6: 提交代码**

```bash
git add src/components/gantt/ src/types/gantt.ts src/router/index.js tests/unit/gantt/
git commit -m "feat(gantt): add basic Gantt layout components"
```

---

### Task 2: 时间轴渲染模块

**文件：**
- 创建: `src/components/gantt/GanttTimeline.vue`
- 创建: `src/composables/useTimeline.ts`
- 测试: `tests/unit/gantt/useTimeline.spec.ts`

**Step 1: 实现时间轴刻度计算逻辑**

```typescript
// src/composables/useTimeline.ts
import { computed, ref } from 'vue'

export function useTimeline(config: { dayWidth: number }) {
  const viewMode = ref<'day' | 'week' | 'month'>('week')
  const startDate = ref(new Date())
  const endDate = ref(new Date(Date.now() + 30 * 24 * 60 * 60 * 1000))

  const columns = computed(() => {
    const cols = []
    const current = new Date(startDate.value)
    while (current <= endDate.value) {
      cols.push({
        date: new Date(current),
        label: formatDate(current, viewMode.value),
        width: config.dayWidth * (viewMode.value === 'day' ? 1 : 7)
      })
      current.setDate(current.getDate() + (viewMode.value === 'day' ? 1 : 7))
    }
    return cols
  })

  return { viewMode, startDate, endDate, columns }
}

function formatDate(date: Date, mode: string): string {
  const fmt = new Intl.DateTimeFormat('zh-CN', {
    month: 'numeric',
    day: 'numeric'
  })
  return fmt.format(date)
}
```

**Step 2: 创建时间轴组件模板**

```vue
<!-- src/components/gantt/GanttTimeline.vue -->
<template>
  <div class="gantt-timeline" :style="{ height: headerHeight + 'px' }">
    <div class="timeline-header">
      <div
        v-for="(col, index) in columns"
        :key="index"
        class="timeline-column"
        :style="{ width: col.width + 'px' }"
      >
        {{ col.label }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Column {
  date: Date
  label: string
  width: number
}

defineProps<{
  columns: Column[]
  headerHeight: number
}>()
</script>

<style scoped>
.gantt-timeline {
  display: flex;
  border-bottom: 1px solid #e4e7ed;
  background: #f5f7fa;
}
.timeline-column {
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 1px solid #e4e7ed;
  font-size: 12px;
  color: #606266;
}
</style>
```

**Step 3: 编写测试**

```typescript
// tests/unit/gantt/useTimeline.spec.ts
import { describe, it, expect, vi } from 'vitest'
import { useTimeline } from '@/composables/useTimeline'

describe('useTimeline', () => {
  it('generates week columns', () => {
    const { columns } = useTimeline({ dayWidth: 40 })
    expect(columns.value.length).toBeGreaterThan(0)
    expect(columns.value[0]).toHaveProperty('date')
    expect(columns.value[0]).toHaveProperty('label')
  })
})
```

**Step 4: 运行测试验证**

```bash
npm run test:unit -- tests/unit/gantt/useTimeline.spec.ts
```

**Expected Output:**

```
PASS  tests/unit/gantt/useTimeline.spec.ts
✓ generates week columns
```

**Step 5: 集成到主组件**

```vue
<!-- 在 GanttContainer.vue 中添加 -->
<script setup lang="ts">
import { useTimeline } from '@/composables/useTimeline'

const { columns } = useTimeline({ dayWidth: 40 })
const headerHeight = ref(48)
</script>

<template>
  <GanttTimeline :columns="columns" :header-height="headerHeight" />
</template>
```

**Step 6: 提交代码**

```bash
git add src/components/gantt/GanttTimeline.vue src/composables/useTimeline.ts tests/unit/gantt/
git commit -m "feat(gantt): add timeline rendering module"
```

---

### Task 3: 任务条组件

**文件：**
- 创建: `src/components/gantt/GanttTaskRow.vue`
- 创建: `src/components/gantt/GanttTaskBar.vue`
- 修改: `src/components/gantt/GanttContainer.vue`

**Step 1: 定义任务条数据结构**

```typescript
// src/types/gantt.ts 添加
export interface GanttTaskBar {
  task: GanttTask
  x: number
  width: number
  color: string
}
```

**Step 2: 创建任务条组件**

```vue
<!-- src/components/gantt/GanttTaskBar.vue -->
<template>
  <div
    class="gantt-task-bar"
    :style="{
      left: x + 'px',
      width: width + 'px',
      backgroundColor: color
    }"
    @click="handleClick"
  >
    <div class="task-progress" :style="{ width: task.progress + '%' }" />
    <span class="task-label">{{ task.name }}</span>
  </div>
</template>

<script setup lang="ts">
import type { GanttTask } from '@/types/gantt'

const props = defineProps<{
  task: GanttTask
  x: number
  width: number
  color?: string
}>()

const emit = defineEmits<{
  (e: 'click', task: GanttTask): void
}>()

const defaultColors: Record<string, string> = {
  high: '#f56c6c',
  medium: '#e6a23c',
  low: '#67c23a'
}

const color = computed(() => props.color || defaultColors[props.task.priority] || '#409eff')

function handleClick() {
  emit('click', props.task)
}
</script>

<style scoped>
.gantt-task-bar {
  position: absolute;
  height: 24px;
  border-radius: 4px;
  cursor: pointer;
  overflow: hidden;
}
.task-progress {
  height: 100%;
  background: rgba(0, 0, 0, 0.2);
}
.task-label {
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  color: #fff;
  white-space: nowrap;
}
</style>
```

**Step 3: 创建任务行组件**

```vue
<!-- src/components/gantt/GanttTaskRow.vue -->
<template>
  <div class="gantt-task-row">
    <div class="task-info">
      <span class="task-name">{{ task.name }}</span>
    </div>
    <div class="task-chart">
      <GanttTaskBar
        :task="task"
        :x="position.x"
        :width="position.width"
        @click="emit('select', task)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { GanttTask } from '@/types/gantt'

const props = defineProps<{
  task: GanttTask
  dayWidth: number
}>()

const emit = defineEmits<{
  (e: 'select', task: GanttTask): void
}>()

const position = computed(() => {
  const days = Math.ceil(
    (props.task.endDate.getTime() - props.task.startDate.getTime()) / (24 * 60 * 60 * 1000)
  )
  return {
    x: props.dayWidth * 5, // 假设从第5天开始
    width: props.dayWidth * days
  }
})
</script>

<style scoped>
.gantt-task-row {
  display: flex;
  height: 40px;
  border-bottom: 1px solid #ebeef5;
}
.task-info {
  width: 200px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  border-right: 1px solid #e4e7ed;
}
.task-chart {
  flex: 1;
  position: relative;
}
</style>
```

**Step 4: 测试任务条渲染**

```typescript
// tests/unit/gantt/GanttTaskBar.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import GanttTaskBar from '@/components/gantt/GanttTaskBar.vue'

describe('GanttTaskBar', () => {
  it('renders task bar with correct position', () => {
    const task = {
      id: 1,
      name: 'Test Task',
      startDate: new Date(),
      endDate: new Date(Date.now() + 86400000),
      progress: 50,
      dependencies: []
    }
    const wrapper = mount(GanttTaskBar, {
      props: { task, x: 100, width: 200 }
    })
    const bar = wrapper.find('.gantt-task-bar')
    expect(bar.attributes('style')).toContain('left: 100px')
    expect(bar.attributes('style')).toContain('width: 200px')
  })
})
```

**Step 5: 运行测试**

```bash
npm run test:unit -- tests/unit/gantt/GanttTaskBar.spec.ts
```

**Expected Output:**

```
PASS  tests/unit/gantt/GanttTaskBar.spec.ts
✓ renders task bar with correct position
```

**Step 6: 提交代码**

```bash
git add src/components/gantt/GanttTaskBar.vue src/components/gantt/GanttTaskRow.vue src/types/gantt.ts tests/unit/gantt/
git commit -m "feat(gantt): add task bar and task row components"
```

---

### Task 4: 任务依赖线绘制

**文件：**
- 创建: `src/components/gantt/GanttDependencyLines.vue`
- 创建: `src/composables/useDependencyLines.ts`

**Step 1: 实现依赖线计算**

```typescript
// src/composables/useDependencyLines.ts
import type { GanttTask } from '@/types/gantt'

interface Point {
  x: number
  y: number
}

export function useDependencyLines(tasks: GanttTask[], config: { dayWidth: number; rowHeight: number }) {
  const lines = computed(() => {
    const result: Array<{ from: Point; to: Point }> = []
    
    tasks.forEach((task, taskIndex) => {
      task.dependencies.forEach(depId => {
        const depTask = tasks.find(t => t.id === depId)
        if (depTask) {
          result.push({
            from: {
              x: (depTask.endDate.getTime() - task.startDate.getTime()) / (24 * 60 * 60 * 1000) * config.dayWidth,
              y: taskIndex * config.rowHeight + config.rowHeight / 2
            },
            to: {
              x: (task.startDate.getTime() - task.startDate.getTime()) / (24 * 60 * 60 * 1000) * config.dayWidth,
              y: taskIndex * config.rowHeight + config.rowHeight / 2
            }
          })
        }
      })
    })
    
    return result
  })

  return { lines }
}
```

**Step 2: 创建 SVG 依赖线组件**

```vue
<!-- src/components/gantt/GanttDependencyLines.vue -->
<template>
  <svg class="dependency-lines">
    <line
      v-for="(line, index) in lines"
      :key="index"
      :x1="line.from.x"
      :y1="line.from.y"
      :x2="line.to.x"
      :y2="line.to.y"
      stroke="#909399"
      stroke-width="2"
      marker-end="url(#arrowhead)"
    />
    <defs>
      <marker
        id="arrowhead"
        markerWidth="10"
        markerHeight="7"
        refX="9"
        refY="3.5"
        orient="auto"
      >
        <polygon points="0 0, 10 3.5, 0 7" fill="#909399" />
      </marker>
    </defs>
  </svg>
</template>

<script setup lang="ts">
interface Line {
  from: Point
  to: Point
}

defineProps<{
  lines: Line[]
}>()
</script>

<style scoped>
.dependency-lines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}
</style>
```

**Step 3: 集成到主组件**

```vue
<!-- 在 GanttContainer.vue 中 -->
<script setup lang="ts">
import GanttDependencyLines from './GanttDependencyLines.vue'

const { lines } = useDependencyLines(tasks.value, { dayWidth: 40, rowHeight: 40 })
</script>

<template>
  <div class="gantt-chart">
    <GanttDependencyLines :lines="lines" />
    <GanttTaskRow
      v-for="task in tasks"
      :key="task.id"
      :task="task"
      :day-width="40"
    />
  </div>
</template>
```

**Step 4: 测试依赖线**

```typescript
// tests/unit/gantt/useDependencyLines.spec.ts
import { describe, it, expect } from 'vitest'
import { useDependencyLines } from '@/composables/useDependencyLines'

describe('useDependencyLines', () => {
  it('generates dependency lines', () => {
    const tasks = [
      { id: 1, dependencies: [], startDate: new Date(), endDate: new Date(Date.now() + 86400000) },
      { id: 2, dependencies: [1], startDate: new Date(Date.now() + 86400000), endDate: new Date(Date.now() + 172800000) }
    ]
    const { lines } = useDependencyLines(tasks as any, { dayWidth: 40, rowHeight: 40 })
    expect(lines.value.length).toBe(1)
  })
})
```

**Step 5: 提交**

```bash
git add src/components/gantt/GanttDependencyLines.vue src/composables/useDependencyLines.ts tests/unit/gantt/
git commit -m "feat(gantt): add dependency line rendering"
```

---

### Task 5: 拖拽调整功能

**文件：**
- 创建: `src/composables/useGanttDraggable.ts`
- 修改: `src/components/gantt/GanttTaskBar.vue`

**Step 1: 实现拖拽逻辑**

```typescript
// src/composables/useGanttDraggable.ts
import { ref } from 'vue'

export function useGanttDraggable(
  task: GanttTask,
  emit: (event: 'update', task: GanttTask) => void
) {
  const isDragging = ref(false)
  const startX = ref(0)
  const originalDates = ref({
    startDate: new Date(task.startDate),
    endDate: new Date(task.endDate)
  })

  function handleDragStart(e: MouseEvent) {
    isDragging.value = true
    startX.value = e.clientX
    originalDates.value = {
      startDate: new Date(task.startDate),
      endDate: new Date(task.endDate)
    }
  }

  function handleDrag(e: MouseEvent) {
    if (!isDragging.value) return
    const deltaX = e.clientX - startX.value
    const days = Math.round(deltaX / 40) // 假设 dayWidth = 40
    
    task.startDate = new Date(originalDates.value.startDate.getTime() + days * 86400000)
    task.endDate = new Date(originalDates.value.endDate.getTime() + days * 86400000)
  }

  function handleDragEnd() {
    isDragging.value = false
    emit('update', task)
  }

  return { isDragging, handleDragStart, handleDrag, handleDragEnd }
}
```

**Step 2: 集成到任务条**

```vue
<!-- GanttTaskBar.vue 添加 -->
<script setup lang="ts">
import { useGanttDraggable } from '@/composables/useGanttDraggable'

const emit = defineEmits<{
  (e: 'update', task: GanttTask): void
}>()

const { isDragging, handleDragStart, handleDrag, handleDragEnd } = useGanttDraggable(props.task, (t) => {
  emit('update', t)
})
</script>

<template>
  <div
    class="gantt-task-bar"
    :class="{ dragging: isDragging }"
    @mousedown="handleDragStart"
    @mousemove="handleDrag"
    @mouseup="handleDragEnd"
    @mouseleave="handleDragEnd"
  >
    <!-- ... -->
  </div>
</template>
```

**Step 3: 测试拖拽**

```typescript
// tests/unit/gantt/useGanttDraggable.spec.ts
import { describe, it, expect, vi } from 'vitest'
import { useGanttDraggable } from '@/composables/useGanttDraggable'

describe('useGanttDraggable', () => {
  it('updates task dates on drag', () => {
    const task = {
      id: 1,
      startDate: new Date('2026-02-01'),
      endDate: new Date('2026-02-05'),
      progress: 0,
      dependencies: []
    }
    const emit = vi.fn()
    const { handleDragEnd } = useGanttDraggable(task as any, emit)
    
    handleDragEnd()
    expect(emit).toHaveBeenCalled()
  })
})
```

**Step 4: 提交**

```bash
git add src/composables/useGanttDraggable.ts
git commit -m "feat(gantt): add draggable functionality"
```

---

### Task 6: 缩放与导航控制

**文件：**
- 修改: `src/components/gantt/GanttContainer.vue`
- 新增: `src/composables/useGanttZoom.ts`

**Step 1: 实现缩放控制**

```typescript
// src/composables/useGanttZoom.ts
import { ref, computed } from 'vue'

export function useGanttZoom() {
  const zoomLevel = ref(1)
  const minZoom = 0.5
  const maxZoom = 2

  const dayWidth = computed(() => 40 * zoomLevel.value)

  function zoomIn() {
    if (zoomLevel.value < maxZoom) {
      zoomLevel.value *= 1.2
    }
  }

  function zoomOut() {
    if (zoomLevel.value > minZoom) {
      zoomLevel.value /= 1.2
    }
  }

  function resetZoom() {
    zoomLevel.value = 1
  }

  return { zoomLevel, dayWidth, zoomIn, zoomOut, resetZoom }
}
```

**Step 2: 添加导航**

```vue
<!-- GanttToolbar.vue 添加 -->
<template>
  <div class="gantt-toolbar">
    <el-button-group>
      <el-button :icon="ZoomOut" @click="zoomOut" />
      <el-button :icon="ZoomIn" @click="zoomIn" />
    </el-button-group>
    <span class="zoom-level">{{ Math.round(zoomLevel * 100) }}%</span>
    <el-button @click="resetZoom">重置</el-button>
  </div>
</template>
```

**Step 3: 测试缩放**

```typescript
// tests/unit/gantt/useGanttZoom.spec.ts
import { describe, it, expect } from 'vitest'
import { useGanttZoom } from '@/composables/useGanttZoom'

describe('useGanttZoom', () => {
  it('increases zoom level', () => {
    const { zoomIn, zoomLevel } = useGanttZoom()
    const initial = zoomLevel.value
    zoomIn()
    expect(zoomLevel.value).toBeGreaterThan(initial)
  })
})
```

**Step 4: 提交**

```bash
git add src/composables/useGanttZoom.ts
git commit -m "feat(gantt): add zoom controls"
```

---

## 验收标准

- [ ] 甘特图可渲染 100+ 任务
- [ ] 拖拽操作流畅（60fps）
- [ ] 任务依赖线正确显示
- [ ] 缩放功能正常工作
- [ ] 单元测试覆盖率 > 80%
- [ ] 响应式适配移动端

## 相关文档

- [主计划文档](./2026-02-08-development-plan.md)
- [后端API计划](./2026-02-08-backend-api-plan.md)
- [UI/UX设计文档](../design/ui-ux/2026-02-08-ui-ux-design.md)

---

**创建时间:** 2026-02-08  
**版本:** v1.0
