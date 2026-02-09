<template>
  <div class="board-page">
      role="main"
      aria-label="任务看板页面"
    <!-- 页面头部 -->
    <div class="board-header">
      role="banner"
      aria-label="任务看板标题"
      <div class="header-left">
        <span class="board-title">任务看板</span>
      </div>
      <div class="header-right">
        <!-- 搜索框 -->
        <el-input
          v-model="searchKeyword"
          placeholder="搜索任务..."
          :prefix-icon="Search"
          clearable
          size="default"
          class="search-input"
        />
        <!-- 优先级筛选 -->
        <el-select v-model="filterPriority" placeholder="按优先级筛选"
            aria-label="优先级筛选" clearable size="default" class="filter-select">
          <el-option label="紧急" value="high" />
          <el-option label="中" value="medium" />
          <el-option label="低" value="low" />
        </el-select>
        <!-- 项目选择器 -->
        <el-select v-model="currentProject" placeholder="选择项目"
            aria-label="项目筛选" size="default" class="project-select">
          <el-option
            v-for="p in projects"
            :key="p.id"
            :label="p.name"
            :value="p.id"
          />
        </el-select>
        <!-- 新建任务按钮 -->
        <el-button type="primary" :icon="Plus" @click="openCreateDialog"
            aria-label="新建任务"
            @keydown.enter="openCreateDialog">新建任务</el-button>
      </div>
    </div>

    <!-- 看板主体 -->
    <div class="board-body" v-loading="loading">
      <!-- 无任务提示 -->
      <el-empty v-if="!hasVisibleTasks" description="暂无任务" :image-size="120">
            role="alert"
            aria-live="assertive"
            aria-label="当前没有任务"
        <el-button type="primary" @click="openCreateDialog"
            aria-label="新建任务"
            @keydown.enter="openCreateDialog">新建任务</el-button>
      </el-empty>
      
      <!-- 看板列 -->
      <div class="board-columns" v-else>
            role="listbox"
            aria-label="任务列表"
            aria-live="polite"
        <div
          v-for="column in columns"
          :key="column.id"
          class="board-column"
          :style="{ backgroundColor: column.bgColor }"
        >
          <!-- 列头部 -->
          <div class="column-header">
            <span class="column-title" :style="{ color: column.color }">
              {{ column.title }}
            </span>
            <span class="column-count">{{ getTasksByStatus(column.status).length }}</span>
          </div>

          <!-- 任务列表 -->
          <draggable
            :list="getTasksByStatus(column.status)"
            group="tasks"
            item-key="id"
            class="task-list"
            ghost-class="ghost"
            @change="(evt) => handleDragChange(evt, column.status)"
          >
            <template #item="{ element: task }">
              <div class="task-card" @click="openTaskDetail(task)">
              role="option"
              tabindex="0"
              :aria-selected="selectedTaskId === task.id"
              @keydown.enter="openTaskDetail(task)"
              @keydown.space="openTaskDetail(task)"
              @keydown.ArrowUp="handleArrowUp(task)"
              @keydown.ArrowDown="handleArrowDown(task)"
                <!-- 优先级标签 -->
                <div class="task-header">
                  <el-tag :type="getPriorityType(task.priority)" size="small" effect="dark">
                    {{ getPriorityLabel(task.priority) }}
                  </el-tag>
                  <el-dropdown trigger="click" @command="(cmd) => handleTaskAction(cmd, task)">
                    <el-icon class="task-action-btn"><MoreFilled /></el-icon>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="edit" aria-label="编辑任务">编辑</el-dropdown-item>
                        <el-dropdown-item command="delete" aria-label="删除任务" divided>删除</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>

                <!-- 任务标题 -->
                <div class="task-title">{{ task.title }}</div>
                
                <!-- 所属项目 -->
                <div class="task-project" v-if="task.projectId">
                  <el-icon><Folder /></el-icon>
                  <span>{{ getProjectName(task.projectId) }}</span>
                </div>

                <!-- 标签 -->
                <div class="task-tags" v-if="task.tags && task.tags.length">
                  <el-tag
                    v-for="tag in task.tags.slice(0, 2)"
                    :key="tag"
                    size="small"
                    effect="plain"
                  >
                    {{ tag }}
                  </el-tag>
                </div>

                <!-- 底部信息 -->
                <div class="task-footer">
                  <div class="task-assignee" v-if="task.assignee">
                    <el-avatar :size="20" :src="task.assignee.avatar">
                      {{ task.assignee.name.charAt(0) }}
                    </el-avatar>
                    <span>{{ task.assignee.name }}</span>
                  </div>
                  <div class="task-meta">
                    <span class="task-due" v-if="task.dueDate" :class="{ overdue: isOverdue(task.dueDate) }">
                      <el-icon><Calendar /></el-icon>
                      {{ formatDate(task.dueDate) }}
                    </span>
                  </div>
                </div>
              </div>
            </template>
          </draggable>
        </div>
      </div>
    </div>

    <!-- 任务详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      :title="currentTask?.title"
      width="680px"
      destroy-on-close
    >
      <template v-if="currentTask">
        <div class="task-detail">
          <!-- 基本信息 -->
          <div class="detail-section">
            <h4>基本信息</h4>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="状态">
                <el-tag :type="getStatusType(currentTask.status)" size="small">
                  {{ getStatusLabel(currentTask.status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="优先级">
                <el-tag :type="getPriorityType(currentTask.priority)" size="small">
                  {{ getPriorityLabel(currentTask.priority) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="负责人">
                <el-avatar :size="24" :src="currentTask.assignee?.avatar">
                  {{ currentTask.assignee?.name?.charAt(0) }}
                </el-avatar>
                {{ currentTask.assignee?.name }}
              </el-descriptions-item>
              <el-descriptions-item label="截止日期">
                {{ currentTask.dueDate || '未设置' }}
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 任务描述 -->
          <div class="detail-section" v-if="currentTask.description">
            <h4>描述</h4>
            <p class="task-description">{{ currentTask.description }}</p>
          </div>

          <!-- 子任务 -->
          <div class="detail-section">
            <h4>子任务 ({{ currentTask.subtasks?.length || 0 }})</h4>
            <div class="subtask-list">
              <div
                v-for="subtask in currentTask.subtasks"
                :key="subtask.id"
                class="subtask-item"
              >
                <el-checkbox v-model="subtask.completed" @change="updateSubtask(subtask)">
                  <span :class="{ completed: subtask.completed }">{{ subtask.title }}</span>
                </el-checkbox>
              </div>
              <el-empty v-if="!currentTask.subtasks?.length" description="暂无子任务" :image-size="60" />
            role="alert"
            aria-live="assertive"
            aria-label="当前没有任务"
            </div>
          </div>

          <!-- 评论 -->
          <div class="detail-section">
            <h4>评论 ({{ currentTask.comments?.length || 0 }})</h4>
            <div class="comment-list">
              <div v-for="comment in currentTask.comments" :key="comment.id" class="comment-item">
                <el-avatar :size="32" :src="comment.user?.avatar">
                  {{ comment.user?.name?.charAt(0) }}
                </el-avatar>
                <div class="comment-content">
                  <div class="comment-header">
                    <span class="comment-user">{{ comment.user?.name }}</span>
                    <span class="comment-time">{{ comment.createdAt }}</span>
                  </div>
                  <div class="comment-text">{{ comment.content }}</div>
                </div>
              </div>
              <el-empty v-if="!currentTask.comments?.length" description="暂无评论" :image-size="60" />
            role="alert"
            aria-live="assertive"
            aria-label="当前没有任务"
            </div>
          </div>
        </div>
      </template>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="openEditDialog">编辑任务</el-button>
      </template>
    </el-dialog>

    <!-- 新建/编辑任务弹窗 -->
    <el-dialog
      v-model="formVisible"
      :title="isEdit ? '编辑任务' : '新建任务'"
      width="560px"
      destroy-on-close
    >
      <el-form :model="taskForm" :rules="formRules" ref="formRef" label-width="80px">
        <el-form-item label="任务标题" prop="title">
          <el-input v-model="taskForm.title" placeholder="请输入任务标题" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="任务描述" prop="description">
          <el-input v-model="taskForm.description" type="textarea" :rows="3" placeholder="请输入任务描述" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="taskForm.priority" placeholder="选择优先级" style="width: 100%">
                <el-option label="紧急" value="high">
                  <el-tag type="danger" size="small">紧急</el-tag>
                </el-option>
                <el-option label="中" value="medium">
                  <el-tag type="warning" size="small">中</el-tag>
                </el-option>
                <el-option label="低" value="low">
                  <el-tag type="success" size="small">低</el-tag>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="截止日期" prop="dueDate">
              <el-date-picker
                v-model="taskForm.dueDate"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="标签">
          <el-select v-model="taskForm.tags" multiple placeholder="选择标签" style="width: 100%">
            <el-option label="开发" value="开发" />
            <el-option label="设计" value="设计" />
            <el-option label="测试" value="测试" />
            <el-option label="文档" value="文档" />
            <el-option label="优化" value="优化" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitLoading">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Calendar, Search, MoreFilled, Folder } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'

// 状态
const loading = ref(false)
const submitLoading = ref(false)
const detailVisible = ref(false)
const formVisible = ref(false)
const isEdit = ref(false)
const currentTask = ref(null)
const formRef = ref(null)
const searchKeyword = ref('')
const filterPriority = ref('')

// 项目列表
const projects = ref([
  { id: 1, name: '企业项目管理系统 V1.0' },
  { id: 2, name: '移动端 APP 开发' },
  { id: 3, name: '数据分析平台' }
])

// 当前选中项目
const currentProject = ref(1)

// 看板列配置
const columns = ref([
  { id: 'draft', title: '草稿', status: 'draft', color: '#8C8C8C', bgColor: '#FAFAFA' },
  { id: 'in_progress', title: '进行中', status: 'in_progress', color: '#1E5EB8', bgColor: '#E6F4FF' },
  { id: 'done', title: '已完成', status: 'done', color: '#52C41A', bgColor: '#F6FFED' }
])

// 任务列表
const tasks = ref([])

// 表单数据
const taskForm = ref({
  id: null,
  title: '',
  description: '',
  priority: 'medium',
  dueDate: '',
  tags: [],
  status: 'todo'
})

// 表单验证规则
const formRules = {
  title: [
    { required: true, message: '请输入任务标题', trigger: 'blur' },
    { min: 2, max: 100, message: '标题长度为 2-100 个字符', trigger: 'blur' }
  ]
}

// 获取某状态的任务列表
const getTasksByStatus = (status) => {
  let filtered = tasks.value.filter(task => task.status === status)
  
  // 搜索筛选
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(task => 
      task.title.toLowerCase().includes(keyword) ||
      task.description?.toLowerCase().includes(keyword)
    )
  }
  
  // 优先级筛选
  if (filterPriority.value) {
    filtered = filtered.filter(task => task.priority === filterPriority.value)
  }
  
  return filtered
}

// 是否有可见任务
const hasVisibleTasks = computed(() => {
  return columns.value.some(column => getTasksByStatus(column.status).length > 0)
})

// 获取项目名称
const getProjectName = (projectId) => {
  const project = projects.value.find(p => p.id === projectId)
  return project?.name || '未知项目'
}

// 打开新建任务弹窗
const openCreateDialog = () => {
  isEdit.value = false
  taskForm.value = {
    id: null,
    title: '',
    description: '',
    priority: 'medium',
    dueDate: '',
    tags: [],
    status: 'todo'
  }
  formVisible.value = true
}

// 打开任务详情
const openTaskDetail = (task) => {
  currentTask.value = task
  detailVisible.value = true
}

// 打开编辑弹窗
const openEditDialog = () => {
  isEdit.value = true
  taskForm.value = { ...currentTask.value }
  detailVisible.value = false
  formVisible.value = true
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          // 编辑模式
          const index = tasks.value.findIndex(t => t.id === taskForm.value.id)
          if (index !== -1) {
            tasks.value[index] = { ...tasks.value[index], ...taskForm.value }
          }
          ElMessage.success('任务已更新')
        } else {
          // 新建模式
          const newTask = {
            ...taskForm.value,
            id: Date.now(),
            status: 'todo',
            projectId: currentProject.value,
            assignee: { id: 1, name: '张经理', avatar: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png' },
            subtasks: [],
            comments: [],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          }
          tasks.value.unshift(newTask)
          ElMessage.success('任务已创建')
        }
        formVisible.value = false
      } catch (e) {
        ElMessage.error('操作失败，请重试')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// 处理拖拽变化
const handleDragChange = (evt, status) => {
  if (evt.added) {
    const task = evt.added.element
    task.status = status
    ElMessage.success(`任务已移动到"${columns.value.find(c => c.status === status).title}"`)
  }
}

// 处理任务操作

const selectedTaskId = ref(null)

const handleArrowUp = (task) => {
  const currentIndex = tasks.value.findIndex(t => t.id === task.id)
  if (currentIndex > 0) {
    selectedTaskId.value = tasks.value[currentIndex - 1].id
  }
}

const handleArrowDown = (task) => {
  const currentIndex = tasks.value.findIndex(t => t.id === task.id)
  if (currentIndex < tasks.value.length - 1) {
    selectedTaskId.value = tasks.value[currentIndex + 1].id
  }
}

const handleKeydown = (event, task) => {
  switch (event.key) {
    case 'Enter':
      event.preventDefault()
      openTaskDetail(task)
      break
    case ' ':
      event.preventDefault()
      openTaskDetail(task)
      break
    case 'ArrowUp':
      handleArrowUp(task)
      break
    case 'ArrowDown':
      handleArrowDown(task)
      break
  }
}

const handleTaskAction = async (command, task) => {
  if (command === 'edit') {
    openEditDialog(task)
  } else if (command === 'delete') {
    try {
      await ElMessageBox.confirm('确定要删除该任务吗？', '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      tasks.value = tasks.value.filter(t => t.id !== task.id)
      ElMessage.success('任务已删除')
    } catch {
      // 用户取消
    }
  }
}

// 更新子任务
const updateSubtask = (subtask) => {
  subtask.completed = !subtask.completed
  ElMessage.success(subtask.completed ? '子任务已完成' : '子任务已取消')
}

// 获取优先级类型
const getPriorityType = (priority) => {
  const map = { high: 'danger', medium: 'warning', low: 'success' }
  return map[priority] || 'info'
}

// 获取优先级标签
const getPriorityLabel = (priority) => {
  const map = { high: '紧急', medium: '中', low: '低' }
  return map[priority] || priority
}

// 获取状态类型
const getStatusType = (status) => {
  const map = { draft: 'info', todo: 'info', in_progress: 'primary', done: 'success' }
  return map[status] || 'info'
}

// 获取状态标签
const getStatusLabel = (status) => {
  const map = { draft: '草稿', todo: '待办', in_progress: '进行中', done: '已完成' }
  return map[status] || status
}

// 格式化日期
const formatDate = (date) => {
  return date.substring(5) // MM-DD 格式
}

// 检查是否过期
const isOverdue = (date) => {
  return new Date(date) < new Date()
}

// 加载任务数据
const loadTasks = () => {
  loading.value = true
  // Mock 数据
  setTimeout(() => {
    tasks.value = [
      {
        id: 1,
        projectId: 1,
        title: '完成用户认证模块',
        description: '实现登录、注册、找回密码功能，包括 JWT Token 验证',
        status: 'in_progress',
        priority: 'high',
        assignee: { id: 1, name: '张经理', avatar: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png' },
        dueDate: '2026-02-15',
        tags: ['开发', '后端'],
        subtasks: [
          { id: 1, title: '设计数据库', completed: true },
          { id: 2, title: '编写API', completed: false },
          { id: 3, title: '单元测试', completed: false }
        ],
        comments: [
          { id: 1, user: { id: 2, name: '李开发', avatar: '' }, content: 'API已提交测试', createdAt: '2小时前' }
        ],
        createdAt: '2026-02-01',
        updatedAt: '2026-02-08'
      },
      {
        id: 2,
        projectId: 1,
        title: '设计前端页面',
        description: '完成所有页面的 UI 设计和原型图',
        status: 'draft',
        priority: 'medium',
        assignee: { id: 2, name: '李开发', avatar: '' },
        dueDate: '2026-02-20',
        tags: ['设计', '前端'],
        subtasks: [],
        comments: [],
        createdAt: '2026-02-02',
        updatedAt: '2026-02-02'
      },
      {
        id: 3,
        projectId: 1,
        title: '数据库优化',
        description: '对慢查询进行优化，添加必要的索引',
        status: 'done',
        priority: 'low',
        assignee: { id: 1, name: '张经理', avatar: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png' },
        dueDate: '2026-02-10',
        tags: ['优化', '数据库'],
        subtasks: [
          { id: 1, title: '分析慢查询', completed: true },
          { id: 2, title: '添加索引', completed: true }
        ],
        comments: [],
        createdAt: '2026-02-03',
        updatedAt: '2026-02-08'
      },
      {
        id: 4,
        projectId: 1,
        title: 'API 接口文档',
        description: '编写所有 API 接口的文档',
        status: 'draft',
        priority: 'medium',
        assignee: { id: 3, name: '王测试', avatar: '' },
        dueDate: '2026-02-25',
        tags: ['文档'],
        subtasks: [],
        comments: [],
        createdAt: '2026-02-05',
        updatedAt: '2026-02-05'
      },
      {
        id: 5,
        projectId: 1,
        title: '性能测试',
        description: '对系统进行压力测试和性能优化',
        status: 'in_progress',
        priority: 'high',
        assignee: { id: 2, name: '李开发', avatar: '' },
        dueDate: '2026-02-18',
        tags: ['测试'],
        subtasks: [
          { id: 1, title: '编写测试用例', completed: true },
          { id: 2, title: '执行压力测试', completed: false }
        ],
        comments: [],
        createdAt: '2026-02-06',
        updatedAt: '2026-02-08'
      },
      {
        id: 6,
        projectId: 1,
        title: '部署上线',
        description: '完成生产环境部署和监控配置',
        status: 'done',
        priority: 'high',
        assignee: { id: 1, name: '张经理', avatar: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png' },
        dueDate: '2026-02-01',
        tags: ['运维'],
        subtasks: [
          { id: 1, title: '配置服务器', completed: true },
          { id: 2, title: '配置监控', completed: true }
        ],
        comments: [],
        createdAt: '2026-01-28',
        updatedAt: '2026-02-01'
      }
    ]
    loading.value = false
  }, 500)
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.board-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 页面头部 */
.board-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #F0F0F0;
}

.board-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 200px;
}

.filter-select {
  width: 120px;
}

.project-select {
  width: 200px;
}

/* 看板主体 */
.board-body {
  flex: 1;
  padding: 24px;
  overflow: hidden;
}

.board-columns {
  display: flex;
  gap: 16px;
  height: 100%;
  overflow-x: auto;
}

/* 看板列 */
.board-column {
  flex: 0 0 320px;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  max-height: 100%;
}

.column-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 12px 8px 12px;
}

.column-title {
  font-size: 14px;
  font-weight: 600;
}

.column-count {
  font-size: 12px;
  color: #8C8C8C;
  background: rgba(0, 0, 0, 0.06);
  padding: 2px 8px;
  border-radius: 10px;
}

/* 任务列表 */
.task-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px 8px 8px;
  min-height: 100px;
}

/* 拖拽样式 */
.ghost {
  opacity: 0.5;
  background: #E6F4FF;
}

/* 任务卡片 */
.task-card {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #E8E8E8;
}

.task-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #1E5EB8;
}

.task-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.task-action-btn {
  cursor: pointer;
  color: #8C8C8C;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.task-action-btn:hover {
  background: #F0F0F0;
  color: #262626;
}

.task-title {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
  margin-bottom: 8px;
  line-height: 1.5;
}

.task-project {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #8C8C8C;
  margin-bottom: 8px;
}

.task-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 8px;
}

.task-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: #8C8C8C;
}

.task-assignee {
  display: flex;
  align-items: center;
  gap: 4px;
}

.task-due {
  display: flex;
  align-items: center;
  gap: 2px;
}

.task-due.overdue {
  color: #FF4D4F;
}

/* 任务详情弹窗 */
.task-detail {
  max-height: 60vh;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #F0F0F0;
}

.task-description {
  color: #595959;
  line-height: 1.6;
}

/* 子任务 */
.subtask-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.subtask-item {
  padding: 8px 0;
}

.subtask-item .completed {
  text-decoration: line-through;
  color: #8C8C8C;
}

/* 评论 */
.comment-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item {
  display: flex;
  gap: 12px;
}

.comment-content {
  flex: 1;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.comment-user {
  font-weight: 500;
  color: #262626;
}

.comment-time {
  font-size: 12px;
  color: #8C8C8C;
}

.comment-text {
  color: #595959;
  line-height: 1.5;
}

/* 焦点状态 - 任务看板 */
.task-card:focus-visible {
  outline: 2px solid #1890ff;
  outline-offset: 2px;
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.15);
  transform: translateY(-2px);
  z-index: 1;
  position: relative;
}

.column-header:focus-visible {
  outline: 2px solid #1890ff;
  outline-offset: 2px;
}

.task-action-btn:focus-visible {
  outline: 2px solid #1890ff;
  outline-offset: 2px;
  background-color: #e6f7ff;
  color: #1890ff;
}

/* 列焦点 */
.board-column:focus-visible {
  outline: 2px solid #1890ff;
  outline-offset: 2px;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.1);
}

/* 焦点辅助类 */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* 加载状态 */
.task-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

</style>
