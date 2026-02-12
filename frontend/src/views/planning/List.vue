<template>
  <div class="page-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">计划管理</h1>
      <el-button type="primary" @click="openCreateDialog" class="header-action-btn">
        <el-icon><Plus /></el-icon>
        新建计划
      </el-button>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-section" role="search" aria-label="计划筛选">
      <!-- 项目筛选 -->
      <el-select
        v-model="filters.project_id"
        placeholder="项目"
        clearable
        style="width: 180px"
        @change="handleSearch"
        class="filter-item"
        aria-label="筛选项目"
      >
        <el-option label="全部项目" value="" />
        <el-option
          v-for="project in projectList"
          :key="project.id"
          :label="project.name"
          :value="project.id"
        />
      </el-select>

      <!-- 状态筛选 -->
      <el-select
        v-model="filters.status"
        placeholder="状态"
        clearable
        style="width: 140px"
        @change="handleSearch"
        class="filter-item"
        aria-label="筛选状态"
      >
        <el-option label="全部" value="" />
        <el-option label="草稿" value="draft" />
        <el-option label="进行中" value="active" />
        <el-option label="已完成" value="completed" />
        <el-option label="已暂停" value="on_hold" />
        <el-option label="已归档" value="archived" />
      </el-select>

      <!-- 搜索框 -->
      <el-input
        v-model="filters.keyword"
        placeholder="搜索计划名称..."
        prefix-icon="Search"
        style="width: 240px"
        clearable
        @input="handleSearch"
        @clear="handleSearch"
        class="filter-item"
        aria-label="搜索计划"
      />

      <!-- 视图切换 -->
      <el-radio-group v-model="viewMode" class="view-toggle" aria-label="视图切换">
        <el-radio-button value="card" aria-label="卡片视图">
          <el-icon><Grid /></el-icon>
        </el-radio-button>
        <el-radio-button value="table" aria-label="表格视图">
          <el-icon><List /></el-icon>
        </el-radio-button>
      </el-radio-group>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container" aria-live="polite">
      <el-skeleton :rows="3" animated />
      <el-skeleton :rows="3" animated />
      <el-skeleton :rows="3" animated />
    </div>

    <!-- 空状态 -->
    <div v-else-if="filteredPlans.length === 0" class="empty-state" role="region" aria-label="空状态">
      <el-empty description="暂无计划" :image-size="120">
        <template #description>
          <p>暂无计划，点击下方按钮创建第一个计划</p>
        </template>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          新建计划
        </el-button>
      </el-empty>
    </div>

    <!-- 无匹配状态 -->
    <div v-else-if="filters.keyword && filteredPlans.length === 0" class="empty-state" role="region" aria-label="无匹配结果">
      <el-empty description="未找到匹配的计划" :image-size="120">
        <template #description>
          <p>调整搜索条件后重试</p>
        </template>
        <el-button @click="clearFilters">
          <el-icon><Close /></el-icon>
          清除筛选
        </el-button>
      </el-empty>
    </div>

    <!-- 卡片视图 -->
    <div v-else-if="viewMode === 'card'" class="card-view">
      <el-row :gutter="24">
        <el-col
          v-for="plan in filteredPlans"
          :key="plan.id"
          :xs="24"
          :sm="12"
          :lg="8"
          :xl="6"
          class="plan-col"
        >
          <article
            class="plan-card"
            role="article"
            :aria-label="'计划: ' + plan.name"
            tabindex="0"
            @click="goToDetail(plan.id)"
            @keydown.enter="goToDetail(plan.id)"
          >
            <!-- 卡片头部 -->
            <div class="plan-card-header">
              <el-tag :type="getStatusType(plan.status)" size="small" class="status-tag">
                {{ getStatusLabel(plan.status) }}
              </el-tag>
              <span class="project-name" :title="plan.project_name">
                <el-icon><Folder /></el-icon>
                {{ plan.project_name }}
              </span>
            </div>

            <!-- 计划名称 -->
            <h3 class="plan-title" :title="plan.name">
              {{ plan.name }}
            </h3>

            <!-- 进度条 -->
            <div class="plan-progress">
              <el-progress
                :percentage="plan.progress"
                :stroke-width="8"
                :color="getProgressColor(plan.progress)"
                :show-text="false"
              />
              <span class="progress-text">{{ plan.progress }}%</span>
            </div>

            <!-- 任务统计 -->
            <div class="task-stats">
              <span class="stat-item">
                <el-icon><Document /></el-icon>
                {{ plan.task_count }} 任务
              </span>
              <span class="stat-item">
                <el-icon><CircleCheck /></el-icon>
                {{ plan.completed_task_count }} 已完成
              </span>
            </div>

            <!-- 时间范围 -->
            <div class="plan-date" v-if="plan.start_date || plan.end_date">
              <el-icon><Calendar /></el-icon>
              {{ formatDate(plan.start_date) }} ~ {{ formatDate(plan.end_date) }}
            </div>

            <!-- 卡片底部 -->
            <div class="plan-footer">
              <div class="plan-owner" v-if="plan.owner_name">
                <el-avatar :size="24" :src="plan.owner_avatar">
                  {{ plan.owner_name.charAt(0) }}
                </el-avatar>
                <span>{{ plan.owner_name }}</span>
              </div>
              <span class="update-time" v-if="plan.updated_at">
                更新于 {{ formatRelativeTime(plan.updated_at) }}
              </span>
            </div>
          </article>
        </el-col>
      </el-row>
    </div>

    <!-- 表格视图 -->
    <div v-else class="table-view">
      <el-table
        :data="filteredPlans"
        style="width: 100%"
        stripe
        highlight-current-row
        @row-click="handleRowClick"
        v-loading="loading"
        role="grid"
        aria-label="计划表格"
      >
        <el-table-column label="计划名称" min-width="250">
          <template #default="{ row }">
            <a class="plan-link" @click.stop="goToDetail(row.id)">
              {{ row.name }}
            </a>
          </template>
        </el-table-column>
        <el-table-column label="关联项目" width="150">
          <template #default="{ row }">
            <span class="project-cell">
              <el-icon><Folder /></el-icon>
              {{ row.project_name }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="负责人" width="120">
          <template #default="{ row }">
            <div class="owner-cell">
              <el-avatar :size="24" :src="row.owner_avatar">
                {{ row.owner_name?.charAt(0) }}
              </el-avatar>
              <span>{{ row.owner_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="180">
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress"
              :stroke-width="8"
              :color="getProgressColor(row.progress)"
              :show-text="true"
              :text-inside="true"
            />
          </template>
        </el-table-column>
        <el-table-column label="时间范围" width="200">
          <template #default="{ row }">
            <span v-if="row.start_date && row.end_date">
              {{ formatDate(row.start_date) }} ~ {{ formatDate(row.end_date) }}
            </span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click.stop="goToDetail(row.id)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button type="success" link size="small" @click.stop="editPlan(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" link size="small" @click.stop="confirmDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-container" v-if="pagination.total > pagination.pageSize">
      <el-pagination
        v-model:current-page="pagination.page"
        :page-size="pagination.pageSize"
        :total="pagination.total"
        layout="prev, pager, next, jumper"
        @current-change="handlePageChange"
        aria-label="分页导航"
      />
    </div>

    <!-- 新建/编辑计划弹窗 -->
    <el-dialog
      v-model="formVisible"
      :title="isEdit ? '编辑计划' : '新建计划'"
      width="560px"
      destroy-on-close
      :close-on-click-modal="false"
      append-to-body
    >
      <el-form
        :model="planForm"
        :rules="formRules"
        ref="formRef"
        label-width="100px"
        class="plan-form"
      >
        <!-- 计划名称 -->
        <el-form-item label="计划名称" prop="name">
          <el-input
            v-model="planForm.name"
            placeholder="请输入计划名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <!-- 关联项目 -->
        <el-form-item label="关联项目" prop="project_id">
          <el-select
            v-model="planForm.project_id"
            placeholder="选择关联项目"
            style="width: 100%"
            :disabled="isEdit"
          >
            <el-option
              v-for="project in projectList"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>

        <!-- 计划描述 -->
        <el-form-item label="计划描述" prop="description">
          <el-input
            v-model="planForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入计划描述"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <!-- 计划周期 -->
        <el-form-item label="计划周期">
          <el-col :span="11">
            <el-date-picker
              v-model="planForm.start_date"
              type="date"
              placeholder="开始日期"
              style="width: 100%"
              value-format="YYYY-MM-DD"
            />
          </el-col>
          <el-col :span="2" class="date-separator">-</el-col>
          <el-col :span="11">
            <el-date-picker
              v-model="planForm.end_date"
              type="date"
              placeholder="结束日期"
              style="width: 100%"
              value-format="YYYY-MM-DD"
              :disabled-date="disabledEndDate"
            />
          </el-col>
        </el-form-item>

        <!-- 编辑模式才显示状态 -->
        <el-form-item label="计划状态" v-if="isEdit">
          <el-select v-model="planForm.status" style="width: 100%">
            <el-option label="草稿" value="draft" />
            <el-option label="进行中" value="active" />
            <el-option label="已完成" value="completed" />
            <el-option label="已暂停" value="on_hold" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="submitForm"
          :loading="submitLoading"
          :disabled="!isFormValid"
        >
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteVisible"
      title="确认删除"
      width="400px"
      center
    >
      <div class="delete-dialog-content">
        <el-icon class="warning-icon"><WarningFilled /></el-icon>
        <p>确定要删除计划「{{ currentPlan?.name }}」吗？</p>
        <p class="danger-text">此操作不可恢复，计划下的所有任务也将被删除。</p>
      </div>
      <template #footer>
        <el-button @click="deleteVisible = false">取消</el-button>
        <el-button type="danger" @click="handleDelete" :loading="deleteLoading">
          确定删除
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Grid, List, Folder, Calendar, Document,
  CircleCheck, View, Edit, Delete, Close, WarningFilled
} from '@element-plus/icons-vue'
import { getPlans, createPlan, updatePlan, deletePlan, getProjectsForPlan } from '@/api/planning'

// 视图模式
const viewMode = ref('card')

// 加载状态
const loading = ref(false)
const submitLoading = ref(false)
const deleteLoading = ref(false)

// 计划列表
const plans = ref([])
const projectList = ref([])

// 筛选条件
const filters = reactive({
  project_id: '',
  status: '',
  keyword: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 12,
  total: 0
})

// 表单相关
const formVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const planForm = reactive({
  id: null,
  name: '',
  project_id: '',
  description: '',
  start_date: '',
  end_date: '',
  status: 'draft'
})

// 删除相关
const deleteVisible = ref(false)
const currentPlan = ref(null)

// 计算属性
const filteredPlans = computed(() => {
  let result = [...plans.value]

  if (filters.keyword) {
    const keyword = filters.keyword.toLowerCase()
    result = result.filter(p =>
      p.name.toLowerCase().includes(keyword) ||
      (p.project_name && p.project_name.toLowerCase().includes(keyword))
    )
  }

  if (filters.project_id) {
    result = result.filter(p => p.project_id === filters.project_id)
  }

  if (filters.status) {
    result = result.filter(p => p.status === filters.status)
  }

  result.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))

  return result
})

const isFormValid = computed(() => {
  return planForm.name && planForm.name.length >= 2 && planForm.project_id
})

// 加载计划数据
const loadPlans = async () => {
  loading.value = true
  try {
    const response = await getPlans({
      page: pagination.page,
      pageSize: pagination.pageSize,
      project_id: filters.project_id || undefined,
      status: filters.status || undefined,
      keyword: filters.keyword || undefined
    })
    plans.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    console.error('加载计划失败:', error)
    ElMessage.error('加载计划失败，请重试')
  } finally {
    loading.value = false
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

// 搜索处理（防抖）
let searchTimer = null
const handleSearch = () => {
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
  searchTimer = setTimeout(() => {
    pagination.page = 1
    loadPlans()
  }, 300)
}

// 清除筛选
const clearFilters = () => {
  filters.project_id = ''
  filters.status = ''
  filters.keyword = ''
  loadPlans()
}

// 分页处理
const handlePageChange = (page) => {
  pagination.page = page
  loadPlans()
}

// 跳转到详情页
const goToDetail = (id) => {
  window.location.href = `/planning/${id}`
}

// 行点击
const handleRowClick = (row) => {
  goToDetail(row.id)
}

// 打开新建对话框
const openCreateDialog = async () => {
  isEdit.value = false
  Object.assign(planForm, {
    id: null,
    name: '',
    project_id: '',
    description: '',
    start_date: '',
    end_date: '',
    status: 'draft'
  })
  formVisible.value = true
}

// 编辑计划
const editPlan = (plan) => {
  isEdit.value = true
  Object.assign(planForm, {
    id: plan.id,
    name: plan.name,
    project_id: plan.project_id,
    description: plan.description || '',
    start_date: plan.start_date || '',
    end_date: plan.end_date || '',
    status: plan.status
  })
  formVisible.value = true
}

// 确认删除
const confirmDelete = (plan) => {
  currentPlan.value = plan
  deleteVisible.value = true
}

// 删除计划
const handleDelete = async () => {
  if (!currentPlan.value) return

  deleteLoading.value = true
  try {
    await deletePlan(currentPlan.value.id)
    ElMessage.success('计划已删除')
    deleteVisible.value = false
    loadPlans()
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败，请重试')
  } finally {
    deleteLoading.value = false
    currentPlan.value = null
  }
}

// 提交表单
const submitForm = async () => {
  if (!isFormValid.value) {
    ElMessage.warning('请填写必填项')
    return
  }

  submitLoading.value = true
  try {
    if (isEdit.value) {
      await updatePlan(planForm.id, {
        name: planForm.name,
        description: planForm.description,
        status: planForm.status,
        start_date: planForm.start_date || undefined,
        end_date: planForm.end_date || undefined
      })
      ElMessage.success('计划更新成功')
    } else {
      await createPlan({
        name: planForm.name,
        project_id: planForm.project_id,
        description: planForm.description,
        start_date: planForm.start_date || undefined,
        end_date: planForm.end_date || undefined
      })
      ElMessage.success('计划创建成功')
    }
    formVisible.value = false
    loadPlans()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败，请重试')
  } finally {
    submitLoading.value = false
  }
}

// 禁用结束日期
const disabledEndDate = (time) => {
  if (planForm.start_date) {
    return time.getTime() < new Date(planForm.start_date).getTime()
  }
  return false
}

// 工具方法
const getStatusType = (status) => {
  const map = {
    draft: 'info',
    active: 'success',
    completed: 'success',
    on_hold: 'warning',
    archived: 'info'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = {
    draft: '草稿',
    active: '进行中',
    completed: '已完成',
    on_hold: '已暂停',
    archived: '已归档'
  }
  return map[status] || status
}

const getProgressColor = (progress) => {
  if (!progress || progress === 0) return '#909399'
  if (progress < 30) return '#F56C6C'
  if (progress < 70) return '#E6A23C'
  return '#67C23A'
}

const formatDate = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`
}

const formatRelativeTime = (date) => {
  if (!date) return '-'
  const now = new Date()
  const d = new Date(date)
  const diff = now.getTime() - d.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return formatDate(date)
}

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入计划名称', trigger: 'blur' },
    { min: 2, max: 100, message: '计划名称长度为 2-100 个字符', trigger: 'blur' }
  ],
  project_id: [
    { required: true, message: '请选择关联项目', trigger: 'change' }
  ]
}

// 键盘快捷键
const handleKeydown = (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
    e.preventDefault()
    openCreateDialog()
  }

  if (e.key === 'Escape') {
    formVisible.value = false
    deleteVisible.value = false
  }
}

// 生命周期
onMounted(() => {
  loadPlans()
  loadProjects()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
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

.header-action-btn {
  font-weight: 500;
}

.filter-section {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-item {
  flex-shrink: 0;
}

.view-toggle {
  margin-left: auto;
}

.card-view {
  margin-top: 8px;
}

.plan-col {
  margin-bottom: 24px;
}

.plan-card {
  background: #fff;
  border: 1px solid #E4E7ED;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.plan-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.plan-card:focus {
  outline: 2px solid #1E5EB8;
  outline-offset: 2px;
}

.plan-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.status-tag {
  flex-shrink: 0;
}

.project-name {
  font-size: 12px;
  color: #595959;
  display: flex;
  align-items: center;
  gap: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.plan-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.plan-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.plan-progress .el-progress {
  flex: 1;
}

.progress-text {
  font-size: 13px;
  color: #595959;
  font-weight: 500;
  min-width: 40px;
  text-align: right;
}

.task-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.stat-item {
  font-size: 12px;
  color: #8C8C8C;
  display: flex;
  align-items: center;
  gap: 4px;
}

.plan-date {
  font-size: 12px;
  color: #595959;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 16px;
}

.plan-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #F0F0F0;
  margin-top: auto;
}

.plan-owner {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #595959;
}

.update-time {
  font-size: 12px;
  color: #BFBFBF;
}

.table-view {
  margin-top: 8px;
}

.plan-link {
  color: #1E5EB8;
  cursor: pointer;
  text-decoration: none;
}

.plan-link:hover {
  text-decoration: underline;
}

.project-cell {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #595959;
}

.owner-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.text-muted {
  color: #BFBFBF;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding: 16px 0;
}

.loading-container {
  padding: 24px;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.plan-form {
  padding: 0 20px;
}

.date-separator {
  text-align: center;
  color: #8C8C8C;
  line-height: 32px;
}

.delete-dialog-content {
  text-align: center;
  padding: 20px;
}

.warning-icon {
  font-size: 48px;
  color: #FAAD14;
  margin-bottom: 16px;
}

.danger-text {
  font-size: 13px;
  color: #FF4D4F;
  margin-top: 8px;
}

@media screen and (max-width: 767px) {
  .page-container {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-item {
    width: 100% !important;
  }

  .view-toggle {
    justify-content: center;
    margin-left: 0;
  }

  .pagination-container {
    justify-content: center;
  }
}
</style>
