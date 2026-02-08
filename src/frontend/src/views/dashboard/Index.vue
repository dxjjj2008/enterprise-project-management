<template>
  <div class="dashboard">
    <!-- 项目概况卡片 -->
    <div class="overview-card">
      <div class="card-header">
        <h3 class="card-title">项目概况</h3>
      </div>
      <!-- 统计卡片（8个单功能卡片） -->
      <el-row :gutter="16" class="stat-row">
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="stat-card" @click="$router.push('/projects')">
            <div class="stat-header">
              <div class="stat-icon-wrap blue">
                <el-icon :size="22"><Folder /></el-icon>
              </div>
              <div class="stat-title">进行中项目</div>
            </div>
            <div class="stat-body">
              <div class="stat-main-value">12</div>
              <div class="stat-sub-value">个进行中项目</div>
            </div>
            <div class="stat-footer">
              <span class="stat-trend up">较上周 +3</span>
            </div>
          </div>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="stat-card" @click="$router.push('/projects')">
            <div class="stat-header">
              <div class="stat-icon-wrap green">
                <el-icon :size="22"><CircleCheck /></el-icon>
              </div>
              <div class="stat-title">完成任务</div>
            </div>
            <div class="stat-body">
              <div class="stat-main-value">89</div>
              <div class="stat-sub-value">个已完成任务</div>
            </div>
            <div class="stat-footer">
              <el-progress :percentage="57" :show-text="false" :stroke-width="4" />
              <span class="stat-sub">完成率 57%</span>
            </div>
          </div>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="stat-card" @click="$router.push('/projects')">
            <div class="stat-header">
              <div class="stat-icon-wrap red">
                <el-icon :size="22"><WarningFilled /></el-icon>
              </div>
              <div class="stat-title">发现问题</div>
            </div>
            <div class="stat-body">
              <div class="stat-main-value">68</div>
              <div class="stat-sub-value">个问题</div>
            </div>
            <div class="stat-footer">
              <el-tag type="danger" size="small">15 待解决</el-tag>
            </div>
          </div>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="stat-card" @click="$router.push('/projects')">
            <div class="stat-header">
              <div class="stat-icon-wrap warning">
                <el-icon :size="22"><Lightning /></el-icon>
              </div>
              <div class="stat-title">风险项</div>
            </div>
            <div class="stat-body">
              <div class="stat-main-value">16</div>
              <div class="stat-sub-value">项风险</div>
            </div>
            <div class="stat-footer">
              <el-tag type="warning" size="small">12 已管控</el-tag>
            </div>
          </div>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="stat-card" @click="$router.push('/projects')">
            <div class="stat-header">
              <div class="stat-icon-wrap purple">
                <el-icon :size="22"><Box /></el-icon>
              </div>
              <div class="stat-title">待交付</div>
            </div>
            <div class="stat-body">
              <div class="stat-main-value">6</div>
              <div class="stat-sub-value">个待交付</div>
            </div>
            <div class="stat-footer">
              <span class="stat-date">本周到期 3 个</span>
            </div>
          </div>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="stat-card" @click="$router.push('/projects')">
            <div class="stat-header">
              <div class="stat-icon-wrap cyan">
                <el-icon :size="22"><Clock /></el-icon>
              </div>
              <div class="stat-title">本周截止</div>
            </div>
            <div class="stat-body">
              <div class="stat-main-value">5</div>
              <div class="stat-sub-value">个任务</div>
            </div>
            <div class="stat-footer">
              <span class="stat-date">02/10 - 02/14</span>
            </div>
          </div>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="stat-card" @click="$router.push('/approvals')">
            <div class="stat-header">
              <div class="stat-icon-wrap pink">
                <el-icon :size="22"><Stamp /></el-icon>
              </div>
              <div class="stat-title">待审批</div>
            </div>
            <div class="stat-body">
              <div class="stat-main-value">3</div>
              <div class="stat-sub-value">项申请</div>
            </div>
            <div class="stat-footer">
              <el-tag type="warning" size="small">2 计划变更</el-tag>
            </div>
          </div>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="stat-card" @click="$router.push('/projects')">
            <div class="stat-header">
              <div class="stat-icon-wrap orange">
                <el-icon :size="22"><Tickets /></el-icon>
              </div>
              <div class="stat-title">任务总数</div>
            </div>
            <div class="stat-body">
              <div class="stat-main-value">156</div>
              <div class="stat-sub-value">个任务</div>
            </div>
            <div class="stat-footer">
              <span class="stat-trend down">较上周 -12</span>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 最近项目 + 待办 -->
    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :xs="24" :lg="12">
        <div class="content-card">
          <div class="card-header">
            <h3 class="card-title">最近项目</h3>
            <el-link type="primary" :underline="false" size="small">全部</el-link>
          </div>
          <div class="project-list">
            <div class="project-item" v-for="project in projects" :key="project.id">
              <div class="project-main">
                <h4 class="project-name">{{ project.name }}</h4>
                <el-progress :percentage="project.progress" :stroke-width="6" :show-text="false" />
              </div>
              <span class="project-progress-text">{{ project.progress }}%</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="content-card">
          <div class="card-header">
            <h3 class="card-title">我的待办</h3>
            <el-link type="primary" :underline="false" size="small">全部</el-link>
          </div>
          <div class="todo-list">
            <div class="todo-item" v-for="item in todos" :key="item.id">
              <el-checkbox v-model="item.done" size="small" />
              <span class="todo-title" :class="{ done: item.done }">{{ item.title }}</span>
              <el-tag :type="getPriorityType(item.priority)" size="small" effect="plain">
                {{ item.priorityLabel }}
              </el-tag>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Folder, CircleCheck, WarningFilled, Lightning, Box, Clock, Stamp, Tickets } from '@element-plus/icons-vue'

