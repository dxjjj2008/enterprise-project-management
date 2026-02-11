<template>
  <div class="page-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">报表统计</h1>
      <div class="header-actions">
        <el-button @click="showExportDialog = true">
          <el-icon><Download /></el-icon>
          导出报表
        </el-button>
      </div>
    </div>

    <!-- 筛选控制栏 -->
    <div class="filter-section">
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        :shortcuts="dateShortcuts"
        style="width: 300px"
        value-format="YYYY-MM-DD"
        @change="handleFilterChange"
      />
      <el-select
        v-model="filters.project_id"
        placeholder="选择项目"
        clearable
        style="width: 200px"
        @change="handleFilterChange"
      >
        <el-option label="全部项目" value="" />
        <el-option
          v-for="project in projectList"
          :key="project.id"
          :label="project.name"
          :value="project.id"
        />
      </el-select>
      <el-button type="primary" @click="handleFilterChange">
        <el-icon><Search /></el-icon>
        查询
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="statistics-cards" v-loading="statsLoading">
      <div class="stat-card" @click="filterByStatus('all')">
        <div class="stat-icon" style="background: #E6F7FF;">
          <el-icon color="#1890FF"><Folder /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.project_total || 0 }}</div>
          <div class="stat-label">项目总数</div>
        </div>
      </div>
      <div class="stat-card" @click="filterByStatus('active')">
        <div class="stat-icon" style="background: #F6FFED;">
          <el-icon color="#52C41A"><Loading /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.project_active || 0 }}</div>
          <div class="stat-label">进行中</div>
        </div>
      </div>
      <div class="stat-card" @click="filterByStatus('completed')">
        <div class="stat-icon" style="background: #F9F0FF;">
          <el-icon color="#722ED1"><CircleCheck /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.project_completed || 0 }}</div>
          <div class="stat-label">已完成</div>
        </div>
      </div>
      <div class="stat-card" @click="filterByStatus('overdue')">
        <div class="stat-icon" style="background: #FFF2F0;">
          <el-icon color="#FF4D4F"><WarningFilled /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.project_overdue || 0 }}</div>
          <div class="stat-label">逾期项目</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #FFF7E6;">
          <el-icon color="#FAAD14"><TrendCharts /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.avg_progress || 0 }}%</div>
          <div class="stat-label">平均进度</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="chart-section">
      <el-row :gutter="24">
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="chart-header">
                <span>项目状态分布</span>
                <el-radio-group v-model="pieChartType" size="small" @change="loadPieChartData">
                  <el-radio-button value="pie">饼图</el-radio-button>
                  <el-radio-button value="doughnut">环形图</el-radio-button>
                </el-radio-group>
              </div>
            </template>
            <div class="chart-body" ref="pieChartRef">
              <div v-if="pieChartData.length === 0" class="chart-empty">
                <el-empty description="暂无数据" />
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="chart-header">
                <span>项目进度趋势</span>
              </div>
            </template>
            <div class="chart-body" ref="lineChartRef">
              <div v-if="lineChartData.length === 0" class="chart-empty">
                <el-empty description="暂无数据" />
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      <el-row :gutter="24" style="margin-top: 24px;">
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="chart-header">
                <span>部门项目对比</span>
              </div>
            </template>
            <div class="chart-body" ref="barChartRef">
              <div v-if="barChartData.length === 0" class="chart-empty">
                <el-empty description="暂无数据" />
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="chart-header">
                <span>任务完成情况</span>
              </div>
            </template>
            <div class="chart-body" ref="taskChartRef">
              <div v-if="taskChartData.length === 0" class="chart-empty">
                <el-empty description="暂无数据" />
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 数据表格 -->
    <div class="data-section">
      <el-card shadow="hover">
        <template #header>
          <div class="data-header">
            <el-radio-group v-model="activeTab" @change="handleTabChange">
              <el-radio-button value="project">项目排行</el-radio-button>
              <el-radio-button value="task">任务统计</el-radio-button>
              <el-radio-button value="resource">资源使用</el-radio-button>
            </el-radio-group>
          </div>
        </template>

        <!-- 项目排行表格 -->
        <el-table
          v-if="activeTab === 'project'"
          :data="projectRankData"
          style="width: 100%"
          stripe
          v-loading="tableLoading"
        >
          <el-table-column prop="name" label="项目名称" min-width="200" />
          <el-table-column prop="manager" label="项目经理" width="120" />
          <el-table-column label="进度" width="180">
            <template #default="{ row }">
              <el-progress
                :percentage="row.progress"
                :stroke-width="10"
                :color="getProgressColor(row.progress)"
              />
            </template>
          </el-table-column>
          <el-table-column prop="task_completed" label="已完成任务" width="120" align="center" />
          <el-table-column prop="task_total" label="总任务数" width="100" align="center" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="更新时间" width="160" />
        </el-table>

        <!-- 任务统计表格 -->
        <el-table
          v-if="activeTab === 'task'"
          :data="taskStatsData"
          style="width: 100%"
          stripe
          v-loading="tableLoading"
        >
          <el-table-column prop="name" label="任务名称" min-width="200" />
          <el-table-column prop="project" label="所属项目" width="150" />
          <el-table-column prop="assignee" label="执行人" width="100" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getTaskStatusType(row.status)" size="small">
                {{ getTaskStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="进度" width="150">
            <template #default="{ row }">
              <el-progress
                :percentage="row.progress"
                :stroke-width="10"
                :color="getProgressColor(row.progress)"
              />
            </template>
          </el-table-column>
          <el-table-column prop="due_date" label="截止日期" width="120" />
        </el-table>

        <!-- 资源使用表格 -->
        <el-table
          v-if="activeTab === 'resource'"
          :data="resourceUsageData"
          style="width: 100%"
          stripe
          v-loading="tableLoading"
        >
          <el-table-column prop="name" label="成员姓名" width="120" />
          <el-table-column prop="department" label="所属部门" width="120" />
          <el-table-column prop="project_count" label="参与项目数" width="100" align="center" />
          <el-table-column prop="planned_hours" label="计划工时" width="100" align="center" />
          <el-table-column prop="actual_hours" label="实际工时" width="100" align="center" />
          <el-table-column label="利用率" width="180">
            <template #default="{ row }">
              <el-progress
                :percentage="row.utilization"
                :stroke-width="10"
                :color="getUtilizationColor(row.utilization)"
              />
            </template>
          </el-table-column>
          <el-table-column label="负荷状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getUtilizationStatusType(row.status)" size="small">
                {{ getUtilizationStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container" v-if="pagination.total > pagination.pageSize">
          <el-pagination
            v-model:current-page="pagination.page"
            :page-size="pagination.pageSize"
            :total="pagination.total"
            layout="prev, pager, next, jumper"
            @current-change="handlePageChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 导出弹窗 -->
    <el-dialog
      v-model="showExportDialog"
      title="导出报表"
      width="480px"
      destroy-on-close
    >
      <el-form :model="exportForm" label-width="100px">
        <el-form-item label="报表类型">
          <el-select v-model="exportForm.report_type" style="width: 100%;">
            <el-option label="项目进度报表" value="project_progress" />
            <el-option label="任务完成报表" value="task_completion" />
            <el-option label="资源使用报表" value="resource_usage" />
            <el-option label="部门绩效报表" value="department_performance" />
          </el-select>
        </el-form-item>
        <el-form-item label="导出格式">
          <el-radio-group v-model="exportForm.format">
            <el-radio value="pdf">PDF</el-radio>
            <el-radio value="excel">Excel</el-radio>
            <el-radio value="csv">CSV</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="exportForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 100%;"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="包含图表">
          <el-switch v-model="exportForm.include_charts" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showExportDialog = false">取消</el-button>
        <el-button type="primary" @click="handleExport" :loading="exporting">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Folder, Loading, CircleCheck, WarningFilled, TrendCharts,
  Download, Search
} from '@element-plus/icons-vue'
import { getStatistics, getProjectRank, getTaskStats, getResourceUsage, getDepartmentStats, exportReport } from '@/api/reports'
import { getProjectsForPlan } from '@/api/planning'

// 响应式数据
const statsLoading = ref(false)
const tableLoading = ref(false)
const exporting = ref(false)

const statistics = reactive({
  project_total: 0,
  project_active: 0,
  project_completed: 0,
  project_overdue: 0,
  avg_progress: 0
})

const filters = reactive({
  project_id: '',
  status: ''
})

const dateRange = ref([])

const projectList = ref([])

// 图表数据
const pieChartRef = ref(null)
const lineChartRef = ref(null)
const barChartRef = ref(null)
const taskChartRef = ref(null)
const pieChartType = ref('pie')
const pieChartData = ref([])
const lineChartData = ref([])
const barChartData = ref([])
const taskChartData = ref([])

// 表格数据
const activeTab = ref('project')
const projectRankData = ref([])
const taskStatsData = ref([])
const resourceUsageData = ref([])

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 导出弹窗
const showExportDialog = ref(false)
const exportForm = reactive({
  report_type: 'project_progress',
  format: 'excel',
  dateRange: [],
  include_charts: true
})

// 日期快捷选项
const dateShortcuts = [
  { text: '最近7天', value: () => {
    const end = new Date()
    const start = new Date()
    start.setTime(start.getTime() - 7 * 24 * 60 * 60 * 1000)
    return [start, end]
  }},
  { text: '最近30天', value: () => {
    const end = new Date()
    const start = new Date()
    start.setTime(start.getTime() - 30 * 24 * 60 * 60 * 1000)
    return [start, end]
  }},
  { text: '本月', value: () => {
    const end = new Date()
    const start = new Date(end.getFullYear(), end.getMonth(), 1)
    return [start, end]
  }},
  { text: '上月', value: () => {
    const end = new Date()
    const start = new Date(end.getFullYear(), end.getMonth() - 1, 1)
    end.setDate(0)
    return [start, end]
  }}
]

// 加载统计数据
const loadStatistics = async () => {
  statsLoading.value = true
  try {
    const response = await getStatistics({
      start_date: dateRange.value?.[0],
      end_date: dateRange.value?.[1],
      project_id: filters.project_id || undefined
    })
    Object.assign(statistics, response)
  } catch (error) {
    console.error('加载统计数据失败:', error)
  } finally {
    statsLoading.value = false
  }
}

// 加载图表数据
const loadPieChartData = async () => {
  pieChartData.value = [
    { value: statistics.project_active || 0, name: '进行中' },
    { value: statistics.project_completed || 0, name: '已完成' },
    { value: statistics.project_overdue || 0, name: '已暂停' }
  ]
}

const loadLineChartData = async () => {
  lineChartData.value = [
    { month: '1月', progress: 20 },
    { month: '2月', progress: 35 },
    { month: '3月', progress: 45 },
    { month: '4月', progress: 55 },
    { month: '5月', progress: 68 },
    { month: '6月', progress: 75 }
  ]
}

const loadBarChartData = async () => {
  barChartData.value = [
    { department: '技术部', projects: 8, completed: 3 },
    { department: '产品部', projects: 5, completed: 2 },
    { department: '设计部', projects: 4, completed: 1 },
    { department: '市场部', projects: 3, completed: 1 }
  ]
}

const loadTaskChartData = async () => {
  taskChartData.value = [
    { status: '已完成', count: 45 },
    { status: '进行中', count: 23 },
    { status: '待开始', count: 18 },
    { status: '已逾期', count: 5 }
  ]
}

const loadAllCharts = async () => {
  await Promise.all([
    loadPieChartData(),
    loadLineChartData(),
    loadBarChartData(),
    loadTaskChartData()
  ])
}

// 加载表格数据
const loadProjectRank = async () => {
  tableLoading.value = true
  try {
    const response = await getProjectRank({
      page: pagination.page,
      pageSize: pagination.pageSize,
      start_date: dateRange.value?.[0],
      end_date: dateRange.value?.[1]
    })
    projectRankData.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    console.error('加载项目排行失败:', error)
  } finally {
    tableLoading.value = false
  }
}

const loadTaskStats = async () => {
  tableLoading.value = true
  try {
    const response = await getTaskStats({
      page: pagination.page,
      pageSize: pagination.pageSize,
      project_id: filters.project_id || undefined
    })
    taskStatsData.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    console.error('加载任务统计失败:', error)
  } finally {
    tableLoading.value = false
  }
}

const loadResourceUsage = async () => {
  tableLoading.value = true
  try {
    const response = await getResourceUsage({
      page: pagination.page,
      pageSize: pagination.pageSize
    })
    resourceUsageData.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    console.error('加载资源使用失败:', error)
  } finally {
    tableLoading.value = false
  }
}

const loadTableData = () => {
  switch (activeTab.value) {
    case 'project':
      loadProjectRank()
      break
    case 'task':
      loadTaskStats()
      break
    case 'resource':
      loadResourceUsage()
      break
  }
}

// 加载项目列表
const loadProjects = async () => {
  try {
    const response = await getProjectsForPlan()
    projectList.value = response || []
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
}

// 筛选处理
const handleFilterChange = () => {
  loadStatistics()
  loadAllCharts()
  loadTableData()
}

const handleTabChange = () => {
  pagination.page = 1
  loadTableData()
}

const handlePageChange = (page) => {
  pagination.page = page
  loadTableData()
}

const filterByStatus = (status) => {
  filters.status = status
  handleFilterChange()
}

// 导出处理
const handleExport = async () => {
  exporting.value = true
  try {
    await exportReport({
      report_type: exportForm.report_type,
      format: exportForm.format,
      start_date: exportForm.dateRange?.[0],
      end_date: exportForm.dateRange?.[1],
      include_charts: exportForm.include_charts
    })
    ElMessage.success('报表导出成功')
    showExportDialog.value = false
  } catch (error) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

// 工具方法
const getProgressColor = (progress) => {
  if (!progress || progress === 0) return '#909399'
  if (progress < 30) return '#F56C6C'
  if (progress < 70) return '#E6A23C'
  return '#67C23A'
}

const getStatusType = (status) => {
  const map = {
    active: 'success',
    completed: 'success',
    on_hold: 'warning'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = {
    active: '进行中',
    completed: '已完成',
    on_hold: '已暂停'
  }
  return map[status] || status
}

const getTaskStatusType = (status) => {
  const map = {
    completed: 'success',
    in_progress: 'primary',
    pending: 'info',
    overdue: 'danger'
  }
  return map[status] || 'info'
}

const getTaskStatusLabel = (status) => {
  const map = {
    completed: '已完成',
    in_progress: '进行中',
    pending: '待开始',
    overdue: '已逾期'
  }
  return map[status] || status
}

const getUtilizationColor = (utilization) => {
  if (utilization < 50) return '#FAAD14'
  if (utilization > 100) return '#FF4D4F'
  return '#52C41A'
}

const getUtilizationStatusType = (status) => {
  const map = {
    high: 'danger',
    normal: 'success',
    low: 'info'
  }
  return map[status] || 'info'
}

const getUtilizationStatusLabel = (status) => {
  const map = {
    high: '超负荷',
    normal: '正常',
    low: '偏低'
  }
  return map[status] || status
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadProjects(),
    loadStatistics(),
    loadAllCharts(),
    loadTableData()
  ])
})
</script>

<style scoped>
.page-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filter-section {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.statistics-cards {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #262626;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #595959;
  margin-top: 4px;
}

.chart-section {
  margin-bottom: 24px;
}

.chart-card {
  margin-bottom: 16px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-body {
  height: 280px;
}

.chart-empty {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.data-section {
  margin-top: 24px;
}

.data-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

@media screen and (max-width: 1200px) {
  .statistics-cards {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media screen and (max-width: 768px) {
  .statistics-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media screen and (max-width: 480px) {
  .statistics-cards {
    grid-template-columns: 1fr;
  }

  .filter-section {
    flex-direction: column;
  }

  .filter-section > * {
    width: 100%;
  }
}
</style>
