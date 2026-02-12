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
        <div class="timeline-header" :style="{ width: timelineWidth + 'px' }">
          <div class="timeline-months">
            <div
              v-for="month in visibleMonths"
              :key="month.key"
              class="timeline-month"
              :style="{ width: (month.days * dayWidth) + 'px' }"
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
              :style="{ width: dayWidth + 'px' }"
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
            v-for="task in flatTasks"
            :key="task.id"
            class="task-row"
            :class="{ 'is-group': task.isGroup }"
            :style="{ paddingLeft: (task.depth * 20 + 20) + 'px' }"
          >
            <div class="task-info">
              <div class="task-expand" v-if="task.children && task.children.length" @click="toggleTask(task)">
                <el-icon :class="{ expanded: task.expanded }">
                  <ArrowRight />
                </el-icon>
              </div>
              <div class="task-icon" v-else-if="task.isMilestone">
                <el-icon class="milestone-icon"><Star /></el-icon>
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
            <div class="task-timeline" :style="{ width: timelineWidth + 'px' }">
              <!-- 背景网格 -->
              <div class="timeline-grid">
                <div
                  v-for="day in visibleDays"
                  :key="day.date"
                  class="grid-cell"
                  :class="{ weekend: day.isWeekend }"
                  :style="{ width: dayWidth + 'px' }"
                />
              </div>
              <!-- 任务条 -->
              <div
                v-if="task.startDate && task.endDate && !task.isMilestone"
                class="task-bar"
                :class="['priority-' + task.priority, { 'is-milestone': task.isMilestone }]"
                :style="getTaskBarStyle(task)"
                @click="editTask(task)"
              >
                <div class="task-bar-progress" :style="{ width: (task.progress || 0) + '%' }" />
                <span class="task-bar-label" v-if="getTaskDuration(task) > 1">{{ task.name }}</span>
              </div>
              <!-- 里程碑 -->
              <div
                v-if="task.isMilestone"
                class="milestone-marker"
                :style="{ left: getMilestonePosition(task.endDate) + 'px' }"
              >
                <el-icon><Star /></el-icon>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 今日线 -->
      <div class="today-line" :style="{ left: todayPosition + 'px' }">
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
import { Plus, ZoomIn, ZoomOut, Download, FullScreen, ArrowRight, Star } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 响应式数据
const currentProject = ref(1)
const currentView = ref('week')
const dayWidth = ref(40)
const ganttContainer = ref(null)

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
    const key = year + '-' + month
    if (!monthMap.has(key)) {
      monthMap.set(key, {
        key: key,
        label: month + '月',
        days: 0
      })
    }
    const item = monthMap.get(key)
    if (item) item.days++
  })

  monthMap.forEach(value => months.push(value))
  return months
})

const timelineWidth = computed(() => visibleDays.value.length * dayWidth.value)

const todayDate = computed(() => {
  return new Date().toISOString().split('T')[0]
})

const todayPosition = computed(() => {
  const today = todayDate.value
  const index = visibleDays.value.findIndex(d => d.date === today)
  return index >= 0 ? index * dayWidth.value + dayWidth.value / 2 : 0
})

// 扁平化任务列表（支持展开/折叠）
const flatTasks = computed(() => {
  const result = []

  const processTask = (task, depth = 0) => {
    result.push({
      ...task,
      depth: depth,
      expanded: expandedTasks.has(task.id)
    })
    if (task.children && expandedTasks.has(task.id)) {
      task.children.forEach(child => processTask(child, depth + 1))
    }
  }

  tasks.forEach(task => processTask(task))
  return result
})

const completedCount = computed(() => {
  return flatTasks.value.filter(t => !t.isGroup && t.progress === 100).length
})

const inProgressCount = computed(() => {
  return flatTasks.value.filter(t => !t.isGroup && t.progress > 0 && t.progress < 100).length
})

