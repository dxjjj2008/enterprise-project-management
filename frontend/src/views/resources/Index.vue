<template>
  <div class="resources-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">资源管理</h1>
        <p class="page-desc">管理团队成员和工作负载分配</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #1E5EB8 0%, #4096FF 100%);">
            <el-icon size="24"><User /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalUsers }}</div>
            <div class="stat-label">团队成员</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #52C41A 0%, #95DE64 100%);">
            <el-icon size="24"><Finished /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.completedTasks }}</div>
            <div class="stat-label">已完成任务</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #FA8C16 0%, #FFC53D 100%);">
            <el-icon size="24"><Loading /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.inProgressTasks }}</div>
            <div class="stat-label">进行中任务</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #F5222D 0%, #FF4D4F 100%);">
            <el-icon size="24"><WarningFilled /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.highWorkload }}</div>
            <div class="stat-label">高负载成员</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 标签页 -->
    <el-tabs v-model="activeTab" class="main-tabs">
      <!-- 工作负载视图 -->
      <el-tab-pane label="工作负载" name="workload">
        <div class="tab-content">
          <!-- 筛选器 -->
          <div class="filter-bar">
            <el-radio-group v-model="workloadFilter" size="default">
              <el-radio-button label="all">全部</el-radio-button>
              <el-radio-button label="high">高负载</el-radio-button>
              <el-radio-button label="medium">中负载</el-radio-button>
              <el-radio-button label="low">低负载</el-radio-button>
            </el-radio-group>
          </div>

          <!-- 工作负载卡片 -->
          <el-row :gutter="16">
            <el-col
              v-for="member in filteredWorkload"
              :key="member.user.id"
              :xs="24" :sm="12" :lg="8" :xl="6"
              class="workload-col"
            >
              <div class="workload-card" @click="viewUserDetail(member.user.id)">
                <div class="card-header">
                  <el-avatar :size="48" :src="member.user.avatar" :alt="member.user.username" loading="lazy">
                    {{ member.user.username?.charAt(0)?.toUpperCase() }}
                  </el-avatar>
                  <div class="user-info">
                    <div class="user-name">{{ member.user.full_name || member.user.username }}</div>
                    <div class="user-username">@{{ member.user.username }}</div>
                  </div>
                  <el-tag
                    :type="getWorkloadTagType(member.workload_level)"
                    size="small"
                  >
                    {{ getWorkloadLabel(member.workload_level) }}
                  </el-tag>
                </div>

                <div class="workload-stats">
                  <div class="stat-row">
                    <span class="stat-label">项目数</span>
                    <span class="stat-value">{{ member.project_count }}</span>
                  </div>
                  <div class="stat-row">
                    <span class="stat-label">总任务</span>
                    <span class="stat-value">{{ member.total_tasks }}</span>
                  </div>
                  <div class="stat-row">
                    <span class="stat-label">已完成</span>
                    <span class="stat-value success">{{ member.completed_tasks }}</span>
                  </div>
                  <div class="stat-row">
                    <span class="stat-label">进行中</span>
                    <span class="stat-value warning">{{ member.in_progress_tasks }}</span>
                  </div>
                </div>

                <el-progress
                  :percentage="member.workload_score"
                  :color="getProgressColor(member.workload_score)"
                  :stroke-width="8"
                  :show-text="false"
                />

                <div class="card-footer">
                  <el-button type="primary" link size="small">
                    查看详情
                    <el-icon><ArrowRight /></el-icon>
                  </el-button>
                </div>
              </div>
            </el-col>
          </el-row>

          <el-empty v-if="filteredWorkload.length === 0" description="暂无数据" />
        </div>
      </el-tab-pane>

      <!-- 成员列表 -->
      <el-tab-pane label="成员列表" name="members">
        <div class="tab-content">
          <el-table
            :data="users"
            v-loading="loading"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="username" label="用户名" width="150">
              <template #default="{ row }">
                <div class="user-cell">
                  <el-avatar :size="32" :src="row.avatar" :alt="row.username" loading="lazy">
                    {{ row.username?.charAt(0)?.toUpperCase() }}
                  </el-avatar>
                  <span>{{ row.username }}</span>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="full_name" label="姓名" width="150" />

            <el-table-column prop="email" label="邮箱" min-width="200" />

            <el-table-column prop="role" label="角色" width="120">
              <template #default="{ row }">
                <el-tag :type="getRoleTagType(row.role)" size="small">
                  {{ getRoleLabel(row.role) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="viewUserDetail(row.id)">
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 利用率 -->
      <el-tab-pane label="利用率" name="utilization">
        <div class="tab-content">
          <el-row :gutter="20">
            <el-col :xs="24" :lg="16">
              <div class="utilization-chart">
                <h3 class="chart-title">资源利用率排名</h3>
                <div class="utilization-list">
                  <div
                    v-for="(item, index) in utilization"
                    :key="item.user_id"
                    class="utilization-item"
                  >
                    <div class="item-rank">{{ index + 1 }}</div>
                    <el-avatar :size="40" :src="item.avatar" :alt="item.username" loading="lazy">
                      {{ item.username?.charAt(0)?.toUpperCase() }}
                    </el-avatar>
                    <div class="item-info">
                      <div class="item-name">{{ item.full_name || item.username }}</div>
                      <div class="item-desc">{{ item.assigned_tasks }} 个进行中任务</div>
                    </div>
                    <el-progress
                      :percentage="Math.min(100, item.assigned_tasks * 10)"
                      :stroke-width="10"
                      :color="getProgressColor(Math.min(100, item.assigned_tasks * 10))"
                      class="item-progress"
                    />
                  </div>
                </div>
              </div>
            </el-col>

            <el-col :xs="24" :lg="8">
              <div class="summary-card">
                <h3 class="summary-title">负载分布</h3>
                <div class="distribution">
                  <div class="distribution-item">
                    <div class="dist-label">
                      <span class="dot high"></span>
                      高负载 (>70%)
                    </div>
                    <div class="dist-value">{{ highLoadCount }}</div>
                  </div>
                  <div class="distribution-item">
                    <div class="dist-label">
                      <span class="dot medium"></span>
                      中负载 (30-70%)
                    </div>
                    <div class="dist-value">{{ mediumLoadCount }}</div>
                  </div>
                  <div class="distribution-item">
                    <div class="dist-label">
                      <span class="dot low"></span>
                      低负载 (<30%)
                    </div>
                    <div class="dist-value">{{ lowLoadCount }}</div>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 用户详情抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      :title="selectedUser?.user?.full_name || '用户详情'"
      size="400px"
      destroy-on-close
    >
      <div v-if="selectedUser" class="user-detail">
        <div class="detail-header">
          <el-avatar :size="80" :src="selectedUser.user?.avatar" :alt="selectedUser.user?.username" loading="lazy">
            {{ selectedUser.user?.username?.charAt(0)?.toUpperCase() }}
          </el-avatar>
          <div class="detail-info">
            <h3>{{ selectedUser.user?.full_name }}</h3>
            <p>@{{ selectedUser.user?.username }}</p>
            <el-tag :type="getRoleTagType(selectedUser.user?.role)" size="small">
              {{ getRoleLabel(selectedUser.user?.role) }}
            </el-tag>
          </div>
        </div>

        <el-divider />

        <div class="detail-section">
          <h4>参与项目</h4>
          <div class="project-list">
            <div
              v-for="project in selectedUser.projects"
              :key="project.id"
              class="project-item"
            >
              <el-tag type="info" size="small">{{ project.key }}</el-tag>
              <span>{{ project.name }}</span>
            </div>
            <el-empty v-if="!selectedUser.projects?.length" description="暂无参与项目" :image-size="60" />
          </div>
        </div>

        <div class="detail-section">
          <h4>任务统计</h4>
          <el-row :gutter="12">
            <el-col :span="8">
              <div class="mini-stat">
                <div class="mini-value">{{ selectedUser.task_stats?.todo || 0 }}</div>
                <div class="mini-label">待办</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="mini-stat warning">
                <div class="mini-value">{{ selectedUser.task_stats?.in_progress || 0 }}</div>
                <div class="mini-label">进行中</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="mini-stat success">
                <div class="mini-value">{{ selectedUser.task_stats?.done || 0 }}</div>
                <div class="mini-label">已完成</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <div class="detail-section">
          <h4>待处理任务</h4>
          <div class="task-list">
            <div
              v-for="task in selectedUser.pending_tasks"
              :key="task.id"
              class="task-item"
            >
              <el-tag :type="getPriorityType(task.priority)" size="small">
                {{ task.priority }}
              </el-tag>
              <span class="task-title">{{ task.title }}</span>
              <el-tag v-if="task.due_date" size="small" type="info">
                {{ formatDate(task.due_date) }}
              </el-tag>
            </div>
            <el-empty v-if="!selectedUser.pending_tasks?.length" description="暂无待处理任务" :image-size="60" />
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  User, Finished, Loading, WarningFilled, Refresh, ArrowRight
} from '@element-plus/icons-vue'
import { getUsers, getUserDetail, getTeamWorkload, getResourceUtilization } from '@/api/resources'

const activeTab = ref('workload')
const loading = ref(false)
const users = ref([])
const workload = ref([])
const utilization = ref([])
const drawerVisible = ref(false)
const selectedUser = ref(null)
const workloadFilter = ref('all')

// 统计数据
const stats = computed(() => ({
  totalUsers: users.value.length,
  completedTasks: workload.value.reduce((sum, m) => sum + (m.completed_tasks || 0), 0),
  inProgressTasks: workload.value.reduce((sum, m) => sum + (m.in_progress_tasks || 0), 0),
  highWorkload: workload.value.filter(m => m.workload_level === 'high').length
}))

// 过滤后的工作负载
const filteredWorkload = computed(() => {
  if (workloadFilter.value === 'all') return workload.value
  return workload.value.filter(m => m.workload_level === workloadFilter.value)
})

// 负载分布统计
const highLoadCount = computed(() => workload.value.filter(m => m.workload_level === 'high').length)
const mediumLoadCount = computed(() => workload.value.filter(m => m.workload_level === 'medium').length)
const lowLoadCount = computed(() => workload.value.filter(m => m.workload_level === 'low').length)

// 加载数据
const loadUsers = async () => {
  try {
    const res = await getUsers({ is_active: true })
    users.value = res.items || []
  } catch (error) {
    console.error('加载用户失败:', error)
  }
}

const loadWorkload = async () => {
  try {
    const res = await getTeamWorkload()
    workload.value = res.items || []
  } catch (error) {
    console.error('加载工作负载失败:', error)
  }
}

const loadUtilization = async () => {
  try {
    const res = await getResourceUtilization()
    utilization.value = res.items || []
  } catch (error) {
    console.error('加载利用率失败:', error)
  }
}

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([loadUsers(), loadWorkload(), loadUtilization()])
    ElMessage.success('数据已刷新')
  } finally {
    loading.value = false
  }
}

