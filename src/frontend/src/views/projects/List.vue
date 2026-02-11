<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">项目列表</h1>
      <el-button type="primary" @click="openCreateDialog" class="header-action-btn">
        <el-icon><Plus /></el-icon>
        新建项目
      </el-button>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-section" role="search" aria-label="项目筛选">
      <!-- 搜索框 -->
      <el-input
        v-model="filters.keyword"
        placeholder="搜索项目名称、描述、Key..."
        prefix-icon="Search"
        style="width: 300px"
        clearable
        @input="handleSearch"
        @clear="handleSearch"
        class="filter-item"
        aria-label="搜索项目"
      />

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
        <el-option label="规划中" value="planning" />
        <el-option label="进行中" value="active" />
        <el-option label="已暂停" value="on_hold" />
        <el-option label="已完成" value="completed" />
        <el-option label="已归档" value="archived" />
      </el-select>

      <!-- 排序方式 -->
      <el-select
        v-model="filters.sortBy"
        placeholder="排序"
        style="width: 150px"
        @change="handleSearch"
        class="filter-item"
        aria-label="排序方式"
      >
        <el-option label="最近更新" value="updated_at" />
        <el-option label="创建时间" value="created_at" />
        <el-option label="项目名称" value="name" />
        <el-option label="截止日期" value="end_date" />
      </el-select>

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
      <el-skeleton :rows="4" animated />
      <el-skeleton :rows="4" animated />
      <el-skeleton :rows="4" animated />
    </div>

    <!-- 空状态 -->
    <div v-else-if="filteredProjects.length === 0" class="empty-state" role="region" aria-label="空状态">
      <el-empty description="暂无项目" :image-size="120">
        <template #description>
          <p>暂无项目，点击下方按钮创建第一个项目</p>
        </template>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          新建项目
        </el-button>
      </el-empty>
    </div>

    <!-- 无匹配状态 -->
    <div v-else-if="filters.keyword && filteredProjects.length === 0" class="empty-state" role="region" aria-label="无匹配结果">
      <el-empty description="未找到匹配的项目" :image-size="120">
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
          v-for="project in filteredProjects"
          :key="project.id"
          :xs="24"
          :sm="12"
          :lg="8"
          :xl="6"
          class="project-col"
        >
          <article
            class="project-card"
            role="article"
            :aria-label="'项目: ' + project.name"
            tabindex="0"
            @click="goToDetail(project.id)"
            @keydown.enter="goToDetail(project.id)"
          >
            <!-- 卡片头部 -->
            <div class="project-card-header">
              <el-tag :type="getStatusType(project.status)" size="small" class="status-tag">
                {{ getStatusLabel(project.status) }}
              </el-tag>
              <el-tag type="info" size="small" class="key-tag">
                {{ project.key }}
              </el-tag>
              <el-dropdown
                trigger="click"
                @command="(cmd) => handleProjectAction(cmd, project)"
                placement="bottom-end"
              >
                <el-icon class="more-btn" @click.stop>
                  <MoreFilled />
                </el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="view" :icon="View">
                      <el-icon><View /></el-icon>
                      查看详情
                    </el-dropdown-item>
                    <el-dropdown-item command="edit" :icon="Edit">
                      <el-icon><Edit /></el-icon>
                      编辑项目
                    </el-dropdown-item>
                    <el-dropdown-item command="duplicate" :icon="CopyDocument">
                      <el-icon><CopyDocument /></el-icon>
                      复制项目
                    </el-dropdown-item>
                    <el-dropdown-item command="archive" :icon="FolderOpened" divided v-if="project.status !== 'archived'">
                      <el-icon><FolderOpened /></el-icon>
                      归档项目
                    </el-dropdown-item>
                    <el-dropdown-item command="delete" :icon="Delete" divided class="danger-item">
                      <el-icon><Delete /></el-icon>
                      删除项目
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>

            <!-- 项目名称 -->
            <h3 class="project-title" :title="project.name">
              {{ project.name }}
            </h3>

            <!-- 项目描述 -->
            <p class="project-desc" :title="project.description">
              {{ project.description || '暂无描述' }}
            </p>

            <!-- 进度条 -->
            <div class="project-progress">
              <el-progress
                :percentage="project.progress || 0"
                :stroke-width="6"
                :color="getProgressColor(project.progress)"
                :show-text="false"
              />
              <span class="progress-text">{{ project.progress || 0 }}%</span>
            </div>

            <!-- 卡片底部 -->
            <div class="project-footer">
              <!-- 成员头像 -->
              <div class="project-members" v-if="project.members && project.members.length > 0">
                <el-avatar
                  v-for="(member, idx) in project.members.slice(0, 5)"
                  :key="idx"
                  :size="28"
                  :src="member.avatar"
                  class="member-avatar"
                />
                <span v-if="project.members.length > 5" class="more-members">
                  +{{ project.members.length - 5 }}
                </span>
              </div>
              <div v-else class="no-members">
                <el-icon><User /></el-icon>
                <span>暂无成员</span>
              </div>

              <!-- 截止日期 -->
              <div class="project-date" :class="{ overdue: isOverdue(project.end_date) }" v-if="project.end_date">
                <el-icon><Calendar /></el-icon>
                {{ formatDate(project.end_date) }}
              </div>
            </div>
          </article>
        </el-col>
      </el-row>
    </div>

    <!-- 表格视图 -->
    <div v-else class="table-view">
      <el-table
        :data="filteredProjects"
        style="width: 100%"
        stripe
        highlight-current-row
        @row-click="handleRowClick"
        v-loading="loading"
        role="grid"
        aria-label="项目表格"
      >
        <el-table-column type="selection" width="48" />
        <el-table-column label="项目标识" width="120">
          <template #default="{ row }">
            <el-tag type="info" size="small" class="table-key-tag">
              {{ row.key }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="项目名称" min-width="200">
          <template #default="{ row }">
            <a class="project-link" @click.stop="goToDetail(row.id)">
              {{ row.name }}
            </a>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="180">
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress || 0"
              :stroke-width="8"
              :color="getProgressColor(row.progress)"
              :show-text="true"
              :text-inside="true"
            />
          </template>
        </el-table-column>
        <el-table-column label="截止日期" width="130">
          <template #default="{ row }">
            <span :class="{ overdue: isOverdue(row.end_date) }" v-if="row.end_date">
              {{ formatDate(row.end_date) }}
            </span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click.stop="goToDetail(row.id)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button type="success" link size="small" @click.stop="editProject(row)">
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

    <!-- 新建/编辑项目弹窗 -->
    <el-dialog
      v-model="formVisible"
      :title="isEdit ? '编辑项目' : '新建项目'"
      width="560px"
      destroy-on-close
      :close-on-click-modal="false"
      append-to-body
    >
      <el-form
        :model="projectForm"
        :rules="formRules"
        ref="formRef"
        label-width="100px"
        class="project-form"
      >
        <!-- 项目名称 -->
        <el-form-item label="项目名称" prop="name">
          <el-input
            v-model="projectForm.name"
            placeholder="请输入项目名称（2-100字符）"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <!-- 项目标识（只读） -->
        <el-form-item label="项目标识">
          <el-input
            :value="projectForm.key"
            disabled
            placeholder="系统自动生成"
          >
            <template #prefix>
              <el-tag type="info" size="small">PJ</el-tag>
            </template>
          </el-input>
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            <span>项目标识由系统自动生成，格式为 PJ + 6位流水号</span>
          </div>
        </el-form-item>

        <!-- 项目描述 -->
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="projectForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述（最多1000字符）"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <!-- 项目周期 -->
        <el-form-item label="项目周期">
          <el-col :span="11">
            <el-date-picker
              v-model="projectForm.startDate"
              type="date"
              placeholder="开始日期"
              style="width: 100%"
              value-format="YYYY-MM-DD"
            />
          </el-col>
          <el-col :span="2" class="date-separator">-</el-col>
          <el-col :span="11">
            <el-date-picker
              v-model="projectForm.endDate"
              type="date"
              placeholder="结束日期"
              style="width: 100%"
              value-format="YYYY-MM-DD"
              :disabled-date="disabledEndDate"
            />
          </el-col>
        </el-form-item>

        <!-- 编辑模式才显示状态 -->
        <el-form-item label="项目状态" v-if="isEdit">
          <el-select v-model="projectForm.status" style="width: 100%">
            <el-option label="规划中" value="planning" />
            <el-option label="进行中" value="active" />
            <el-option label="已暂停" value="on_hold" />
            <el-option label="已完成" value="completed" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-form-item>
      </el-form>

      <!-- 弹窗底部 -->
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
        <p>确定要删除项目「{{ currentProject?.name }}」吗？</p>
        <p class="danger-text">此操作不可恢复，项目下的所有任务和文档也将被删除。</p>
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
  Plus, Grid, List, MoreFilled, Edit, Delete, View,
  CopyDocument, FolderOpened, Close, Calendar,
  User, InfoFilled, WarningFilled
} from '@element-plus/icons-vue'
import { getProjects, createProject, getNextProjectKey, updateProject, deleteProject } from '@/api/projects'

