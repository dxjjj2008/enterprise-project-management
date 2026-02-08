<template>
  <div class="board-page">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">任务看板</h1>
        <el-tag type="success" size="small">进行中</el-tag>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showCreateTask = true">
          <el-icon><Plus /></el-icon>
          新建任务
        </el-button>
      </div>
    </div>

    <!-- 测试数据存在 -->
    <div class="debug-info">
      <p>任务数量: {{ tasks.length }}</p>
      <p>列数: {{ columns.length }}</p>
    </div>

    <!-- 看板 -->
    <div class="kanban-board">
      <div
        v-for="column in columns"
        :key="column.id"
        class="kanban-column"
        :class="`kanban-column-${column.id}`"
      >
        <div class="kanban-column-header">
          <span class="column-title">{{ column.name }}</span>
          <span class="column-count">{{ getColumnTasks(column.id).length }}</span>
        </div>

        <div class="kanban-column-content">
          <div
            v-for="task in getColumnTasks(column.id)"
            :key="task.id"
            class="task-card"
          >
            <h4 class="task-title">{{ task.title }}</h4>
            <p class="task-priority">优先级: {{ task.priority }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'

const showCreateTask = ref(false)

const columns = ref([
  { id: 'todo', name: '待办' },
  { id: 'in_progress', name: '进行中' },
  { id: 'review', name: '审核中' },
  { id: 'done', name: '已完成' }
])

const tasks = ref([
  { id: 1, title: '完成项目需求分析文档', status: 'todo', priority: 'high' },
  { id: 2, title: '设计数据库架构', status: 'in_progress', priority: 'urgent' },
  { id: 3, title: '前端页面原型设计', status: 'in_progress', priority: 'medium' },
  { id: 4, title: 'API 接口定义', status: 'review', priority: 'high' },
  { id: 5, title: '项目启动会议', status: 'done', priority: 'medium' }
])

const getColumnTasks = (columnId) => {
  return tasks.value.filter(task => task.status === columnId)
}
</script>

<style scoped>
.board-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

.debug-info {
  background: #FFF7E6;
  border: 1px solid #FFD591;
  border-radius: 6px;
  padding: 12px 16px;
  margin-bottom: 20px;
}

.debug-info p {
  margin: 4px 0;
  font-size: 13px;
  color: #8C8C8C;
}

.kanban-board {
  display: flex;
  gap: 16px;
  flex: 1;
  overflow-x: auto;
}

.kanban-column {
  flex-shrink: 0;
  width: 280px;
  background: #E8EBF0;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
}

.kanban-column-header {
  padding: 12px 16px;
  border-bottom: 2px solid transparent;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.kanban-column-todo .kanban-column-header {
  border-bottom-color: #8C8C8C;
}

.kanban-column-in_progress .kanban-column-header {
  border-bottom-color: #1890FF;
}

.kanban-column-review .kanban-column-header {
  border-bottom-color: #FAAD14;
}

.kanban-column-done .kanban-column-header {
  border-bottom-color: #52C41A;
}

.column-title {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
}

.column-count {
  background: #FFFFFF;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  color: #595959;
}

.kanban-column-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.task-card {
  background: #FFFFFF;
  border-radius: 6px;
  border: 1px solid #E8E8E8;
  padding: 12px;
  margin-bottom: 8px;
}

.task-title {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
  margin: 0 0 8px 0;
}

.task-priority {
  font-size: 12px;
  color: #8C8C8C;
  margin: 0;
}
</style>
