<template>
  <div class="risk-list">
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索风险标题..."
        :prefix-icon="Search"
        clearable
        style="width: 240px;"
      />
      <el-select v-model="filterLevel" placeholder="风险等级" clearable style="width: 140px; margin-left: 12px;">
        <el-option label="低风险" value="low" />
        <el-option label="中风险" value="medium" />
        <el-option label="高风险" value="high" />
        <el-option label="极高风险" value="critical" />
      </el-select>
    </div>

    <!-- 风险表格 -->
    <el-table
      :data="filteredRisks"
      stripe
      style="width: 100%"
      :default-sort="{ prop: 'score', order: 'descending' }"
      @row-click="handleRowClick"
    >
      <el-table-column prop="title" label="风险标题" min-width="200">
        <template #default="{ row }">
          <div class="risk-title">
            <el-icon class="risk-icon"><Warning /></el-icon>
            <span>{{ row.title }}</span>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column prop="level" label="等级" width="100" sortable>
        <template #default="{ row }">
          <el-tag :type="getLevelType(row.level)" size="small">{{ getLevelLabel(row.level) }}</el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="score" label="评分" width="80" sortable>
        <template #default="{ row }">
          <span :class="['score', { high: row.score >= 70, medium: row.score >= 40 && row.score < 70 }]">
            {{ row.score }}
          </span>
        </template>
      </el-table-column>
      
      <el-table-column prop="status" label="状态" width="100" sortable>
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="category" label="类别" width="120" />
      
      <el-table-column prop="probability" label="概率" width="80">
        <template #default="{ row }">
          {{ row.probability }}%
        </template>
      </el-table-column>
      
      <el-table-column prop="impact" label="影响" width="80">
        <template #default="{ row }">
          {{ row.impact }}%
        </template>
      </el-table-column>
      
      <el-table-column prop="owner_name" label="负责人" width="100" />
      
      <el-table-column prop="identified_date" label="识别日期" width="120" sortable>
        <template #default="{ row }">
          {{ formatDate(row.identified_date) }}
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
    <el-empty v-if="!risks.length" description="暂无风险数据" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search, Warning, View, Edit } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  risks: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['detail', 'edit'])

// 筛选状态
const searchKeyword = ref('')
const filterLevel = ref('')

// 计算属性
const filteredRisks = computed(() => {
  return props.risks.filter(risk => {
    // 关键词过滤
    if (searchKeyword.value && !risk.title.toLowerCase().includes(searchKeyword.value.toLowerCase())) {
      return false
    }
    // 等级过滤
    if (filterLevel.value && risk.level !== filterLevel.value) {
      return false
    }
    return true
  })
})

// 方法
const handleRowClick = (row) => {
  emit('detail', row)
}

const getLevelType = (level) => {
  const types = { low: 'info', medium: 'warning', high: 'danger', critical: 'danger' }
  return types[level] || 'info'
}

const getLevelLabel = (level) => {
  const labels = { low: '低', medium: '中', high: '高', critical: '极高' }
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
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.risk-list {
  min-height: 400px;
}

.filter-bar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.risk-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.risk-icon {
  color: #e6a23c;
}

.score {
  font-weight: 600;
}

.score.high {
  color: #f56c6c;
}

.score.medium {
  color: #e6a23c;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}
</style>
