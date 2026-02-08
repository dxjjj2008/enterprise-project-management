<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">项目列表</h1>
      <el-button type="primary">
        <el-icon><Plus /></el-icon>
        新建项目
      </el-button>
    </div>
    
    <!-- 筛选区域 -->
    <div class="filter-section">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索项目名称..."
        prefix-icon="Search"
        style="width: 300px"
        clearable
      />
      <el-select v-model="statusFilter" placeholder="状态" clearable style="width: 150px">
        <el-option label="全部" value="" />
        <el-option label="进行中" value="active" />
        <el-option label="已完成" value="completed" />
        <el-option label="已归档" value="archived" />
      </el-select>
      <el-radio-group v-model="viewMode">
        <el-radio-button label="card">
          <el-icon><Grid /></el-icon>
        </el-radio-button>
        <el-radio-button label="table">
          <el-icon><List /></el-icon>
        </el-radio-button>
      </el-radio-group>
    </div>
    
    <!-- 卡片视图 -->
    <el-row v-if="viewMode === 'card'" :gutter="24">
      <el-col
        v-for="project in filteredProjects"
        :key="project.id"
        :xs="24"
        :sm="12"
        :lg="8"
        :xl="6"
      >
        <div class="project-card">
          <div class="project-card-header">
            <el-tag :type="getStatusType(project.status)" size="small">
              {{ getStatusLabel(project.status) }}
            </el-tag>
            <el-dropdown trigger="click">
              <el-icon class="more-btn"><MoreFilled /></el-icon>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>编辑</el-dropdown-item>
                  <el-dropdown-item>复制</el-dropdown-item>
                  <el-dropdown-item divided>归档</el-dropdown-item>
                  <el-dropdown-item divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          <h3 class="project-title">{{ project.name }}</h3>
          <p class="project-desc">{{ project.description }}</p>
          <div class="project-progress">
            <div class="progress-bar">
              <div class="progress-bar-fill blue" :style="{ width: project.progress + '%' }" />
            </div>
            <span>{{ project.progress }}%</span>
          </div>
          <div class="project-footer">
            <div class="project-members">
              <el-avatar
                v-for="member in project.members.slice(0, 3)"
                :key="member"
                :size="24"
              />
              <span v-if="project.members.length > 3" class="more-members">
                +{{ project.members.length - 3 }}
              </span>
            </div>
            <span class="project-date">{{ project.endDate }}</span>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 表格视图 -->
    <div v-else class="table-container">
      <el-table :data="filteredProjects" style="width: 100%">
        <el-table-column prop="name" label="项目名称" min-width="200" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :stroke-width="6" />
          </template>
        </el-table-column>
        <el-table-column prop="members" label="成员" width="150">
          <template #default="{ row }">
            <div class="table-members">
              <el-avatar
                v-for="member in row.members.slice(0, 3)"
                :key="member"
                :size="24"
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="endDate" label="截止日期" width="120" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default>
            <el-button type="primary" link size="small">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Plus, Grid, List, MoreFilled } from '@element-plus/icons-vue'

const searchKeyword = ref('')
const statusFilter = ref('')
const viewMode = ref('card')

const projects = ref([
  { id: 1, name: '企业项目管理系统 V1.0', description: '面向中小企业的项目管理平台', status: 'active', progress: 65, members: [1,2,3,4], endDate: '2026-03-31' },
  { id: 2, name: '技术架构升级', description: '系统微服务化改造', status: 'active', progress: 30, members: [1,2], endDate: '2026-04-15' },
  { id: 3, name: '客户门户优化', description: '提升客户自助服务体验', status: 'active', progress: 85, members: [1,2,3], endDate: '2026-02-28' },
  { id: 4, name: '移动端 APP 开发', description: 'iOS 和 Android 应用', status: 'planning', progress: 0, members: [1,2,3,4,5], endDate: '2026-05-30' }
])

const filteredProjects = computed(() => {
  return projects.value.filter(p => {
    const matchKeyword = !searchKeyword.value || p.name.includes(searchKeyword.value)
    const matchStatus = !statusFilter.value || p.status === statusFilter.value
    return matchKeyword && matchStatus
  })
})

const getStatusType = (status) => {
  const map = { active: '', completed: 'success', planning: 'info', archived: 'info' }
  return map[status] || ''
}

const getStatusLabel = (status) => {
  const map = { active: '进行中', completed: '已完成', planning: '规划中', archived: '已归档' }
  return map[status] || status
}
</script>

<style scoped>
.page-container {
  max-width: 1400px;
  margin: 0 auto;
}

.filter-section {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.project-card {
  background: #FFFFFF;
  border-radius: 8px;
  border: 1px solid #F0F0F0;
  padding: 20px;
  margin-bottom: 24px;
  transition: all 0.2s;
  cursor: pointer;
}

.project-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.project-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.more-btn {
  cursor: pointer;
  color: #8C8C8C;
}

.project-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 8px 0;
}

.project-desc {
  font-size: 13px;
  color: #8C8C8C;
  margin: 0 0 16px 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.project-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.project-progress .progress-bar {
  flex: 1;
}

.project-progress span {
  font-size: 12px;
  color: #595959;
  min-width: 40px;
}

.project-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.project-members {
  display: flex;
  align-items: center;
}

.project-members .el-avatar {
  border: 2px solid #FFFFFF;
  margin-left: -8px;
}

.project-members .el-avatar:first-child {
  margin-left: 0;
}

.more-members {
  margin-left: 8px;
  font-size: 12px;
  color: #8C8C8C;
}

.project-date {
  font-size: 12px;
  color: #8C8C8C;
}

.table-members {
  display: flex;
}
</style>
