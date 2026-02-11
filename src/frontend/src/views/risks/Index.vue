<template>
  <div class="risk-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">风险管理</h2>
        <el-breadcrumb separator="/" class="breadcrumb">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item>风险管理</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-select v-model="selectedProject" placeholder="选择项目" clearable style="width: 200px; margin-right: 12px;">
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
        <el-button type="primary" :icon="Plus" @click="showCreateDialog">识别风险</el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card total">
        <div class="stat-icon">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">风险总数</div>
        </div>
      </div>
      <div class="stat-card high-risk" @click="activeTab = 'high'">
        <div class="stat-icon">
          <el-icon><WarningFilled /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.highRisks }}</div>
          <div class="stat-label">高风险</div>
        </div>
      </div>
      <div class="stat-card mitigating">
        <div class="stat-icon">
          <el-icon><Aim /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.byStatus?.mitigating || 0 }}</div>
          <div class="stat-label">应对中</div>
        </div>
      </div>
      <div class="stat-card closed">
        <div class="stat-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.byStatus?.closed || 0 }}</div>
          <div class="stat-label">已关闭</div>
        </div>
      </div>
    </div>

    <!-- Tab切换 -->
    <div class="content-tabs">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="所有风险" name="all">
          <RiskList :risks="risks" @detail="viewDetail" @edit="handleEdit" />
        </el-tab-pane>
        <el-tab-pane label="高风险" name="high">
          <RiskList :risks="highRisks" @detail="viewDetail" @edit="handleEdit" />
        </el-tab-pane>
        <el-tab-pane label="应对中" name="mitigating">
          <RiskList :risks="mitigatingRisks" @detail="viewDetail" @edit="handleEdit" />
        </el-tab-pane>
        <el-tab-pane label="已关闭" name="closed">
          <RiskList :risks="closedRisks" @detail="viewDetail" @edit="handleEdit" />
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 风险详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="风险详情" width="700px">
      <div class="risk-detail" v-if="currentRisk">
        <div class="detail-header">
          <el-tag :type="getLevelType(currentRisk.level)">{{ getLevelLabel(currentRisk.level) }}</el-tag>
          <el-tag :type="getStatusType(currentRisk.status)" style="margin-left: 8px;">{{ getStatusLabel(currentRisk.status) }}</el-tag>
          <span class="risk-score">风险评分: {{ currentRisk.score }}</span>
        </div>
        
        <h3 class="detail-title">{{ currentRisk.title }}</h3>
        <p class="detail-desc">{{ currentRisk.description }}</p>
        
        <el-divider />
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="风险类别">{{ currentRisk.category || '-' }}</el-descriptions-item>
          <el-descriptions-item label="风险来源">{{ currentRisk.source || '-' }}</el-descriptions-item>
          <el-descriptions-item label="发生概率">{{ currentRisk.probability }}%</el-descriptions-item>
          <el-descriptions-item label="影响程度">{{ currentRisk.impact }}%</el-descriptions-item>
          <el-descriptions-item label="负责人">{{ currentRisk.owner_name || '未指定' }}</el-descriptions-item>
          <el-descriptions-item label="关联任务">{{ currentRisk.task_title || '无' }}</el-descriptions-item>
          <el-descriptions-item label="识别日期">{{ formatDate(currentRisk.identified_date) }}</el-descriptions-item>
          <el-descriptions-item label="到期日期">{{ formatDate(currentRisk.due_date) || '-' }}</el-descriptions-item>
        </el-descriptions>
        
        <el-divider content-position="left">应对措施</el-divider>
        <div class="mitigation-content">
          <p><strong>应对措施：</strong>{{ currentRisk.mitigation || '未制定' }}</p>
          <p><strong>应急预案：</strong>{{ currentRisk.contingency_plan || '未制定' }}</p>
        </div>
        
        <!-- 应对记录 -->
        <el-divider content-position="left">应对记录</el-divider>
        <el-timeline>
          <el-timeline-item v-for="response in currentRisk.responses" :key="response.id" :timestamp="formatDate(response.created_at)" placement="top">
            <p>{{ response.action }}</p>
            <p v-if="response.result" class="response-result">{{ response.result }}</p>
          </el-timeline-item>
          <el-timeline-item v-if="!currentRisk.responses?.length">
            <p class="no-data">暂无应对记录</p>
          </el-timeline-item>
        </el-timeline>
      </div>
      
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="showEditDialog">编辑风险</el-button>
      </template>
    </el-dialog>

    <!-- 创建/编辑风险弹窗 -->
    <el-dialog v-model="createDialogVisible" :title="isEdit ? '编辑风险' : '识别新风险'" width="600px">
      <el-form ref="formRef" :model="riskForm" :rules="formRules" label-width="100px">
        <el-form-item label="风险标题" prop="title">
          <el-input v-model="riskForm.title" placeholder="请输入风险标题" />
        </el-form-item>
        
        <el-form-item label="风险描述">
          <el-input v-model="riskForm.description" type="textarea" :rows="3" placeholder="请输入风险描述" />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="风险等级" prop="level">
              <el-select v-model="riskForm.level" placeholder="选择风险等级" style="width: 100%;">
                <el-option label="低风险" value="low" />
                <el-option label="中风险" value="medium" />
                <el-option label="高风险" value="high" />
                <el-option label="极高风险" value="critical" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="风险状态">
              <el-select v-model="riskForm.status" placeholder="选择风险状态" style="width: 100%;">
                <el-option label="已识别" value="identified" />
                <el-option label="已评估" value="assessed" />
                <el-option label="应对中" value="mitigating" />
                <el-option label="监控中" value="monitoring" />
                <el-option label="已关闭" value="closed" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="发生概率">
              <el-slider v-model="riskForm.probability" :min="0" :max="100" show-input />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="影响程度">
              <el-slider v-model="riskForm.impact" :min="0" :max="100" show-input />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="风险类别">
              <el-input v-model="riskForm.category" placeholder="如：技术风险、资源风险" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="风险来源">
              <el-input v-model="riskForm.source" placeholder="如：需求变更、技术难点" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="应对措施">
          <el-input v-model="riskForm.mitigation" type="textarea" :rows="2" placeholder="请输入风险应对措施" />
        </el-form-item>
        
        <el-form-item label="应急预案">
          <el-input v-model="riskForm.contingency_plan" type="textarea" :rows="2" placeholder="请输入应急预案" />
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
import { Plus, Warning, WarningFilled, Aim, CircleCheck } from '@element-plus/icons-vue'
import RiskList from './RiskList.vue'

