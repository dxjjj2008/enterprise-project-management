<template>
  <div class="gantt-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">甘特图</h2>
        <el-breadcrumb separator="/" class="breadcrumb">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item>项目管理</el-breadcrumb-item>
          <el-breadcrumb-item>甘特图</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="createTask">新建任务</el-button>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-select v-model="currentProject" placeholder="选择项目" class="project-select">
          <el-option
            v-for="project in projects"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          />
        </el-select>
        <el-button-group class="view-switcher">
          <el-button :type="currentView === 'day' ? 'primary' : ''" @click="currentView = 'day'">日</el-button>
          <el-button :type="currentView === 'week' ? 'primary' : ''" @click="currentView = 'week'">周</el-button>
          <el-button :type="currentView === 'month' ? 'primary' : ''" @click="currentView = 'month'">月</el-button>
        </el-button-group>
      </div>
      <div class="toolbar-right">
        <el-button :icon="ZoomIn" circle @click="zoomIn" />
        <el-button :icon="ZoomOut" circle @click="zoomOut" />
        <el-button :icon="Download" circle @click="exportGantt" />
        <el-button :icon="FullScreen" circle @click="toggleFullscreen" />
      </div>
    </div>

    <!-- 甘特图主体 -->
    <div class="gantt-container" ref="ganttContainer">
      <!-- 时间轴头部 -->
      <div class="gantt-header">
        <div class="task-name-header">任务名称</div>
        <div class="timeline-header" :style="{ width: `${timelineWidth}px` }">
          <div class="timeline-months">
            <div
              v-for="month in visibleMonths"
              :key="month.key"
              class="timeline-month"
              :style="{ width: `${month.days * dayWidth}px` }"
            >
              {{ month.label }}
            </div>
          </div>
          <div class="timeline-days">
            <div
              v-for="day in visibleDays"
              :key="day.date"
              class="timeline-day"
              :class="{ weekend: day.isWeekend }"
              :style="{ width: `${dayWidth}px` }"
            >
              {{ day.day }}
            </div>
          </div>
        </div>
      </div>

      <!-- 任务列表 -->
      <div class="gantt-body">
        <div class="task-list">
          <div
            v-for="task in tasks"
            :key="task.id"
            class="task-row"
            :class="{ 'is-group': task.isGroup }"
          >
            <div class="task-info">
              <div class="task-expand" v-if="task.children?.length" @click="toggleTask(task)">
                <el-icon :class="{ expanded: task.expanded }">
                  <ArrowRight />
                </el-icon>
              </div>
              <div class="task-icon" v-else></div>
              <el-checkbox
                v-model="task.selected"
                @change="handleTaskSelect(task)"
                class="task-checkbox"
              />
              <el-tag :type="getPriorityType(task.priority)" size="small" class="task-priority">
                {{ getPriorityLabel(task.priority) }}
              </el-tag>
              <span class="task-name">{{ task.name }}</span>
            </div>
            <div class="task-timeline" :style="{ width: `${timelineWidth}px` }">
              <!-- 背景网格 -->
              <div class="timeline-grid">
                <div
                  v-for="day in visibleDays"
                  :key="day.date"
                  class="grid-cell"
                  :class="{ weekend: day.isWeekend }"
                  :style="{ width: `${dayWidth}px` }"
                />
              </div>
              <!-- 任务条 -->
              <div
                v-if="task.startDate && task.endDate"
                class="task-bar"
                :class="[`priority-${task.priority}`, { 'is-milestone': task.isMilestone }]"
                :style="getTaskBarStyle(task)"
                @click="editTask(task)"
              >
                <div class="task-bar-progress" :style="{ width: `${task.progress || 0}%` }" />
                <span class="task-bar-label" v-if="task.duration > 1">{{ task.name }}</span>
              </div>
              <!-- 里程碑 -->
              <div
                v-if="task.isMilestone"
                class="milestone-marker"
                :style="{ left: `${getMilestonePosition(task.endDate)}px` }"
              />
              <!-- 依赖线 -->
              <svg v-if="task.dependencies?.length" class="dependency-lines">
                <path
                  v-for="depId in task.dependencies"
                  :key="depId"
                  :d="getDependencyPath(task, depId)"
                  class="dependency-line"
                />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- 今日线 -->
      <div class="today-line" :style="{ left: `${todayPosition}px` }">
        <div class="today-label">今天</div>
      </div>
    </div>

    <!-- 底部统计 -->
    <div class="gantt-footer">
      <div class="footer-item">
        <span class="label">任务总数：</span>
        <span class="value">{{ tasks.length }}</span>
      </div>
      <div class="footer-item">
        <span class="label">已完成：</span>
        <span class="value completed">{{ completedCount }}</span>
      </div>
      <div class="footer-item">
        <span class="label">进行中：</span>
        <span class="value in-progress">{{ inProgressCount }}</span>
      </div>
      <div class="footer-item">
        <span class="label">总进度：</span>
        <span class="value progress">{{ overallProgress }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { Plus, ZoomIn, ZoomOut, Download, FullScreen, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 响应式数据
const currentProject = ref(1)
const currentView = ref('week')
const dayWidth = ref(40)
const ganttContainer = ref(null)
const expandedTasks = reactive(new Set())

// 项目列表
const projects = ref([
  { id: 1, name: '企业项目管理系统' },
  { id: 2, name: '移动端应用开发' },
  { id: 3, name: '数据分析平台' }
])

// 任务列表
const tasks = reactive([
  {
    id: 1,
    name: '需求分析',
    startDate: '2026-02-01',
    endDate: '2026-02-05',
    progress: 100,
    priority: 'high',
    isGroup: true,
    selected: false,
    expanded: true,
    children: [
      { id: 11, name: '用户调研', startDate: '2026-02-01', endDate: '2026-02-02', progress: 100, priority: 'medium', selected: false },
      { id: 12, name: '需求文档', startDate: '2026-02-03', endDate: '2026-02-05', progress: 100, priority: 'high', selected: false }
    ]
  },
  {
    id: 2,
    name: '系统设计',
    startDate: '2026-02-06',
    endDate: '2026-02-12',
    progress: 80,
    priority: 'high',
    isGroup: true,
    selected: false,
    expanded: true,
    children: [
      { id: 21, name: '架构设计', startDate: '2026-02-06', endDate: '2026-02-08', progress: 100, priority: 'high', selected: false },
      { id: 22, name: '数据库设计', startDate: '2026-02-09', endDate: '2026-02-10', progress: 80, priority: 'medium', selected: false },
      { id: 23, name: '接口设计', startDate: '2026-02-11', endDate: '2026-02-12', progress: 60, priority: 'medium', selected: false }
    ]
  },
  {
    id: 3,
    name: '前端开发',
    startDate: '2026-02-13',
    endDate: '2026-02-25',
    progress: 40,
    priority: 'high',
    isGroup: true,
    selected: false,
    expanded: false,
    children: [
      { id: 31, name: '页面开发', startDate: '2026-02-13', endDate: '2026-02-20', progress: 50, priority: 'medium', selected: false },
      { id: 32, name: '组件封装', startDate: '2026-02-18', endDate: '2026-02-23', progress: 30, priority: 'medium', selected: false },
      { id: 33, name: '联调测试', startDate: '2026-02-24', endDate: '2026-02-25', progress: 0, priority: 'high', selected: false }
    ]
  },
  {
    id: 4,
    name: '后端开发',
    startDate: '2026-02-13',
    endDate: '2026-02-28',
    progress: 30,
    priority: 'high',
    isGroup: true,
    selected: false,
    expanded: false,
    children: [
      { id: 41, name: 'API开发', startDate: '2026-02-13', endDate: '2026-02-22', progress: 40, priority: 'medium', selected: false },
      { id: 42, name: '数据库实现', startDate: '2026-02-15', endDate: '2026-02-19', progress: 60, priority: 'high', selected: false },
      { id: 43, name: '业务逻辑', startDate: '2026-02-20', endDate: '2026-02-28', progress: 10, priority: 'medium', selected: false }
    ]
  },
  {
    id: 5,
    name: '测试验收',
    startDate: '2026-02-26',
    endDate: '2026-03-05',
    progress: 0,
    priority: 'high',
    isGroup: true,
    selected: false,
    expanded: false,
    children: [
      { id: 51, name: '单元测试', startDate: '2026-02-26', endDate: '2026-03-01', progress: 0, priority: 'medium', selected: false },
      { id: 52, name: '集成测试', startDate: '2026-03-02', endDate: '2026-03-04', progress: 0, priority: 'high', selected: false },
      { id: 53, name: 'UAT验收', startDate: '2026-03-05', endDate: '2026-03-05', progress: 0, priority: 'high', isMilestone: true, selected: false }
    ]
  },
  {
    id: 6,
    name: '里程碑：项目上线',
    startDate: '2026-03-10',
    endDate: '2026-03-10',
    progress: 0,
    priority: 'high',
    isMilestone: true,
    selected: false
  }
])

// 计算属性
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

const visibleMonths = computed(() => {
  const months = []
  const monthMap = new Map()
  
  visibleDays.value.forEach(day => {
    const [year, month] = day.date.split('-')
    const key = `${year}-${month}`
    if (!monthMap.has(key)) {
      monthMap.set(key, {
        key,
        label: `${month}月`,
        days: 0
      })
    }
    monthMap.get(key).days++
  })
  
  monthMap.forEach(value => months.push(value))
  return months
})

const timelineWidth = computed(() => visibleDays.value.length * dayWidth.value)

const todayPosition = computed(() => {
  const today = '2026-02-09'
  const index = visibleDays.value.findIndex(d => d.date === today)
  return index >= 0 ? index * dayWidth.value + dayWidth.value / 2 : 0
})

const completedCount = computed(() => {
  return tasks.filter(t => !t.isGroup && t.progress === 100).length
})

const inProgressCount = computed(() => {
  return tasks.filter(t => !t.isGroup && t.progress > 0 && t.progress < 100).length
})

const overallProgress = computed(() => {
  const leafTasks = tasks.filter(t => !t.children)
  if (leafTasks.length === 0) return 0
  const total = leafTasks.reduce((sum, t) => sum + (t.progress || 0), 0)
  return Math.round(total / leafTasks.length)
})

// 方法
const getPriorityType = (priority) => {
  const types = { high: 'danger', medium: 'warning', low: 'info' }
  return types[priority] || 'info'
}

const getPriorityLabel = (priority) => {
  const labels = { high: '高', medium: '中', low: '低' }
  return labels[priority] || '-'
}

const getTaskBarStyle = (task) => {
  const startIndex = visibleDays.value.findIndex(d => d.date === task.startDate)
  const endIndex = visibleDays.value.findIndex(d => d.date === task.endDate)
  
  if (startIndex === -1) return { display: 'none' }
  
  const left = startIndex * dayWidth.value
  const width = Math.max((endIndex - startIndex + 1) * dayWidth.value, dayWidth.value)
  
  return {
    left: `${left}px`,
    width: `${width}px`
  }
}

const getMilestonePosition = (date) => {
  const index = visibleDays.value.findIndex(d => d.date === date)
  return index >= 0 ? index * dayWidth.value + dayWidth.value / 2 : 0
}

const getDependencyPath = (task, depId) => {
  // 简化版：返回直线
  return ''
}

const toggleTask = (task) => {
  task.expanded = !task.expanded
}

const handleTaskSelect = (task) => {
  console.log('Task selected:', task)
}

const zoomIn = () => {
  dayWidth.value = Math.min(80, dayWidth.value + 10)
}

const zoomOut = () => {
  dayWidth.value = Math.max(20, dayWidth.value - 10)
}

const createTask = () => {
  ElMessage.info('新建任务功能开发中')
}

const editTask = (task) => {
  ElMessage.info(`编辑任务: ${task.name}`)
}

const exportGantt = () => {
  ElMessage.success('甘特图导出功能开发中')
}

const toggleFullscreen = () => {
  if (!ganttContainer.value) return
  
  if (document.fullscreenElement) {
    document.exitFullscreen()
  } else {
    ganttContainer.value.requestFullscreen()
  }
}

onMounted(() => {
  console.log('Gantt component mounted')
})
</script>

<style lang="scss" scoped>
.gantt-page {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  
  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px 0;
  }
  
  .breadcrumb {
    font-size: 14px;
  }
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: #fff;
  border-radius: 8px;
  margin-bottom: 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  
  .toolbar-left {
    display: flex;
    gap: 12px;
    
    .project-select {
      width: 200px;
    }
  }
  
  .toolbar-right {
    display: flex;
    gap: 8px;
  }
}

.gantt-container {
  flex: 1;
  background-color: #fff;
  border-radius: 8px;
  overflow: auto;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  position: relative;
}

.gantt-header {
  display: flex;
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: #fff;
  border-bottom: 1px solid #ebeef5;
}

.task-name-header {
  width: 280px;
  min-width: 280px;
  padding: 12px 16px;
  font-weight: 500;
  color: #606266;
  background-color: #fafafa;
  border-right: 1px solid #ebeef5;
  position: sticky;
  left: 0;
  z-index: 11;
}

.timeline-header {
  display: flex;
  flex-direction: column;
}

.timeline-months {
  display: flex;
  border-bottom: 1px solid #ebeef5;
}

.timeline-month {
  padding: 8px;
  text-align: center;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  background-color: #f5f7fa;
  border-right: 1px solid #ebeef5;
}

.timeline-days {
  display: flex;
}

.timeline-day {
  padding: 4px;
  text-align: center;
  font-size: 12px;
  color: #606266;
  border-right: 1px solid #ebeef5;
  
  &.weekend {
    background-color: #fafafa;
    color: #909399;
  }
}

.gantt-body {
  display: flex;
}

.task-list {
  width: 280px;
  min-width: 280px;
  position: sticky;
  left: 0;
  z-index: 9;
}

.task-row {
  display: flex;
  align-items: center;
  height: 48px;
  border-bottom: 1px solid #ebeef5;
  background-color: #fff;
  
  &:hover {
    background-color: #f5f7fa;
  }
  
  &.is-group {
    background-color: #fafafa;
    font-weight: 500;
  }
}

.task-info {
  display: flex;
  align-items: center;
  width: 280px;
  padding: 0 16px;
}

.task-expand {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  margin-right: 4px;
  
  .el-icon {
    transition: transform 0.2s;
    
    &.expanded {
      transform: rotate(90deg);
    }
  }
}

.task-icon {
  width: 20px;
  margin-right: 4px;
}

.task-checkbox {
  margin-right: 8px;
}

.task-priority {
  margin-right: 8px;
}

.task-name {
  font-size: 13px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-timeline {
  position: relative;
  height: 48px;
}

.timeline-grid {
  display: flex;
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
}

.grid-cell {
  height: 100%;
  border-right: 1px solid #ebeef5;
  
  &.weekend {
    background-color: #fafafa;
  }
}

.task-bar {
  position: absolute;
  top: 10px;
  height: 28px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  overflow: hidden;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }
  
  &.priority-high {
    background: linear-gradient(90deg, #f56c6c, #e6a23c);
  }
  
  &.priority-medium {
    background: linear-gradient(90deg, #409eff, #67c23a);
  }
  
  &.priority-low {
    background: linear-gradient(90deg, #909399, #c0c4cc);
  }
  
  &.is-milestone {
    width: 20px !important;
    height: 20px;
    transform: rotate(45deg);
    background: #f56c6c;
    border-radius: 2px;
  }
}

.task-bar-progress {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.3);
}

.task-bar-label {
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  color: #fff;
  white-space: nowrap;
}

.milestone-marker {
  position: absolute;
  top: 14px;
  width: 16px;
  height: 16px;
  transform: rotate(45deg);
  background-color: #f56c6c;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.dependency-lines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.dependency-line {
  fill: none;
  stroke: #909399;
  stroke-width: 1.5;
  stroke-dasharray: 4;
}

.today-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 2px;
  background-color: #f56c6c;
  z-index: 20;
  
  .today-label {
    position: absolute;
    top: 8px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 11px;
    color: #f56c6c;
    white-space: nowrap;
    background-color: #fef0f0;
    padding: 2px 6px;
    border-radius: 4px;
  }
}

.gantt-footer {
  display: flex;
  gap: 32px;
  padding: 16px 20px;
  background-color: #fff;
  border-radius: 8px;
  margin-top: 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  
  .footer-item {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .label {
      font-size: 14px;
      color: #909399;
    }
    
    .value {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      
      &.completed {
        color: #67c23a;
      }
      
      &.in-progress {
        color: #409eff;
      }
      
      &.progress {
        color: #e6a23c;
      }
    }
  }
}
</style>
