<template>
  <div class="approval-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">审批中心</h2>
        <el-breadcrumb separator="/" class="breadcrumb">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item>审批中心</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="showCreateDialog">新建审批</el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card pending" @click="activeTab = 'pending'">
        <div class="stat-icon">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">待我审批</div>
        </div>
      </div>
      <div class="stat-card processing" @click="activeTab = 'processing'">
        <div class="stat-icon">
          <el-icon><Loading /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.processing }}</div>
          <div class="stat-label">审批中</div>
        </div>
      </div>
      <div class="stat-card approved" @click="activeTab = 'approved'">
        <div class="stat-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.approved }}</div>
          <div class="stat-label">已通过</div>
        </div>
      </div>
      <div class="stat-card rejected" @click="activeTab = 'rejected'">
        <div class="stat-icon">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.rejected }}</div>
          <div class="stat-label">已拒绝</div>
        </div>
      </div>
    </div>

    <!-- Tab切换 -->
    <div class="content-tabs">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="待我审批" name="pending">
          <ApprovalList :approvals="pendingApprovals" type="pending" @approve="handleApprove" @reject="handleReject" />
        </el-tab-pane>
        <el-tab-pane label="我申请的" name="my-apply">
          <ApprovalList :approvals="myApprovals" type="my-apply" @cancel="handleCancel" @detail="viewDetail" />
        </el-tab-pane>
        <el-tab-pane label="全部审批" name="all">
          <ApprovalList :approvals="allApprovals" type="all" @detail="viewDetail" />
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 审批详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="审批详情" width="600px">
      <div class="approval-detail" v-if="currentApproval">
        <div class="detail-header">
          <el-tag :type="getStatusType(currentApproval.status)">{{ getStatusLabel(currentApproval.status) }}</el-tag>
          <span class="approval-type">{{ getTypeLabel(currentApproval.type) }}</span>
        </div>
        <h3 class="detail-title">{{ currentApproval.title }}</h3>
        <p class="detail-desc">{{ currentApproval.description }}</p>
        
        <el-divider />
        
        <div class="detail-info">
          <div class="info-row">
            <span class="info-label">申请人：</span>
            <span class="info-value">{{ currentApproval.applicant_name }}</span>
          </div>
          <div class="info-row" v-if="currentApproval.project_name">
            <span class="info-label">关联项目：</span>
            <span class="info-value">{{ currentApproval.project_name }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">提交时间：</span>
            <span class="info-value">{{ formatDate(currentApproval.created_at) }}</span>
          </div>
        </div>

        <!-- 审批流程 -->
        <div class="flow-nodes" v-if="currentApproval.flow_nodes && currentApproval.flow_nodes.length">
          <h4>审批流程</h4>
          <el-timeline>
            <el-timeline-item
              v-for="(node, index) in currentApproval.flow_nodes"
              :key="index"
              :type="node.status === 'approved' ? 'success' : node.status === 'rejected' ? 'danger' : 'info'"
              :timestamp="node.approved_at ? formatDate(node.approved_at) : '待审批'"
            >
              <div class="node-content">
                <span class="node-name">{{ node.name }}</span>
                <span class="node-status" :class="node.status">
                  {{ node.status === 'approved' ? '已通过' : node.status === 'rejected' ? '已拒绝' : '待审批' }}
                </span>
                <p class="node-comment" v-if="node.comment">{{ node.comment }}</p>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>

        <!-- 操作按钮 -->
        <div class="detail-actions" v-if="activeTab === 'pending' && canApprove(currentApproval)">
          <el-button type="primary" @click="handleApprove(currentApproval)">通过</el-button>
          <el-button type="danger" @click="handleReject(currentApproval)">拒绝</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 新建审批弹窗 -->
    <el-dialog v-model="createDialogVisible" title="新建审批" width="500px">
      <el-form :model="newApproval" label-width="80px">
        <el-form-item label="审批类型">
          <el-select v-model="newApproval.type" placeholder="选择审批类型">
            <el-option
              v-for="type in approvalTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            >
              <span>{{ type.label }}</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="newApproval.title" placeholder="请输入审批标题" />
        </el-form-item>
        <el-form-item label="关联项目">
          <el-select v-model="newApproval.project_id" placeholder="选择关联项目（可选）" clearable>
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="newApproval.description" type="textarea" rows="4" placeholder="请输入审批说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitApproval">提交</el-button>
      </template>
    </el-dialog>

    <!-- 审批/拒绝弹窗 -->
    <el-dialog v-model="actionDialogVisible" :title="actionType === 'approve' ? '通过审批' : '拒绝审批'" width="400px">
      <el-form v-if="actionType === 'reject'" label-width="80px">
        <el-form-item label="拒绝原因" required>
          <el-input v-model="actionComment" type="textarea" rows="3" placeholder="请输入拒绝原因" />
        </el-form-item>
      </el-form>
      <p v-else>确认通过该审批吗？</p>
      <template #footer>
        <el-button @click="actionDialogVisible = false">取消</el-button>
        <el-button :type="actionType === 'approve' ? 'primary' : 'danger'" @click="confirmAction">
          {{ actionType === 'approve' ? '确认通过' : '确认拒绝' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Clock, Loading, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import ApprovalList from './ApprovalList.vue'

// 统计数据
const stats = reactive({
  pending: 5,
  processing: 3,
  approved: 12,
  rejected: 2
})

// Tab状态
const activeTab = ref('pending')

// 审批列表数据
const pendingApprovals = ref([
  {
    id: 1,
    type: 'project_change',
    title: '项目进度变更申请',
    description: '由于客户需求变更，需要调整项目进度',
    status: 'pending',
    applicant_name: '张三',
    project_name: '企业项目管理系统',
    created_at: '2026-02-10T10:30:00'
  },
  {
    id: 2,
    type: 'leave',
    title: '年假申请',
    description: '2月15日-2月20日休年假',
    status: 'pending',
    applicant_name: '李四',
    project_name: '企业项目管理系统',
    created_at: '2026-02-10T09:00:00'
  }
])

const myApprovals = ref([
  {
    id: 3,
    type: 'expense',
    title: '差旅费用报销',
    description: '1月份出差费用报销',
    status: 'approved',
    applicant_name: '我',
    created_at: '2026-02-08T14:00:00'
  }
])

const allApprovals = ref([
  ...pendingApprovals.value,
  ...myApprovals.value
])

// 审批类型
const approvalTypes = [
  { value: 'leave', label: '请假申请' },
  { value: 'expense', label: '费用报销' },
  { value: 'trip', label: '出差申请' },
  { value: 'purchase', label: '采购申请' },
  { value: 'project_init', label: '项目立项' },
  { value: 'project_change', label: '项目变更' }
]

// 项目列表
const projects = ref([
  { id: 1, name: '企业项目管理系统' },
  { id: 2, name: '移动端应用开发' },
  { id: 3, name: '数据分析平台' }
])

// 弹窗状态
const detailDialogVisible = ref(false)
const createDialogVisible = ref(false)
const actionDialogVisible = ref(false)
const currentApproval = ref(null)
const actionType = ref('')
const actionComment = ref('')

// 新建审批表单
const newApproval = reactive({
  type: '',
  title: '',
  project_id: null,
  description: ''
})

// 获取状态类型
const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    processing: 'info',
    approved: 'success',
    rejected: 'danger',
    cancelled: 'info'
  }
  return types[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = {
    pending: '待审批',
    processing: '审批中',
    approved: '已通过',
    rejected: '已拒绝',
    cancelled: '已撤销'
  }
  return labels[status] || status
}

const getTypeLabel = (type) => {
  const found = approvalTypes.find(t => t.value === type)
  return found ? found.label : type
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const canApprove = (approval) => {
  return approval.status === 'pending' || approval.status === 'processing'
}

// Tab切换
const handleTabChange = (tab) => {
  // 加载对应数据
  console.log('切换到:', tab)
}

// 查看详情
const viewDetail = (approval) => {
  currentApproval.value = approval
  detailDialogVisible.value = true
}

// 显示新建对话框
const showCreateDialog = () => {
  Object.assign(newApproval, { type: '', title: '', project_id: null, description: '' })
  createDialogVisible.value = true
}

// 提交审批
const submitApproval = async () => {
  if (!newApproval.type || !newApproval.title) {
    ElMessage.warning('请填写必填项')
    return
  }
  
  // 模拟提交
  ElMessage.success('审批已提交')
  createDialogVisible.value = false
  
  // 添加到列表
  myApprovals.value.unshift({
    id: Date.now(),
    ...newApproval,
    status: 'pending',
    applicant_name: '我',
    created_at: new Date().toISOString()
  })
}

// 审批操作
const handleApprove = (approval) => {
  currentApproval.value = approval
  actionType.value = 'approve'
  actionComment.value = ''
  actionDialogVisible.value = true
}

const handleReject = (approval) => {
  currentApproval.value = approval
  actionType.value = 'reject'
  actionComment.value = ''
  actionDialogVisible.value = true
}

const handleCancel = (approval) => {
  ElMessage.success('已撤销该审批')
  approval.status = 'cancelled'
}

const confirmAction = () => {
  if (actionType.value === 'reject' && !actionComment.value) {
    ElMessage.warning('请输入拒绝原因')
    return
  }
  
  if (actionType.value === 'approve') {
    currentApproval.value.status = 'approved'
    stats.pending--
    stats.approved++
    ElMessage.success('审批已通过')
  } else {
    currentApproval.value.status = 'rejected'
    stats.pending--
    stats.rejected++
    ElMessage.success('已拒绝该审批')
  }
  
  actionDialogVisible.value = false
  detailDialogVisible.value = false
}
</script>

<style lang="scss" scoped>
.approval-page {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
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
}

.stats-cards {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  
  .stat-card {
    flex: 1;
    display: flex;
    align-items: center;
    padding: 20px;
    background: #fff;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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
    
    &.pending .stat-icon {
      background: #fff7e6;
      color: #faad14;
    }
    
    &.processing .stat-icon {
      background: #e6f7ff;
      color: #1890ff;
    }
    
    &.approved .stat-icon {
      background: #f6ffed;
      color: #52c41a;
    }
    
    &.rejected .stat-icon {
      background: #fff2f0;
      color: #ff4d4f;
    }
    
    .stat-value {
      font-size: 28px;
      font-weight: 600;
      color: #303133;
    }
    
    .stat-label {
      font-size: 14px;
      color: #909399;
    }
  }
}

.content-tabs {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.approval-detail {
  .detail-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
  }
  
  .approval-type {
    color: #909399;
    font-size: 14px;
  }
  
  .detail-title {
    font-size: 18px;
    font-weight: 500;
    margin: 0 0 12px 0;
  }
  
  .detail-desc {
    color: #606266;
    line-height: 1.6;
    margin: 0 0 20px 0;
  }
  
  .detail-info {
    .info-row {
      display: flex;
      margin-bottom: 8px;
      
      .info-label {
        color: #909399;
        width: 80px;
      }
      
      .info-value {
        color: #303133;
      }
    }
  }
  
  .flow-nodes {
    margin-top: 20px;
    
    h4 {
      margin: 0 0 16px 0;
      font-size: 16px;
    }
    
    .node-content {
      .node-name {
        font-weight: 500;
      }
      
      .node-status {
        margin-left: 8px;
        font-size: 12px;
        
        &.approved { color: #52c41a; }
        &.rejected { color: #ff4d4f; }
      }
      
      .node-comment {
        margin: 8px 0 0 0;
        color: #909399;
        font-size: 13px;
      }
    }
  }
  
  .detail-actions {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid #ebeef5;
  }
}
</style>
