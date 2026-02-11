<template>
  <div class="page-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">审批管理</h1>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新建审批
      </el-button>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-section" role="search" aria-label="审批筛选">
      <el-select
        v-model="filters.type"
        placeholder="审批类型"
        clearable
        style="width: 160px"
        @change="handleSearch"
      >
        <el-option label="全部" value="" />
        <el-option label="请假" value="leave" />
        <el-option label="报销" value="expense" />
        <el-option label="出差" value="trip" />
        <el-option label="采购" value="purchase" />
        <el-option label="项目立项" value="project_init" />
        <el-option label="项目变更" value="project_change" />
      </el-select>

      <el-select
        v-model="filters.status"
        placeholder="状态"
        clearable
        style="width: 140px"
        @change="handleSearch"
      >
        <el-option label="全部" value="" />
        <el-option label="待审批" value="pending" />
        <el-option label="审批中" value="processing" />
        <el-option label="已通过" value="approved" />
        <el-option label="已拒绝" value="rejected" />
        <el-option label="已撤销" value="cancelled" />
      </el-select>

      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        style="width: 260px"
        value-format="YYYY-MM-DD"
        @change="handleSearch"
      />

      <el-input
        v-model="filters.keyword"
        placeholder="搜索关键词..."
        prefix-icon="Search"
        style="width: 200px"
        clearable
        @input="handleSearch"
        @clear="handleSearch"
      />

      <el-button @click="clearFilters">
        <el-icon><Refresh /></el-icon>
        重置
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="statistics-cards">
      <div class="stat-card" @click="filterByStatus('pending')">
        <div class="stat-icon pending">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.pending || 0 }}</div>
          <div class="stat-label">待审批</div>
        </div>
      </div>
      <div class="stat-card" @click="filterByStatus('approved')">
        <div class="stat-icon approved">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.approved || 0 }}</div>
          <div class="stat-label">已通过</div>
        </div>
      </div>
      <div class="stat-card" @click="filterByStatus('rejected')">
        <div class="stat-icon rejected">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.rejected || 0 }}</div>
          <div class="stat-label">已拒绝</div>
        </div>
      </div>
      <div class="stat-card" @click="filterByStatus('processing')">
        <div class="stat-icon processing">
          <el-icon><Loading /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.processing || 0 }}</div>
          <div class="stat-label">审批中</div>
        </div>
      </div>
    </div>

    <!-- Tab切换 -->
    <div class="tabs-section">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="待办" name="pending" />
        <el-tab-pane label="已办" name="completed" />
      </el-tabs>
    </div>

    <!-- 审批列表 -->
    <div class="approval-list" v-loading="loading">
      <div v-if="filteredApprovals.length === 0" class="empty-state">
        <el-empty description="暂无审批数据" />
      </div>

      <div
        v-else
        v-for="approval in filteredApprovals"
        :key="approval.id"
        class="approval-item"
        @click="openDetail(approval)"
      >
        <div class="approval-icon" :class="approval.type">
          <el-icon v-if="approval.type === 'leave'"><Calendar /></el-icon>
          <el-icon v-else-if="approval.type === 'expense'"><Money /></el-icon>
          <el-icon v-else-if="approval.type === 'trip'"><Location /></el-icon>
          <el-icon v-else-if="approval.type === 'purchase'"><ShoppingCart /></el-icon>
          <el-icon v-else-if="approval.type === 'project_init'"><FolderAdd /></el-icon>
          <el-icon v-else-if="approval.type === 'project_change'"><Edit /></el-icon>
          <el-icon v-else><Document /></el-icon>
        </div>

        <div class="approval-content">
          <div class="approval-header">
            <span class="approval-title">{{ approval.title }}</span>
            <el-tag :type="getStatusTagType(approval.status)" size="small">
              {{ getStatusLabel(approval.status) }}
            </el-tag>
          </div>
          <div class="approval-meta">
            <span class="meta-item">
              <el-icon><User /></el-icon>
              {{ approval.applicant_name }}
            </span>
            <span class="meta-item" v-if="approval.project_name">
              <el-icon><Folder /></el-icon>
              {{ approval.project_name }}
            </span>
            <span class="meta-item">
              <el-icon><Clock /></el-icon>
              {{ formatDate(approval.created_at) }}
            </span>
            <span class="meta-item">
              <el-icon><InfoFilled /></el-icon>
              {{ getTypeLabel(approval.type) }}
            </span>
          </div>
        </div>

        <div class="approval-actions">
          <el-button
            v-if="approval.status === 'pending'"
            type="primary"
            size="small"
            @click.stop="handleApproval(approval)"
          >
            处理
          </el-button>
          <el-button
            v-else
            type="default"
            size="small"
            @click.stop="openDetail(approval)"
          >
            查看
          </el-button>
        </div>
      </div>
    </div>

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

    <!-- 审批详情弹窗 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="currentApproval?.title"
      width="640px"
      destroy-on-close
    >
      <div v-if="currentApproval" class="approval-detail">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h4>基本信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="申请人">
              {{ currentApproval.applicant_name }}
            </el-descriptions-item>
            <el-descriptions-item label="审批类型">
              {{ getTypeLabel(currentApproval.type) }}
            </el-descriptions-item>
            <el-descriptions-item label="提交时间">
              {{ formatDateTime(currentApproval.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="当前状态">
              <el-tag :type="getStatusTagType(currentApproval.status)" size="small">
                {{ getStatusLabel(currentApproval.status) }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 审批流程 -->
        <div class="detail-section">
          <h4>审批流程</h4>
          <div class="flow-timeline">
            <div
              v-for="(node, index) in currentApproval.flow_nodes"
              :key="index"
              class="flow-node"
              :class="{ completed: node.status === 'approved', current: node.status === 'pending' }"
            >
              <div class="node-indicator">
                <el-icon v-if="node.status === 'approved'"><CircleCheck /></el-icon>
                <el-icon v-else-if="node.status === 'rejected'"><CircleClose /></el-icon>
                <el-icon v-else><Clock /></el-icon>
              </div>
              <div class="node-content">
                <div class="node-title">{{ node.name }}</div>
                <div class="node-info">
                  <span>{{ node.approver_name }}</span>
                  <span v-if="node.approved_at">{{ formatDateTime(node.approved_at) }}</span>
                </div>
                <div class="node-comment" v-if="node.comment">
                  {{ node.comment }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 申请内容 -->
        <div class="detail-section">
          <h4>申请内容</h4>
          <div class="form-preview">
            <p>{{ currentApproval.description }}</p>
          </div>
        </div>

        <!-- 审批操作（待审批状态） -->
        <div v-if="currentApproval.status === 'pending'" class="detail-section">
          <h4>审批意见</h4>
          <el-input
            v-model="approvalForm.comment"
            type="textarea"
            :rows="3"
            placeholder="请输入审批意见（可选）"
          />
          <div class="approval-buttons">
            <el-button type="success" @click="handleApprove" :loading="processing">
              <el-icon><CircleCheck /></el-icon>
              通过
            </el-button>
            <el-button type="danger" @click="handleReject" :loading="processing">
              <el-icon><CircleClose /></el-icon>
              拒绝
            </el-button>
            <el-button @click="showDetailDialog = false">取消</el-button>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 新建审批弹窗 -->
    <el-dialog
      v-model="showCreateDialog"
      title="新建审批"
      width="560px"
      destroy-on-close
    >
      <el-steps :active="createStep" finish-status="success" align-center style="margin-bottom: 24px;">
        <el-step title="选择类型" />
        <el-step title="填写表单" />
        <el-step title="提交审批" />
      </el-steps>

      <!-- 步骤1：选择类型 -->
      <div v-if="createStep === 0" class="type-selector">
        <div
          v-for="type in approvalTypes"
          :key="type.value"
          class="type-item"
          :class="{ selected: createForm.type === type.value }"
          @click="selectType(type.value)"
        >
          <el-icon :size="32" :color="type.color">{{ type.icon }}</el-icon>
          <span class="type-name">{{ type.label }}</span>
          <span class="type-desc">{{ type.description }}</span>
        </div>
      </div>

      <!-- 步骤2：填写表单 -->
      <div v-if="createStep === 1">
        <el-form :model="createForm" label-width="100px">
          <el-form-item label="审批标题" required>
            <el-input v-model="createForm.title" placeholder="请输入审批标题" />
          </el-form-item>

          <el-form-item label="关联项目" v-if="needsProject">
            <el-select v-model="createForm.project_id" placeholder="选择关联项目" style="width: 100%;">
              <el-option
                v-for="project in projectList"
                :key="project.id"
                :label="project.name"
                :value="project.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="申请说明">
            <el-input
              v-model="createForm.description"
              type="textarea"
              :rows="4"
              placeholder="请输入申请说明"
            />
          </el-form-item>
        </el-form>
      </div>

      <!-- 步骤3：确认提交 -->
      <div v-if="createStep === 2" class="confirm-section">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="审批类型">
            {{ getTypeLabel(createForm.type) }}
          </el-descriptions-item>
          <el-descriptions-item label="审批标题">
            {{ createForm.title }}
          </el-descriptions-item>
          <el-descriptions-item label="关联项目" v-if="createForm.project_id">
            {{ getProjectName(createForm.project_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="申请说明">
            {{ createForm.description || '无' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <template #footer>
        <el-button v-if="createStep > 0" @click="createStep--">上一步</el-button>
        <el-button v-if="createStep < 2" type="primary" @click="createStep++">下一步</el-button>
        <el-button v-if="createStep === 2" type="primary" @click="submitCreate" :loading="submitting">
          提交审批
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Refresh, Clock, CircleCheck, CircleClose, Loading,
  Calendar, Money, Location, ShoppingCart, FolderAdd, Edit,
  Document, User, Folder, InfoFilled
} from '@element-plus/icons-vue'
import { getApprovals, getApprovalDetail, createApproval, approveApproval, rejectApproval, getApprovalStats } from '@/api/approvals'
import { getProjectsForPlan } from '@/api/planning'

// 响应式数据
const loading = ref(false)
const processing = ref(false)
const submitting = ref(false)

const activeTab = ref('all')
const showDetailDialog = ref(false)
const showCreateDialog = ref(false)
const createStep = ref(0)

const currentApproval = ref(null)
const approvalList = ref([])
const projectList = ref([])

const filters = reactive({
  type: '',
  status: '',
  keyword: ''
})

const dateRange = ref([])

const stats = reactive({
  pending: 0,
  approved: 0,
  rejected: 0,
  processing: 0
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const approvalForm = reactive({
  comment: ''
})

const createForm = reactive({
  type: '',
  title: '',
  project_id: null,
  description: ''
})

const approvalTypes = [
  { value: 'leave', label: '请假', icon: Calendar, color: '#1890FF', description: '请假申请' },
  { value: 'expense', label: '报销', icon: Money, color: '#52C41A', description: '费用报销' },
  { value: 'trip', label: '出差', icon: Location, color: '#722ED1', description: '出差申请' },
  { value: 'purchase', label: '采购', icon: ShoppingCart, color: '#FAAD14', description: '采购申请' },
  { value: 'project_init', label: '项目立项', icon: FolderAdd, color: '#13C2C2', description: '新项目立项' },
  { value: 'project_change', label: '项目变更', icon: Edit, color: '#EB2F96', description: '项目变更申请' }
]

const needsProject = computed(() => {
  return ['project_init', 'project_change'].includes(createForm.type)
})

// 加载审批列表
const loadApprovals = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      pageSize: pagination.pageSize,
      type: filters.type || undefined,
      status: getStatusFilter(),
      keyword: filters.keyword || undefined,
      start_date: dateRange.value?.[0],
      end_date: dateRange.value?.[1]
    }
    const response = await getApprovals(params)
    approvalList.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    console.error('加载审批列表失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const getStatusFilter = () => {
  if (activeTab.value === 'pending') return 'pending'
  if (activeTab.value === 'completed') return 'approved,rejected,cancelled'
  return filters.status || undefined
}

// 加载统计数据
const loadStats = async () => {
  try {
    const response = await getApprovalStats()
    Object.assign(stats, response)
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

const loadProjects = async () => {
  try {
    const response = await getProjectsForPlan()
    projectList.value = response || []
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
}

// 搜索处理
let searchTimer = null
const handleSearch = () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    pagination.page = 1
    loadApprovals()
  }, 300)
}

const clearFilters = () => {
  filters.type = ''
  filters.status = ''
  filters.keyword = ''
  dateRange.value = []
  handleSearch()
}

const handleTabChange = () => {
  pagination.page = 1
  loadApprovals()
}

const handlePageChange = (page) => {
  pagination.page = page
  loadApprovals()
}

const filterByStatus = (status) => {
  filters.status = status
  activeTab.value = 'all'
  handleSearch()
}

// 打开详情
const openDetail = async (approval) => {
  try {
    const detail = await getApprovalDetail(approval.id)
    currentApproval.value = detail
    showDetailDialog.value = true
  } catch (error) {
    ElMessage.error('获取详情失败')
  }
}

// 处理审批
const handleApproval = async (approval) => {
  await openDetail(approval)
}

const handleApprove = async () => {
  try {
    await ElMessageBox.confirm('确认通过该审批？', '确认', { type: 'success' })
    processing.value = true
    await approveApproval(currentApproval.value.id, { comment: approvalForm.comment })
    ElMessage.success('审批已通过')
    showDetailDialog.value = false
    await Promise.all([loadApprovals(), loadStats()])
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  } finally {
    processing.value = false
    approvalForm.comment = ''
  }
}

const handleReject = async () => {
  if (!approvalForm.comment) {
    ElMessage.warning('请输入拒绝原因')
    return
  }
  try {
    await ElMessageBox.confirm('确认拒绝该审批？', '确认', { type: 'danger' })
    processing.value = true
    await rejectApproval(currentApproval.value.id, { comment: approvalForm.comment })
    ElMessage.success('已拒绝该审批')
    showDetailDialog.value = false
    await Promise.all([loadApprovals(), loadStats()])
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  } finally {
    processing.value = false
    approvalForm.comment = ''
  }
}

// 新建审批
const selectType = (type) => {
  createForm.type = type
  createStep.value = 1
}

const submitCreate = async () => {
  if (!createForm.title) {
    ElMessage.warning('请填写审批标题')
    return
  }
  submitting.value = true
  try {
    await createApproval({
      type: createForm.type,
      title: createForm.title,
      project_id: createForm.project_id || undefined,
      description: createForm.description
    })
    ElMessage.success('审批已提交')
    showCreateDialog.value = false
    createStep.value = 0
    Object.assign(createForm, { type: '', title: '', project_id: null, description: '' })
    loadApprovals()
  } catch (error) {
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

const getProjectName = (projectId) => {
  const project = projectList.value.find(p => p.id === projectId)
  return project?.name || '-'
}

// 计算属性
const filteredApprovals = computed(() => {
  return approvalList.value
})

// 工具方法
const getStatusTagType = (status) => {
  const map = {
    pending: 'warning',
    processing: 'primary',
    approved: 'success',
    rejected: 'danger',
    cancelled: 'info'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = {
    pending: '待审批',
    processing: '审批中',
    approved: '已通过',
    rejected: '已拒绝',
    cancelled: '已撤销'
  }
  return map[status] || status
}

const getTypeLabel = (type) => {
  const item = approvalTypes.find(t => t.value === type)
  return item?.label || type
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

const formatDateTime = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadApprovals(),
    loadStats(),
    loadProjects()
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

.filter-section {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.statistics-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
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

.stat-icon.pending { background: #FFFBE6; color: #FAAD14; }
.stat-icon.approved { background: #F6FFED; color: #52C41A; }
.stat-icon.rejected { background: #FFF2F0; color: #FF4D4F; }
.stat-icon.processing { background: #E6F7FF; color: #1890FF; }

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #262626;
}

.stat-label {
  font-size: 14px;
  color: #595959;
}

.tabs-section {
  margin-bottom: 16px;
}

.approval-list {
  background: #fff;
  border-radius: 8px;
}

.empty-state {
  padding: 60px;
  text-align: center;
}

.approval-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid #F0F0F0;
  cursor: pointer;
  transition: all 0.2s;
}

.approval-item:hover {
  background: #F5F7FA;
}

.approval-item:last-child {
  border-bottom: none;
}

.approval-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.approval-icon.leave { background: #E6F7FF; color: #1890FF; }
.approval-icon.expense { background: #F6FFED; color: #52C41A; }
.approval-icon.trip { background: #F9F0FF; color: #722ED1; }
.approval-icon.purchase { background: #FFF7E6; color: #FAAD14; }
.approval-icon.project_init { background: #E6FFFB; color: #13C2C2; }
.approval-icon.project_change { background: #FFF0F6; color: #EB2F96; }

.approval-content {
  flex: 1;
  min-width: 0;
}

.approval-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.approval-title {
  font-size: 15px;
  font-weight: 500;
  color: #262626;
}

.approval-meta {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #8C8C8C;
}

.approval-actions {
  flex-shrink: 0;
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding: 16px;
  border-top: 1px solid #F0F0F0;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  margin: 0 0 12px;
  font-size: 14px;
  font-weight: 600;
  color: #262626;
}

.flow-timeline {
  padding: 16px 0;
}

.flow-node {
  display: flex;
  gap: 16px;
  padding-bottom: 24px;
  position: relative;
}

.flow-node:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 15px;
  top: 32px;
  bottom: 0;
  width: 2px;
  background: #E8E8E8;
}

.flow-node.completed::before {
  background: #52C41A;
}

.node-indicator {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #F5F5F5;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  z-index: 1;
}

.flow-node.completed .node-indicator {
  background: #F6FFED;
  color: #52C41A;
}

.flow-node.current .node-indicator {
  background: #E6F7FF;
  color: #1890FF;
}

.node-content {
  flex: 1;
}

.node-title {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
  margin-bottom: 4px;
}

.node-info {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #8C8C8C;
}

.node-comment {
  margin-top: 8px;
  padding: 8px 12px;
  background: #F5F5F5;
  border-radius: 4px;
  font-size: 13px;
  color: #595959;
}

.form-preview {
  padding: 16px;
  background: #F9F9F9;
  border-radius: 8px;
  font-size: 14px;
  color: #595959;
  line-height: 1.6;
}

.approval-buttons {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  justify-content: flex-end;
}

.type-selector {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.type-item {
  padding: 20px;
  border: 2px solid #E8E8E8;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.type-item:hover {
  border-color: #1E5EB8;
}

.type-item.selected {
  border-color: #1E5EB8;
  background: #F0F7FF;
}

.type-name {
  display: block;
  margin-top: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #262626;
}

.type-desc {
  display: block;
  font-size: 12px;
  color: #8C8C8C;
  margin-top: 4px;
}

.confirm-section {
  padding: 16px;
}

@media screen and (max-width: 768px) {
  .statistics-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .type-selector {
    grid-template-columns: repeat(2, 1fr);
  }

  .approval-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .approval-actions {
    align-self: flex-end;
    margin-top: 12px;
  }
}
</style>