const viewUserDetail = async (userId) => {
  try {
    selectedUser.value = await getUserDetail(userId)
    drawerVisible.value = true
  } catch (error) {
    ElMessage.error('获取用户详情失败')
  }
}

// 辅助函数
const getWorkloadTagType = (level) => {
  const map = { high: 'danger', medium: 'warning', low: 'success' }
  return map[level] || 'info'
}

const getWorkloadLabel = (level) => {
  const map = { high: '高负载', medium: '中负载', low: '低负载' }
  return map[level] || level
}

const getRoleTagType = (role) => {
  const map = { admin: 'danger', manager: 'warning', member: 'primary' }
  return map[role] || 'info'
}

const getRoleLabel = (role) => {
  const map = { admin: '管理员', manager: '项目经理', member: '成员' }
  return map[role] || role
}

const getPriorityType = (priority) => {
  const map = { high: 'danger', medium: 'warning', low: 'success' }
  return map[priority] || 'info'
}

const getProgressColor = (percentage) => {
  if (percentage > 70) return '#F5222D'
  if (percentage > 30) return '#FA8C16'
  return '#52C41A'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.resources-page {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 4px 0;
}

.page-desc {
  font-size: 14px;
  color: #8C8C8C;
  margin: 0;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #262626;
}

.stat-label {
  font-size: 14px;
  color: #8C8C8C;
}

.main-tabs {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.filter-bar {
  margin-bottom: 20px;
}

.workload-col {
  margin-bottom: 16px;
}

.workload-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #F0F0F0;
  cursor: pointer;
  transition: all 0.3s;
}

.workload-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 16px;
  font-weight: 500;
  color: #262626;
}