// ========== 响应式数据 ==========

// 视图模式
const viewMode = ref('card')

// 加载状态
const loading = ref(false)
const submitLoading = ref(false)
const deleteLoading = ref(false)

// 项目列表
const projects = ref([])

// 筛选条件
const filters = reactive({
  keyword: '',
  status: '',
  sortBy: 'updated_at'
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

const projectForm = reactive({
  id: null,
  name: '',
  key: '',
  description: '',
  startDate: '',
  endDate: '',
  status: 'planning'
})

// 删除相关
const deleteVisible = ref(false)
const currentProject = ref(null)

// ========== 计算属性 ==========

const filteredProjects = computed(() => {
  let result = [...projects.value]

  // 关键词筛选
  if (filters.keyword) {
    const keyword = filters.keyword.toLowerCase()
    result = result.filter(p =>
      p.name.toLowerCase().includes(keyword) ||
      (p.description && p.description.toLowerCase().includes(keyword)) ||
      p.key.toLowerCase().includes(keyword)
    )
  }

  // 状态筛选
  if (filters.status) {
    result = result.filter(p => p.status === filters.status)
  }

  // 排序
  result.sort((a, b) => {
    switch (filters.sortBy) {
      case 'name':
        return a.name.localeCompare(b.name)
      case 'end_date':
        return (a.end_date || '').localeCompare(b.end_date || '')
      case 'created_at':
        return new Date(b.created_at) - new Date(a.created_at)
      default:
        return new Date(b.updated_at) - new Date(a.updated_at)
    }
  })

  return result
})

const isFormValid = computed(() => {
  return projectForm.name && projectForm.name.length >= 2 && projectForm.name.length <= 100
})

// ========== 方法 ==========

// 加载项目数据
const loadProjects = async () => {
  loading.value = true
  try {
    const response = await getProjects(pagination.page, pagination.pageSize, {
      status: filters.status || undefined
    })
    projects.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    console.error('加载项目失败:', error)
    ElMessage.error('加载项目失败，请重试')
  } finally {
    loading.value = false
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
    loadProjects()
  }, 300)
}

// 清除筛选
const clearFilters = () => {
  filters.keyword = ''
  filters.status = ''
  filters.sortBy = 'updated_at'
  loadProjects()
}

// 分页处理
const handlePageChange = (page) => {
  pagination.page = page
  loadProjects()
}

// 跳转到详情页
const goToDetail = (id) => {
  window.location.href = `/projects/${id}`
}

// 行点击
const handleRowClick = (row) => {
  goToDetail(row.id)
}

// 选择变化
const handleSelectionChange = (selection) => {
  console.log('选择变化:', selection)
}

// 获取下一个可用Key
const fetchNextKey = async () => {
  try {
    const keyData = await getNextProjectKey()
    projectForm.key = keyData.key
  } catch (error) {
    // 使用本地生成作为后备
    const timestamp = Date.now().toString().slice(-6)
    projectForm.key = `PJ${timestamp}`
  }
}

// 打开新建对话框
const openCreateDialog = async () => {
  isEdit.value = false
  Object.assign(projectForm, {
    id: null,
    name: '',
    key: '',
    description: '',
    startDate: '',
    endDate: '',
    status: 'planning'
  })
  await fetchNextKey()
  formVisible.value = true
}

// 编辑项目
const editProject = (project) => {
  isEdit.value = true
  Object.assign(projectForm, {
    id: project.id,
    name: project.name,
    key: project.key || '',
    description: project.description || '',
    startDate: project.start_date || '',
    endDate: project.end_date || '',
    status: project.status || 'planning'
  })
  formVisible.value = true
}

// 项目操作处理
const handleProjectAction = (command, project) => {
  switch (command) {
    case 'view':
      goToDetail(project.id)
      break
    case 'edit':
      editProject(project)
      break
    case 'duplicate':
      duplicateProject(project)
      break
    case 'archive':
      archiveProject(project)
      break
    case 'delete':
      confirmDelete(project)
      break
  }
}

// 复制项目
const duplicateProject = async (project) => {
  try {
    await fetchNextKey()
    projectForm.name = project.name + '（副本）'
    projectForm.description = project.description || ''
    projectForm.startDate = project.start_date || ''
    projectForm.endDate = project.end_date || ''
    isEdit.value = false
    formVisible.value = true
    ElMessage.info('已复制项目信息，请完善后创建')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 归档项目
const archiveProject = async (project) => {
  try {
    await ElMessageBox.confirm(
      '确定要归档项目「' + project.name + '」吗？归档后项目将移到归档列表。',
      '确认归档',
      {
        confirmButtonText: '确定归档',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await updateProject(project.id, { status: 'archived' })
    ElMessage.success('项目已归档')
    loadProjects()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('归档失败:', error)
      ElMessage.error('归档失败')
    }
  }
}

// 确认删除
const confirmDelete = (project) => {
  currentProject.value = project
  deleteVisible.value = true
}

// 删除项目
const handleDelete = async () => {
  if (!currentProject.value) return

  deleteLoading.value = true
  try {
    await deleteProject(currentProject.value.id)
    ElMessage.success('项目已删除')
    deleteVisible.value = false
    loadProjects()
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败，请重试')
  } finally {
    deleteLoading.value = false
    currentProject.value = null
  }
}

// 提交表单
const submitForm = async () => {
  if (!isFormValid.value) {
    ElMessage.warning('请填写项目名称')
    return
  }

  submitLoading.value = true
  try {
    if (isEdit.value) {
      await updateProject(projectForm.id, {
        name: projectForm.name,
        description: projectForm.description,
        status: projectForm.status,
        start_date: projectForm.startDate || undefined,
        end_date: projectForm.endDate || undefined
      })
      ElMessage.success('项目更新成功')
    } else {
      await createProject({
        name: projectForm.name,
        description: projectForm.description,
        start_date: projectForm.startDate || undefined,
        end_date: projectForm.endDate || undefined
      })
      ElMessage.success('项目创建成功')
    }
    formVisible.value = false
    loadProjects()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败，请重试')
  } finally {
    submitLoading.value = false
  }
}

// 禁用结束日期
const disabledEndDate = (time) => {
  if (projectForm.startDate) {
    return time.getTime() < new Date(projectForm.startDate).getTime()
  }
  return false
}

// ========== 工具方法 ==========

const getStatusType = (status) => {
  const map = {
    planning: 'info',
    active: 'success',
    on_hold: 'warning',
    completed: 'success',
    archived: 'info'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = {
    planning: '规划中',
    active: '进行中',
    on_hold: '已暂停',
    completed: '已完成',
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

const isOverdue = (date) => {
  if (!date) return false
  return new Date(date) < new Date()
}

const formatDate = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  return (d.getMonth() + 1) + '-' + d.getDate()
}

// ========== 表单验证规则 ==========

const formRules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 100, message: '项目名称长度为 2-100 个字符', trigger: 'blur' }
  ]
}

// ========== 键盘快捷键 ==========

const handleKeydown = (e) => {
  // Ctrl/Cmd + K 聚焦搜索框
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    document.querySelector('.filter-section .el-input input')?.focus()
  }

  // Ctrl/Cmd + N 新建项目
  if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
    e.preventDefault()
    openCreateDialog()
  }

  // Escape 关闭弹窗
  if (e.key === 'Escape') {
    formVisible.value = false
    deleteVisible.value = false
  }
}

// ========== 生命周期 ==========

onMounted(() => {
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
/* ========== 基础布局 ========== */

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

/* ========== 筛选区域 ========== */

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

/* ========== 卡片视图 ========== */

.card-view {
  margin-top: 8px;
}

.project-col {
  margin-bottom: 24px;
}

.project-card {
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

.project-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.project-card:focus {
  outline: 2px solid #1E5EB8;
  outline-offset: 2px;
}

/* 卡片头部 */
.project-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.status-tag {
  flex-shrink: 0;
}

.key-tag {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 12px;
  background: #F5F7FA;
  border: none;
}

.more-btn {
  margin-left: auto;
  color: #8C8C8C;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.more-btn:hover {
  background: #F5F7FA;
  color: #262626;
}

/* 项目名称 */
.project-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 项目描述 */
.project-desc {
  font-size: 13px;
  color: #595959;
  margin: 0 0 16px;
  line-height: 1.5;
  flex: 1;
  min-height: 40px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* 进度条 */
.project-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.project-progress .el-progress {
  flex: 1;
}

.progress-text {
  font-size: 13px;
  color: #595959;
  font-weight: 500;
  min-width: 40px;
  text-align: right;
}

/* 卡片底部 */
.project-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #F0F0F0;
}

.project-members {
  display: flex;
  align-items: center;
}

.member-avatar {
  margin-right: -8px;
  border: 2px solid #fff;
  cursor: pointer;
}

.member-avatar:hover {
  z-index: 1;
}

.more-members {
  font-size: 12px;
  color: #8C8C8C;
  margin-left: 8px;
}

.no-members {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #BFBFBF;
}

.project-date {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #595959;
}

.project-date.overdue {
  color: #FF4D4F;
}

/* ========== 表格视图 ========== */

.table-view {
  margin-top: 8px;
}

.table-key-tag {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 12px;
}

.project-link {
  color: #1E5EB8;
  cursor: pointer;
  text-decoration: none;
}

.project-link:hover {
  text-decoration: underline;
}

.text-muted {
  color: #BFBFBF;
}

.overdue {
  color: #FF4D4F;
}

/* ========== 分页 ========== */

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding: 16px 0;
}

/* ========== 加载和空状态 ========== */

.loading-container {
  padding: 24px;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

/* ========== 表单 ========== */

.project-form {
  padding: 0 20px;
}

.form-tip {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  font-size: 12px;
  color: #8C8C8C;
}

.date-separator {
  text-align: center;
  color: #8C8C8C;
  line-height: 32px;
}

/* ========== 删除对话框 ========== */

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

/* ========== 下拉菜单危险项 ========== */

.danger-item {
  color: #FF4D4F;
}

.danger-item:hover {
  background: #FFF2F0;
}

/* ========== 响应式设计 ========== */

/* 平板端 (768px - 1024px) */
@media screen and (min-width: 768px) and (max-width: 1024px) {
  .filter-section {
    gap: 12px;
  }

  .project-card {
    padding: 16px;
  }
}

/* 移动端 (< 768px) */
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

/* 小屏移动端 (< 480px) */
@media screen and (max-width: 479px) {
  .project-footer {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .project-members {
    order: 1;
  }

  .project-date {
    order: 2;
  }
}
</style>
