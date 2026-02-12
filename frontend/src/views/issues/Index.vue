<template>
  <div class="issue-page">
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">问题跟踪</h2>
        <el-breadcrumb separator="/" class="breadcrumb">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item>问题跟踪</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-select v-model="selectedProject" placeholder="选择项目" clearable style="width: 200px; margin-right: 12px;">
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
        <el-button type="primary" :icon="Plus" @click="showCreateDialog">报告问题</el-button>
      </div>
    </div>

    <div class="stats-cards">
      <div class="stat-card total" @click="activeTab = 'all'">
        <div class="stat-icon">
          <el-icon><Tickets /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">问题总数</div>
        </div>
      </div>
      <div class="stat-card open" @click="activeTab = 'open'">
        <div class="stat-icon">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.byStatus?.open || 0 }}</div>
          <div class="stat-label">待处理</div>
        </div>
      </div>
      <div class="stat-card progress">
        <div class="stat-icon">
          <el-icon><Loading /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.byStatus?.in_progress || 0 }}</div>
          <div class="stat-label">处理中</div>
        </div>
      </div>
    </div>

    <div class="content-tabs">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="所有问题" name="all">
          <IssueList :issues="issues" @detail="viewDetail" @edit="handleEdit" />
        </el-tab-pane>
        <el-tab-pane label="待处理" name="open">
          <IssueList :issues="openIssues" @detail="viewDetail" @edit="handleEdit" />
        </el-tab-pane>
        <el-tab-pane label="处理中" name="in_progress">
          <IssueList :issues="inProgressIssues" @detail="viewDetail" @edit="handleEdit" />
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-dialog v-model="createDialogVisible" :title="isEdit ? '编辑问题' : '报告问题'" width="600px">
      <el-form ref="formRef" :model="issueForm" :rules="formRules" label-width="100px">
        <el-form-item label="问题标题" prop="title">
          <el-input v-model="issueForm.title" placeholder="请输入问题标题" />
        </el-form-item>
        <el-form-item label="问题描述">
          <el-input v-model="issueForm.description" type="textarea" :rows="3" placeholder="请输入问题描述" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="issueForm.priority" style="width: 100%;">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="紧急" value="urgent" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">{{ isEdit ? '更新' : '创建' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Tickets, Warning, Loading } from '@element-plus/icons-vue'
import IssueList from './IssueList.vue'
import { getProjects } from '@/api/projects'
import { getIssues, createIssue, getIssueStats } from '@/api/issues'

const projects = ref([])
const selectedProject = ref(null)
const issues = ref([])
const stats = reactive({ total: 0, byStatus: {} })
const activeTab = ref('all')
const createDialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const currentIssue = ref(null)

const issueForm = reactive({
  title: '',
  description: '',
  priority: 'medium'
})

const formRules = {
  title: [{ required: true, message: '请输入问题标题', trigger: 'blur' }]
}

const openIssues = computed(() => issues.value.filter(i => i.status === 'open'))
const inProgressIssues = computed(() => issues.value.filter(i => i.status === 'in_progress'))

const loadProjects = async () => {
  try {
    const response = await getProjects()
    projects.value = response.data?.items || []
    if (projects.value.length > 0 && !selectedProject.value) {
      selectedProject.value = projects.value[0].id
    }
  } catch (error) {
    ElMessage.error('获取项目列表失败')
  }
}

const loadIssues = async () => {
  if (!selectedProject.value) return
  try {
    const params = { project_id: selectedProject.value }
    if (activeTab.value !== 'all') {
      params.status = activeTab.value
    }
    const response = await getIssues(selectedProject.value, params)
    issues.value = response.data?.items || []
  } catch (error) {
    ElMessage.error('获取问题列表失败')
  }
}

const loadStats = async () => {
  try {
    const response = await getIssueStats({ project_id: selectedProject.value })
    Object.assign(stats, response.data)
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

watch(selectedProject, () => {
  loadIssues()
  loadStats()
})

const handleTabChange = (tab) => {
  loadIssues()
}

const showCreateDialog = () => {
  isEdit.value = false
  Object.assign(issueForm, { title: '', description: '', priority: 'medium' })
  createDialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    const data = { ...issueForm, project_id: selectedProject.value }
    if (isEdit.value) {
      // await updateIssue(selectedProject.value, currentIssue.value.id, data)
      ElMessage.success('问题更新成功')
    } else {
      await createIssue(selectedProject.value, data)
      ElMessage.success('问题创建成功')
    }
    createDialogVisible.value = false
    loadIssues()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    }
  } finally {
    submitting.value = false
  }
}

const viewDetail = (issue) => {
  currentIssue.value = issue
}

const handleEdit = (issue) => {
  currentIssue.value = issue
  isEdit.value = true
  Object.assign(issueForm, {
    title: issue.title,
    description: issue.description,
    priority: issue.priority
  })
  createDialogVisible.value = true
}

onMounted(() => {
  loadProjects()
  loadStats()
})
</script>

<style scoped>
.issue-page { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-title { margin: 0 0 8px 0; font-size: 24px; font-weight: 600; }
.header-right { display: flex; align-items: center; }
.stats-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }
.stat-card { background: #fff; border-radius: 8px; padding: 20px; display: flex; align-items: center; cursor: pointer; border: 1px solid #e4e7ed; }
.stat-card:hover { box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1); }
.stat-icon { width: 48px; height: 48px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 16px; font-size: 24px; }
.stat-card.total .stat-icon { background: #e3f2fd; color: #1976d2; }
.stat-card.open .stat-icon { background: #ffebee; color: #d32f2f; }
.stat-card.progress .stat-icon { background: #fff3e0; color: #f57c00; }
.stat-value { font-size: 28px; font-weight: 600; color: #303133; }
.stat-label { font-size: 14px; color: #909399; margin-top: 4px; }
.content-tabs { background: #fff; border-radius: 8px; padding: 20px; border: 1px solid #e4e7ed; }
</style>