// API
import { getProjects } from '@/api/projects'
import { getRisks, createRisk, updateRisk, getRiskStats } from '@/api/risks'

// 响应式状态
const projects = ref([])
const selectedProject = ref(null)
const risks = ref([])
const stats = reactive({
  total: 0,
  highRisks: 0,
  byStatus: {},
  byLevel: {}
})
const activeTab = ref('all')
const detailDialogVisible = ref(false)
const createDialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const currentRisk = ref(null)

// 表单数据
const riskForm = reactive({
  title: '',
  description: '',
  level: 'medium',
  status: 'identified',
  probability: 0,
  impact: 0,
  category: '',
  source: '',
  mitigation: '',
  contingency_plan: ''
})

// 表单验证规则
const formRules = {
  title: [{ required: true, message: '请输入风险标题', trigger: 'blur' }]
}

// 计算属性
const highRisks = computed(() => risks.value.filter(r => ['high', 'critical'].includes(r.level)))
const mitigatingRisks = computed(() => risks.value.filter(r => r.status === 'mitigating'))
const closedRisks = computed(() => risks.value.filter(r => r.status === 'closed'))

// 获取项目列表
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

// 获取风险列表
const loadRisks = async () => {
  if (!selectedProject.value) return
  
  try {
    const params = { project_id: selectedProject.value }
    if (activeTab.value === 'high') {
      params.level = 'high,critical'
    } else if (activeTab.value !== 'all') {
      params.status = activeTab.value
    }
    
    const response = await getRisks(selectedProject.value, params)
    risks.value = response.data?.items || []
  } catch (error) {
    ElMessage.error('获取风险列表失败')
  }
}