const todos = ref([
  { id: 1, title: '完成项目管理系统需求文档', done: false, priority: 'high', priorityLabel: '高' },
  { id: 2, title: '评审前端架构设计方案', done: false, priority: 'medium', priorityLabel: '中' },
  { id: 3, title: '安排项目会议', done: false, priority: 'low', priorityLabel: '低' },
  { id: 4, title: '更新甘特图时间线', done: true, priority: 'medium', priorityLabel: '中' }
])

const projects = ref([
  { id: 1, name: '企业项目管理系统 V1.0', progress: 65 },
  { id: 2, name: '技术架构升级', progress: 30 },
  { id: 3, name: '客户门户优化', progress: 85 }
])

const getPriorityType = (priority) => {
  const map = { high: 'danger', medium: 'warning', low: 'info' }
  return map[priority] || 'info'
}
</script>

<style scoped>
.dashboard {
  max-width: 1600px;
  margin: 0 auto;
}

/* 项目概况大卡片 */
.overview-card {
  background: #FFFFFF;
  border-radius: 8px;
  border: 1px solid #E4E7ED;
  padding: 20px;
}

.overview-card .card-header {
  margin-bottom: 16px;
}

.overview-card .card-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

.stat-row {
  margin-bottom: 0;
}

/* 8个单功能统计卡片 */
.stat-card {
  background: #FFFFFF;
  border-radius: 8px;
  border: 1px solid #E4E7ED;
  padding: 16px;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: all 0.2s;
  height: 180px;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.stat-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.stat-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon-wrap.blue { background: rgba(30, 94, 184, 0.1); color: #1E5EB8; }
.stat-icon-wrap.green { background: rgba(82, 196, 26, 0.1); color: #52C41A; }
.stat-icon-wrap.orange { background: rgba(250, 173, 20, 0.1); color: #FAAD14; }
.stat-icon-wrap.red { background: rgba(255, 77, 79, 0.1); color: #FF4D4F; }
.stat-icon-wrap.warning { background: rgba(250, 140, 22, 0.1); color: #FA8C16; }
.stat-icon-wrap.purple { background: rgba(114, 46, 209, 0.1); color: #722ED1; }
.stat-icon-wrap.cyan { background: rgba(19, 194, 194, 0.1); color: #13C2C2; }
.stat-icon-wrap.pink { background: rgba(235, 47, 150, 0.1); color: #EB2F96; }

.stat-title {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
}

.stat-body {
  flex: 1;
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.stat-main-value {
  font-size: 32px;
  font-weight: 700;
  color: #262626;
  line-height: 1.1;
}

.stat-sub-value {
  font-size: 14px;
  color: #8C8C8C;
}

.stat-footer {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid #F0F0F0;
}

.stat-trend {
  font-size: 12px;
  font-weight: 500;
}

.stat-trend.up { color: #52C41A; }
.stat-trend.down { color: #FF4D4F; }

.stat-date {
  font-size: 12px;
  color: #595959;
  background: #F5F7FA;
  padding: 2px 8px;
  border-radius: 4px;
}

/* 内容卡片 */
.content-card {
  background: #FFFFFF;
  border-radius: 8px;
  border: 1px solid #E4E7ED;
  padding: 20px;
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

/* 任务统计 */
.task-stats {
  display: flex;
  gap: 32px;
  align-items: center;
}

.task-stat-item {
  flex-shrink: 0;
}

.progress-inner {
  text-align: center;
}

.progress-inner .progress-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #262626;
}

.progress-inner .progress-label {
  display: block;
  font-size: 12px;
  color: #8C8C8C;
}

.task-stat-bars {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-bar-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-bar-label {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #595959;
}

.stat-bar-value {
  font-weight: 600;
}

/* 风险问题统计 */
.risk-issue-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.risk-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.risk-bar-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.risk-label {
  width: 56px;
  font-size: 12px;
  color: #8C8C8C;
}

.risk-bar-item .el-progress {
  flex: 1;
}

.risk-count {
  width: 24px;
  text-align: right;
  font-size: 12px;
  font-weight: 600;
  color: #262626;
}

.issue-nums {
  display: flex;
  justify-content: space-around;
}

.issue-num {
  text-align: center;
}

.issue-num .issue-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #262626;
}

.issue-num .issue-label {
  display: block;
  font-size: 12px;
  color: #8C8C8C;
  margin-top: 4px;
}

/* 待办列表 */
.todo-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.todo-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: #F9FAFB;
  border-radius: 6px;
}

.todo-title {
  flex: 1;
  font-size: 14px;
  color: #262626;
}

.todo-title.done {
  text-decoration: line-through;
  color: #BFBFBF;
}

/* 项目列表 */
.project-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.project-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: #F9FAFB;
  border-radius: 6px;
}

.project-main {
  flex: 1;
}

.project-name {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
  margin: 0 0 8px 0;
}

.project-main .el-progress {
  width: 100%;
}

.project-progress-text {
  font-size: 13px;
  font-weight: 600;
  color: #595959;
  min-width: 40px;
  text-align: right;
}
</style>
