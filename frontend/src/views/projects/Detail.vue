<template>
  <div class="project-detail">
    <!-- 项目头部 -->
    <div class="project-header">
      <div class="header-left">
        <el-page-header @back="$router.back()">
          <template #content>
            <div class="project-title-wrap">
              <h1 class="project-title">企业项目管理系统 V1.0</h1>
              <el-tag type="success" size="small">进行中</el-tag>
            </div>
          </template>
        </el-page-header>
      </div>
      <div class="header-right">
        <el-button @click="$router.push('board')">
          <el-icon><Grid /></el-icon>
          任务看板
        </el-button>
        <el-button @click="$router.push('gantt')">
          <el-icon><Clock /></el-icon>
          甘特图
        </el-button>
        <el-button type="primary">
          <el-icon><Setting /></el-icon>
          项目设置
        </el-button>
      </div>
    </div>

    <!-- Tab 导航 -->
    <el-tabs v-model="activeTab" class="project-tabs">
      <el-tab-pane label="概览" name="overview">
        <div class="overview-content">
          <!-- 项目信息 -->
          <el-row :gutter="24">
            <el-col :xs="24" :lg="16">
              <div class="content-card">
                <h3 class="card-title">项目概览</h3>
                <p class="project-desc">
                  面向中小企业的项目管理平台，支持项目计划、任务管理、甘特图、报表统计等功能。
                </p>
                
                <div class="progress-section">
                  <div class="progress-header">
                    <span>总体进度</span>
                    <span class="progress-value">65%</span>
                  </div>
                  <el-progress :percentage="65" :stroke-width="8" />
                </div>

                <el-divider />

                <div class="stats-grid">
                  <div class="stat-item">
                    <div class="stat-value">12</div>
                    <div class="stat-label">总任务数</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-value">8</div>
                    <div class="stat-label">已完成</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-value">3</div>
                    <div class="stat-label">进行中</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-value">1</div>
                    <div class="stat-label">待开始</div>
                  </div>
                </div>
              </div>

              <!-- 燃尽图占位 -->
              <div class="content-card">
                <h3 class="card-title">燃尽图</h3>
                <div class="burndown-placeholder">
                  <el-icon :size="48" color="#BFBFBF"><DataAnalysis /></el-icon>
                  <p>燃尽图展示</p>
                </div>
              </div>
            </el-col>

            <el-col :xs="24" :lg="8">
              <!-- 项目信息 -->
              <div class="content-card">
                <h3 class="card-title">项目信息</h3>
                <div class="info-list">
                  <div class="info-item">
                    <span class="info-label">负责人</span>
                    <div class="info-value">
                      <el-avatar :size="24">张</el-avatar>
                      <span>张经理</span>
                    </div>
                  </div>
                  <div class="info-item">
                    <span class="info-label">开始日期</span>
                    <span class="info-value">2026-02-01</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">截止日期</span>
                    <span class="info-value">2026-03-31</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">预估工时</span>
                    <span class="info-value">320 小时</span>
                  </div>
                </div>
              </div>

              <!-- 团队成员 -->
              <div class="content-card">
                <div class="card-header">
                  <h3 class="card-title">团队成员</h3>
                  <el-button type="primary" link size="small">+ 添加</el-button>
                </div>
                <div class="member-list">
                  <div class="member-item" v-for="i in 5" :key="i">
                    <el-avatar :size="36">成</el-avatar>
                    <div class="member-info">
                      <span class="member-name">成员 {{ i }}</span>
                      <span class="member-role">开发人员</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 最近活动 -->
              <div class="content-card">
                <h3 class="card-title">最近活动</h3>
                <div class="activity-list">
                  <div class="activity-item" v-for="i in 5" :key="i">
                    <div class="activity-dot"></div>
                    <div class="activity-content">
                      <p>张经理 更新了任务 "完成需求分析文档"</p>
                      <span class="activity-time">{{ i }} 小时前</span>
                    </div>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>

      <el-tab-pane label="任务" name="tasks">
        <div class="tasks-content">
          <el-button type="primary" @click="$router.push('board')">
            <el-icon><Grid /></el-icon>
            进入看板
          </el-button>
          <el-table :data="taskList" style="width: 100%; margin-top: 16px">
            <el-table-column prop="title" label="任务" min-width="300" />
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="assignee" label="负责人" width="150" />
            <el-table-column prop="dueDate" label="截止日期" width="120" />
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="文档" name="documents">
        <div class="documents-content">
          <el-empty description="暂无文档" />
        </div>
      </el-tab-pane>

      <el-tab-pane label="报表" name="reports">
        <div class="reports-content">
          <el-empty description="报表统计功能开发中" />
        </div>
      </el-tab-pane>

      <el-tab-pane label="设置" name="settings">
        <div class="settings-content">
          <el-empty description="项目设置功能开发中" />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Grid, Clock, Setting, DataAnalysis } from '@element-plus/icons-vue'

const activeTab = ref('overview')

const taskList = ref([
  { title: '完成项目需求分析文档', status: 'in_progress', assignee: '张三', dueDate: '2026-02-15' },
  { title: '设计数据库架构', status: 'done', assignee: '李四', dueDate: '2026-02-10' },
  { title: '前端页面原型设计', status: 'todo', assignee: '王五', dueDate: '2026-02-12' }
])

const getStatusType = (status) => {
  const map = { todo: 'info', in_progress: '', done: 'success' }
  return map[status] || ''
}

const getStatusLabel = (status) => {
  const map = { todo: '待办', in_progress: '进行中', done: '已完成' }
  return map[status] || status
}
</script>

<style scoped>
.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.project-title-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
}

.project-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

.header-right {
  display: flex;
  gap: 12px;
}

.project-tabs {
  background: #FFFFFF;
  border-radius: 8px;
  border: 1px solid #E4E7ED;
  padding: 0 24px;
}

.content-card {
  background: #FFFFFF;
  border-radius: 8px;
  border: 1px solid #E4E7ED;
  padding: 24px;
  margin-bottom: 24px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 16px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.project-desc {
  font-size: 14px;
  color: #595959;
  line-height: 1.6;
  margin: 0 0 20px 0;
}

.progress-section {
  margin-bottom: 8px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.progress-value {
  font-weight: 600;
  color: #1E5EB8;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #262626;
}

.stat-label {
  font-size: 12px;
  color: #8C8C8C;
  margin-top: 4px;
}

.burndown-placeholder {
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #F5F7FA;
  border-radius: 8px;
  color: #8C8C8C;
}

.burndown-placeholder p {
  margin: 12px 0 0 0;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  font-size: 14px;
  color: #8C8C8C;
}

.info-value {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #262626;
}

.member-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.member-info {
  display: flex;
  flex-direction: column;
}

.member-name {
  font-size: 14px;
  color: #262626;
}

.member-role {
  font-size: 12px;
  color: #8C8C8C;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  gap: 12px;
}

.activity-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #1E5EB8;
  margin-top: 6px;
}

.activity-content p {
  margin: 0;
  font-size: 13px;
  color: #595959;
}

.activity-time {
  font-size: 12px;
  color: #8C8C8C;
}
</style>