// 获取统计数据
const loadStats = async () => {
  try {
    const response = await getRiskStats({ project_id: selectedProject.value })
    Object.assign(stats, response.data)
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// 监听项目变化
watch(selectedProject, () => {
  loadRisks()
  loadStats()
})

// 监听Tab切换
const handleTabChange = (tab) => {
  loadRisks()
}

// 显示创建弹窗
const showCreateDialog = () => {
  isEdit.value = false
  resetForm()
  createDialogVisible.value = true
}

// 显示编辑弹窗
const showEditDialog = () => {
  isEdit.value = true
  Object.assign(riskForm, {
    title: currentRisk.value.title,
    description: currentRisk.value.description,
    level: currentRisk.value.level,
    status: currentRisk.value.status,
    probability: currentRisk.value.probability,
    impact: currentRisk.value.impact,
    category: currentRisk.value.category,
    source: currentRisk.value.source,
    mitigation: currentRisk.value.mitigation,
    contingency_plan: currentRisk.value.contingency_plan
  })
  detailDialogVisible.value = false
  createDialogVisible.value = true
}

// 重置表单
const resetForm = () => {
  Object.assign(riskForm, {
    title: '',
    description: '',
    level: 'medium',
    status: 'identified',
    probability: 0,
    impact: 0,
    category: '',
    source: '',
    mitigation: '',
    contingency_plan: ''
  })
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    const data = {
      ...riskForm,
      project_id: selectedProject.value
    }
    
    if (isEdit.value) {
      await updateRisk(selectedProject.value, currentRisk.value.id, data)
      ElMessage.success('风险更新成功')
    } else {
      await createRisk(selectedProject.value, data)
      ElMessage.success('风险创建成功')
    }
    
    createDialogVisible.value = false
    loadRisks()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    }
  } finally {
    submitting.value = false
  }
}

// 查看详情
const viewDetail = async (risk) => {
  try {
    // 重新获取完整详情
    const response = await fetch(`/api/v1/projects/${selectedProject.value}/risks/${risk.id}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      }
    })
    const data = await response.json()
    currentRisk.value = data
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取风险详情失败')
  }
}

// 编辑风险
const handleEdit = (risk) => {
  currentRisk.value = risk
  showEditDialog()
}

// 工具函数
const getLevelType = (level) => {
  const types = { low: 'info', medium: 'warning', high: 'danger', critical: 'danger' }
  return types[level] || 'info'
}

const getLevelLabel = (level) => {
  const labels = { low: '低风险', medium: '中风险', high: '高风险', critical: '极高风险' }
  return labels[level] || level
}

const getStatusType = (status) => {
  const types = { identified: 'info', assessed: '', mitigating: 'warning', monitoring: '', closed: 'success' }
  return types[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = { identified: '已识别', assessed: '已评估', mitigating: '应对中', monitoring: '监控中', closed: '已关闭' }
  return labels[status] || status
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadProjects()
  loadStats()
})
</script>

<style scoped>
.risk-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.breadcrumb {
  margin-bottom: 0;
}

.header-right {
  display: flex;
  align-items: center;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #e4e7ed;
}

.stat-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
}

.stat-card.total .stat-icon {
  background: #e3f2fd;
  color: #1976d2;
}

.stat-card.high-risk .stat-icon {
  background: #ffebee;
  color: #d32f2f;
}

.stat-card.mitigating .stat-icon {
  background: #fff3e0;
  color: #f57c00;
}

.stat-card.closed .stat-icon {
  background: #e8f5e9;
  color: #388e3c;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.content-tabs {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e4e7ed;
}

.risk-detail {
  padding: 0 20px;
}

.detail-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.risk-score {
  margin-left: auto;
  font-size: 16px;
  font-weight: 600;
  color: #f56c6c;
}

.detail-title {
  margin: 0 0 12px 0;
  font-size: 20px;
}

.detail-desc {
  color: #606266;
  margin-bottom: 16px;
}

.mitigation-content {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
}

.mitigation-content p {
  margin: 8px 0;
}

.response-result {
  color: #67c23a;
  font-size: 13px;
}

.no-data {
  color: #909399;
  text-align: center;
}
</style>