.user-username {
  font-size: 13px;
  color: #8C8C8C;
}

.workload-stats {
  margin-bottom: 16px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #F5F5F5;
}

.stat-row:last-child {
  border-bottom: none;
}

.workload-stats .stat-label {
  color: #8C8C8C;
}

.workload-stats .stat-value {
  font-weight: 500;
}

.stat-value.success {
  color: #52C41A;
}

.stat-value.warning {
  color: #FA8C16;
}

.card-footer {
  margin-top: 12px;
  text-align: right;
}

.utilization-chart,
.summary-card {
  background: #FAFAFA;
  border-radius: 12px;
  padding: 20px;
}

.chart-title,
.summary-title {
  font-size: 16px;
  font-weight: 500;
  margin: 0 0 16px 0;
  color: #262626;
}

.utilization-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.utilization-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #FFFFFF;
  border-radius: 8px;
}

.item-rank {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #1E5EB8;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.item-info {
  flex: 1;
}

.item-name {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
}

.item-desc {
  font-size: 12px;
  color: #8C8C8C;
}

.item-progress {
  width: 100px;
}

.distribution {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.distribution-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dist-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #595959;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot.high {
  background: #F5222D;
}

.dot.medium {
  background: #FA8C16;
}

.dot.low {
  background: #52C41A;
}

.dist-value {
  font-size: 24px;
  font-weight: 600;
  color: #262626;
}

.user-detail {
  padding: 0 20px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.detail-info h3 {
  font-size: 18px;
  font-weight: 500;
  margin: 0 0 4px 0;
}

.detail-info p {
  font-size: 14px;
  color: #8C8C8C;
  margin: 0 0 8px 0;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
  margin: 0 0 12px 0;
}

.project-list,
.task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.project-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #595959;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #FAFAFA;
  border-radius: 6px;
}

.task-title {
  flex: 1;
  font-size: 14px;
  color: #262626;
}

.mini-stat {
  text-align: center;
  padding: 12px;
  background: #FAFAFA;
  border-radius: 8px;
}

.mini-value {
  font-size: 24px;
  font-weight: 600;
  color: #262626;
}

.mini-label {
  font-size: 12px;
  color: #8C8C8C;
}

.mini-stat.warning .mini-value {
  color: #FA8C16;
}

.mini-stat.success .mini-value {
  color: #52C41A;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

@media (max-width: 768px) {
  .resources-page {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .stats-row {
    margin-bottom: 16px;
  }

  .main-tabs {
    padding: 16px;
  }
}
</style>