const overallProgress = computed(() => {
  const leafTasks = flatTasks.value.filter(t => !t.children || t.children.length === 0)
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

const getTaskDuration = (task) => {
  if (!task.startDate || !task.endDate) return 0
  const start = new Date(task.startDate)
  const end = new Date(task.endDate)
  return Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1
}

const getTaskBarStyle = (task) => {
  const startIndex = visibleDays.value.findIndex(d => d.date === task.startDate)
  const endIndex = visibleDays.value.findIndex(d => d.date === task.endDate)

  if (startIndex === -1) return { display: 'none' }

  const left = startIndex * dayWidth.value
  const width = Math.max((endIndex - startIndex + 1) * dayWidth.value, dayWidth.value)

  return {
    left: left + 'px',
    width: width + 'px'
  }
}

const getMilestonePosition = (date) => {
  const index = visibleDays.value.findIndex(d => d.date === date)
  return index >= 0 ? index * dayWidth.value + dayWidth.value / 2 : 0
}

const toggleTask = (task) => {
  if (expandedTasks.has(task.id)) {
    expandedTasks.delete(task.id)
  } else {
    expandedTasks.add(task.id)
  }
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
  ElMessage.info('编辑任务: ' + task.name)
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

<style scoped>
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
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.breadcrumb {
  font-size: 14px;
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
}

.toolbar-left {
  display: flex;
  gap: 12px;
}

.project-select {
  width: 200px;
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
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  border-right: 1px solid #ebeef5;
  text-align: center;
}

.timeline-days {
  display: flex;
}

.timeline-day {
  padding: 4px;
  font-size: 12px;
  color: #909399;
  text-align: center;
  border-right: 1px solid #f0f2f5;
}

.timeline-day.weekend {
  background-color: #fafafa;
  color: #c0c4cc;
}

.gantt-body {
  position: relative;
}

.task-row {
  display: flex;
  align-items: center;
  border-bottom: 1px solid #f0f2f5;
  transition: background-color 0.2s;
}

.task-row:hover {
  background-color: #f5f7fa;
}

.task-row.is-group {
  background-color: #fafafa;
  font-weight: 500;
}

.task-info {
  width: 280px;
  min-width: 280px;
  display: flex;
  align-items: center;
  padding: 8px 16px;
  border-right: 1px solid #ebeef5;
  position: sticky;
  left: 0;
  background-color: #fff;
  z-index: 5;
}

.task-expand {
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.task-expand .expanded {
  transform: rotate(90deg);
}

.task-icon {
  width: 20px;
  height: 20px;
}

.milestone-icon {
  color: #e6a23c;
}

.task-checkbox {
  margin-right: 8px;
}

.task-priority {
  margin-right: 8px;
}

.task-name {
  font-size: 14px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-timeline {
  position: relative;
  height: 48px;
  display: flex;
  align-items: center;
}

.timeline-grid {
  position: absolute;
  top: 0;
  left: 0;
  display: flex;
  height: 100%;
}

.grid-cell {
  height: 100%;
  border-right: 1px solid #f0f2f5;
}

.grid-cell.weekend {
  background-color: #fafafa;
}

.task-bar {
  position: absolute;
  height: 28px;
  border-radius: 4px;
  cursor: pointer;
  overflow: hidden;
  display: flex;
  align-items: center;
  padding: 0 8px;
  transition: box-shadow 0.2s;
}

.task-bar:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.task-bar.priority-high {
  background: linear-gradient(135deg, #f56c6c 0%, #e6a23c 100%);
  color: #fff;
}

.task-bar.priority-medium {
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  color: #fff;
}

.task-bar.priority-low {
  background: linear-gradient(135deg, #909399 0%, #606266 100%);
  color: #fff;
}

.task-bar-progress {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.3);
}

.task-bar-label {
  position: relative;
  z-index: 1;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.milestone-marker {
  position: absolute;
  transform: translateX(-50%);
  color: #e6a23c;
  font-size: 16px;
}

.today-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 2px;
  background-color: #f56c6c;
  z-index: 20;
}

.today-label {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #f56c6c;
  color: #fff;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 2px;
  white-space: nowrap;
}

.gantt-footer {
  display: flex;
  gap: 32px;
  padding: 16px 24px;
  background-color: #fff;
  border-radius: 8px;
  margin-top: 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.footer-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.footer-item .label {
  font-size: 14px;
  color: #606266;
}

.footer-item .value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.footer-item .value.completed {
  color: #67c23a;
}

.footer-item .value.in-progress {
  color: #409eff;
}

.footer-item .value.progress {
  color: #e6a23c;
}
</style>
