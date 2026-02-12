<template>
  <div class="issue-list">
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索问题标题..."
        :prefix-icon="Search"
        clearable
        style="width: 240px;"
      />
      <el-select v-model="filterStatus" placeholder="问题状态" clearable style="width: 140px; margin-left: 12px;">
        <el-option label="待处理" value="open" />
        <el-option label="进行中" value="in_progress" />
        <el-option label="已解决" value="resolved" />
        <el-option label="已关闭" value="closed" />
      </el-select>
      <el-select v-model="filterPriority" placeholder="优先级" clearable style="width: 120px; margin-left: 12px;">
        <el-option label="紧急" value="urgent" />
        <el-option label="高" value="high" />
        <el-option label="中" value="medium" />
        <el-option label="低" value="low" />
      </el-select>
    </div>

    <!-- 问题表格 -->
    <el-table
      :data="filteredIssues"
      stripe
      style="width: 100%"
      :default-sort="{ prop: 'created_at', order: 'descending' }"
      @row-click="handleRowClick"
    >
      <el-table-column prop="title" label="问题标题" min-width="200">
        <template #default="{ row }">
          <div class="issue-title">
            <el-icon class="issue-icon"><InfoFilled /></el-icon>
            <span>{{ row.title }}</span>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column prop="status" label="状态" width="100" sortable>
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="priority" label="优先级" width="90" sortable>
        <template #default="{ row }">
          <el-tag :type="getPriorityType(row.priority)" size="small">{{ getPriorityLabel(row.priority) }}</el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="issue_type" label="类型" width="100">
        <template #default="{ row }">
          {{ getTypeLabel(row.issue_type) }}
        </template>
      </el-table-column>
      
      <el-table-column prop="severity" label="严重程度" width="100">
        <template #default="{ row }">
          <el-tag :type="getSeverityType(row.severity)" size="small">{{ getSeverityLabel(row.severity) }}</el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="assignee_name" label="指派给" width="100" />
      
      <el-table-column prop="reporter_name" label="报告人" width="100" />
      
      <el-table-column prop="created_at" label="创建时间" width="120" sortable>
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button-group>
            <el-tooltip content="查看详情">
              <el-button type="primary" :icon="View" size="small" @click.stop="$emit('detail', row)" />
            </el-tooltip>
            <el-tooltip content="编辑">
              <el-button type="warning" :icon="Edit" size="small" @click.stop="$emit('edit', row)" />
            </el-tooltip>
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>

    <!-- 空状态 -->
    <el-empty v-if="!issues.length" description="暂无问题数据" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search, InfoFilled, View, Edit } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  issues: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['detail', 'edit'])

// 筛选状态
const searchKeyword = ref('')
const filterStatus = ref('')
const filterPriority = ref('')

// 计算属性
const filteredIssues = computed(() => {
  return props.issues.filter(issue => {
    // 关键词过滤
    if (searchKeyword.value && !issue.title.toLowerCase().includes(searchKeyword.value.toLowerCase())) {
      return false
    }
    // 状态过滤
    if (filterStatus.value && issue.status !== filterStatus.value) {
      return false
    }
    // 优先级过滤
    if (filterPriority.value && issue.priority !== filterPriority.value) {
      return false
    }
    return true
  })
})

// 方法
const handleRowClick = (row) => {
  emit('detail', row)
}

const getStatusType = (status) => {
  const types = { open: 'info', in_progress: 'warning', resolved: 'success', closed: 'info' }
  return types[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = { open: '待处理', in_progress: '进行中', resolved: '已解决', closed: '已关闭' }
  return labels[status] || status
}

const getPriorityType = (priority) => {
  const types = { urgent: 'danger', high: 'warning', medium: '', low: 'info' }
  return types[priority] || 'info'
}

const getPriorityLabel = (priority) => {
  const labels = { urgent: '紧急', high: '高', medium: '中', low: '低' }
  return labels[priority] || priority
}

const getTypeLabel = (type) => {
  const labels = { bug: 'Bug', feature: '功能', improvement: '改进', task: '任务', question: '问题' }
  return labels[type] || type || '-'
}

const getSeverityType = (severity) => {
  const types = { critical: 'danger', major: 'warning', minor: 'info', trivial: 'info' }
  return types[severity] || 'info'
}

const getSeverityLabel = (severity) => {
  const labels = { critical: '严重', major: '重要', minor: '一般', trivial: '轻微' }
  return labels[severity] || severity || '-'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.issue-list {
  min-height: 400px;
}

.filter-bar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.issue-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.issue-icon {
  color: #409eff;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}
</style>
