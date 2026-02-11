<template>
  <div class="approval-list">
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索审批标题..."
        clearable
        style="width: 240px"
        @clear="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select v-model="filterType" placeholder="审批类型" clearable style="width: 140px">
        <el-option
          v-for="type in approvalTypes"
          :key="type.value"
          :label="type.label"
          :value="type.value"
        />
      </el-select>
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        style="width: 260px"
        @change="handleDateChange"
      />
    </div>

    <!-- 审批列表 -->
    <div class="list-content" v-if="filteredApprovals.length">
      <div
        v-for="approval in filteredApprovals"
        :key="approval.id"
        class="approval-card"
        @click="$emit('detail', approval)"
      >
        <div class="card-header">
          <el-tag :type="getStatusType(approval.status)" size="small">
            {{ getStatusLabel(approval.status) }}
          </el-tag>
          <span class="approval-type">{{ getTypeLabel(approval.type) }}</span>
          <span class="approval-date">{{ formatDate(approval.created_at) }}</span>
        </div>
        
        <div class="card-body">
          <h4 class="card-title">{{ approval.title }}</h4>
          <p class="card-desc">{{ approval.description }}</p>
        </div>
        
        <div class="card-footer">
          <div class="applicant-info">
            <el-avatar :size="24" :src="''">{{ approval.applicant_name?.charAt(0) }}</el-avatar>
            <span class="applicant-name">{{ approval.applicant_name }}</span>
          </div>
          <div class="project-tag" v-if="approval.project_name">
            <el-icon><Folder /></el-icon>
            {{ approval.project_name }}
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="card-actions" v-if="type === 'pending' && canApprove(approval)">
          <el-button type="primary" size="small" @click.stop="$emit('approve', approval)">
            <el-icon><Check /></el-icon> 通过
          </el-button>
          <el-button type="danger" size="small" @click.stop="$emit('reject', approval)">
            <el-icon><Close /></el-icon> 拒绝
          </el-button>
        </div>
        <div class="card-actions" v-if="type === 'my-apply' && canCancel(approval)">
          <el-button size="small" @click.stop="$emit('cancel', approval)">
            <el-icon><Close /></el-icon> 撤销
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <el-empty v-else description="暂无审批数据" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search, Folder, Check, Close } from '@element-plus/icons-vue'

const props = defineProps({
  approvals: {
    type: Array,
    default: () => []
  },
  type: {
    type: String,
    default: 'pending' // pending, my-apply, all
  }
})

defineEmits(['approve', 'reject', 'cancel', 'detail'])

// 筛选状态
const searchKeyword = ref('')
const filterType = ref('')
const dateRange = ref(null)

// 审批类型
const approvalTypes = [
  { value: 'leave', label: '请假' },
  { value: 'expense', label: '报销' },
  { value: 'trip', label: '出差' },
  { value: 'purchase', label: '采购' },
  { value: 'project_init', label: '项目立项' },
  { value: 'project_change', label: '项目变更' }
]

// 筛选后的列表
const filteredApprovals = computed(() => {
  let result = [...props.approvals]
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(a => 
      a.title?.toLowerCase().includes(keyword) ||
      a.description?.toLowerCase().includes(keyword)
    )
  }
  
  if (filterType.value) {
    result = result.filter(a => a.type === filterType.value)
  }
  
  if (dateRange.value) {
    const [start, end] = dateRange.value
    result = result.filter(a => {
      if (!a.created_at) return true
      const date = new Date(a.created_at)
      return date >= start && date <= end
    })
  }
  
  return result
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
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

const canApprove = (approval) => {
  return approval.status === 'pending' || approval.status === 'processing'
}

const canCancel = (approval) => {
  return approval.status === 'pending' || approval.status === 'processing'
}

const handleSearch = () => {
  // 触发computed重新计算
}

const handleDateChange = () => {
  // 触发computed重新计算
}
</script>

<style lang="scss" scoped>
.approval-list {
  .filter-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
  }
  
  .list-content {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .approval-card {
    background: #fff;
    border-radius: 8px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.3s;
    border: 1px solid #ebeef5;
    
    &:hover {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      border-color: #409eff;
    }
    
    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;
      
      .approval-type {
        color: #909399;
        font-size: 13px;
      }
      
      .approval-date {
        margin-left: auto;
        color: #909399;
        font-size: 13px;
      }
    }
    
    .card-body {
      margin-bottom: 12px;
      
      .card-title {
        font-size: 16px;
        font-weight: 500;
        margin: 0 0 8px 0;
        color: #303133;
      }
      
      .card-desc {
        font-size: 14px;
        color: #606266;
        margin: 0;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
    
    .card-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      
      .applicant-info {
        display: flex;
        align-items: center;
        gap: 8px;
        
        .applicant-name {
          font-size: 13px;
          color: #606266;
        }
      }
      
      .project-tag {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        color: #909399;
      }
    }
    
    .card-actions {
      display: flex;
      gap: 8px;
      margin-top: 12px;
      padding-top: 12px;
      border-top: 1px solid #ebeef5;
    }
  }
}
</style>
