<template>
  <div class="planning-detail-page">
    <!-- 面包屑导航 -->
    <div class="breadcrumb-nav" aria-label="面包屑导航">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/planning' }">
          <el-icon><Document /></el-icon>
          计划管理
        </el-breadcrumb-item>
        <el-breadcrumb-item>{{ plan.project_name || '计划详情' }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ plan.name }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- 页面工具栏 -->
    <div class="page-toolbar">
      <div class="toolbar-left">
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <el-divider direction="vertical" />
        <el-button-group>
          <el-button :type="isEditing ? 'primary' : 'default'" @click="toggleEdit">
            <el-icon><Edit /></el-icon>
            {{ isEditing ? '取消编辑' : '编辑' }}
          </el-button>
          <el-button type="primary" @click="savePlan" :loading="saving">
            <el-icon><Check /></el-icon>
            保存
          </el-button>
        </el-button-group>
        <el-divider direction="vertical" />
        <el-button @click="publishPlan">
          <el-icon><Promotion /></el-icon>
          发布计划
        </el-button>
        <el-button @click="showMilestoneDialog = true">
          <el-icon><Flag /></el-icon>
          里程碑
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-button @click="exportPlan">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <!-- 计划概览区域 -->
    <div class="plan-overview">
      <!-- 基本信息卡片 -->
      <el-card class="overview-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
          </div>
        </template>
        <el-form label-position="top" size="small">
          <el-form-item label="计划名称">
            <el-input v-model="plan.name" :disabled="!isEditing" />
          </el-form-item>
          <el-form-item label="关联项目">
            <el-input :value="plan.project_name" disabled />
          </el-form-item>
          <el-form-item label="计划状态">
            <el-select v-model="plan.status" :disabled="!isEditing" style="width: 100%">
              <el-option label="草稿" value="draft" />
              <el-option label="进行中" value="active" />
              <el-option label="已完成" value="completed" />
              <el-option label="已暂停" value="on_hold" />
              <el-option label="已归档" value="archived" />
            </el-select>
          </el-form-item>
          <el-form-item label="计划周期">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              :disabled="!isEditing"
              style="width: 100%"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item label="计划描述">
            <el-input
              v-model="plan.description"
              type="textarea"
              :rows="3"
              :disabled="!isEditing"
            />
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 进度统计卡片 -->
      <el-card class="overview-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>进度统计</span>
          </div>
        </template>
        <div class="progress-stats">
          <div class="stat-item">
            <div class="stat-value">{{ wbsTasks.length }}</div>
            <div class="stat-label">总任务数</div>
          </div>
          <div class="stat-item success">
            <div class="stat-value">{{ completedTaskCount }}</div>
            <div class="stat-label">已完成</div>
          </div>
          <div class="stat-item primary">
            <div class="stat-value">{{ inProgressTaskCount }}</div>
            <div class="stat-label">进行中</div>
          </div>
          <div class="stat-item warning">
            <div class="stat-value">{{ overdueTaskCount }}</div>
            <div class="stat-label">逾期</div>
          </div>
        </div>
        <div class="overall-progress">
          <div class="progress-label">
            <span>整体进度</span>
            <span class="progress-value">{{ plan.progress }}%</span>
          </div>
          <el-progress
            :percentage="plan.progress"
            :stroke-width="12"
            :color="getProgressColor(plan.progress)"
          />
        </div>
      </el-card>
    </div>

    <!-- WBS编辑器 -->
    <div class="wbs-editor">
      <div class="wbs-header">
        <h3>工作分解结构 (WBS)</h3>
        <div class="wbs-actions">
          <el-button size="small" @click="addTask(null)">
            <el-icon><Plus /></el-icon>
            添加任务
          </el-button>
        </div>
      </div>

      <!-- WBS工具栏 -->
      <div class="wbs-toolbar" v-if="selectedTask">
        <el-tooltip content="添加同级任务 (Ctrl+N)" placement="top">
          <el-button size="small" @click="addSiblingTask" :disabled="!selectedTask">
            <el-icon><Plus /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="添加子任务 (Ctrl+Shift+N)" placement="top">
          <el-button size="small" @click="addChildTask" :disabled="!selectedTask">
            <el-icon><PlusIcon /></el-icon>
          </el-button>
        </el-tooltip>
        <el-divider direction="vertical" />
        <el-tooltip content="升级 (Ctrl+←)" placement="top">
          <el-button size="small" @click="upgradeTask" :disabled="!canUpgrade">
            <el-icon><ArrowLeft /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="降级 (Ctrl+→)" placement="top">
          <el-button size="small" @click="downgradeTask" :disabled="!canDowngrade">
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </el-tooltip>
        <el-divider direction="vertical" />
        <el-tooltip content="上移 (Ctrl+↑)" placement="top">
          <el-button size="small" @click="moveUpTask" :disabled="!canMoveUp">
            <el-icon><Top /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="下移 (Ctrl+↓)" placement="top">
          <el-button size="small" @click="moveDownTask" :disabled="!canMoveDown">
            <el-icon><Bottom /></el-icon>
          </el-button>
        </el-tooltip>
        <el-divider direction="vertical" />
        <el-tooltip content="复制 (Ctrl+C)" placement="top">
          <el-button size="small" @click="copyTask" :disabled="!selectedTask">
            <el-icon><CopyDocument /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="粘贴 (Ctrl+V)" placement="top">
          <el-button size="small" @click="pasteTask" :disabled="!copiedTask">
            <el-icon><DocumentCopy /></el-icon>
          </el-button>
        </el-tooltip>
        <el-divider direction="vertical" />
        <el-tooltip content="删除 (Delete)" placement="top">
          <el-button size="small" type="danger" @click="deleteTask" :disabled="!selectedTask">
            <el-icon><Delete /></el-icon>
          </el-button>
        </el-tooltip>
      </div>

      <!-- WBS树形表格 -->
      <div class="wbs-tree-table">
        <el-table
          :data="wbsTasks"
          row-key="id"
          default-expand-all
          :tree-props="{ children: 'children' }"
          @selection-change="handleSelectionChange"
          @row-click="handleRowClick"
          highlight-current-row
          v-loading="loading"
        >
          <el-table-column type="selection" width="48" />
          <el-table-column label="序号" width="80">
            <template #default="{ row, rowIndex }">
              <span>{{ getTaskNumber(row, rowIndex) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="任务名称" min-width="250">
            <template #default="{ row }">
              <div class="task-name-cell">
                <el-icon v-if="row.children && row.children.length" class="expand-icon" @click.stop="toggleExpand(row)">
                  <component :is="row._expanded ? 'ArrowDown' : 'ArrowRight'" />
                </el-icon>
                <el-icon v-else class="expand-icon placeholder" />
                <el-icon v-if="row.is_milestone" class="milestone-icon">
                  <Flag />
                </el-icon>
                <el-checkbox
                  v-model="row._checked"
                  @change="(val) => toggleTaskComplete(row, val)"
                  class="task-checkbox"
                />
                <el-input
                  v-model="row.name"
                  size="small"
                  :disabled="!isEditing"
                  class="task-name-input"
                  @change="(val) => markTaskChanged(row)"
                />
              </div>
            </template>
          </el-table-column>
          <el-table-column label="负责人" width="140">
            <template #default="{ row }">
              <el-select
                v-model="row.assignee_id"
                size="small"
                :disabled="!isEditing"
                placeholder="选择成员"
                style="width: 100%"
                @change="(val) => markTaskChanged(row)"
              >
                <el-option
                  v-for="member in teamMembers"
                  :key="member.id"
                  :label="member.name"
                  :value="member.id"
                >
                  <el-avatar :size="20" :src="member.avatar">{{ member.name.charAt(0) }}</el-avatar>
                  <span style="margin-left: 8px">{{ member.name }}</span>
                </el-option>
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="开始日期" width="140">
            <template #default="{ row }">
              <el-date-picker
                v-model="row.start_date"
                type="date"
                size="small"
                :disabled="!isEditing"
                style="width: 100%"
                value-format="YYYY-MM-DD"
                @change="(val) => markTaskChanged(row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="结束日期" width="140">
            <template #default="{ row }">
              <el-date-picker
                v-model="row.end_date"
                type="date"
                size="small"
                :disabled="!isEditing"
                style="width: 100%"
                value-format="YYYY-MM-DD"
                @change="(val) => markTaskChanged(row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="工期(天)" width="100">
            <template #default="{ row }">
              <el-input-number
                v-model="row.duration"
                :min="1"
                :max="365"
                size="small"
                :disabled="!isEditing"
                @change="(val) => markTaskChanged(row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="进度" width="160">
            <template #default="{ row }">
              <div class="progress-cell">
                <el-slider
                  v-model="row.progress"
                  :min="0"
                  :max="100"
                  :disabled="!isEditing"
                  @change="(val) => markTaskChanged(row)"
                />
                <span class="progress-text">{{ row.progress }}%</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="里程碑" width="80" align="center">
            <template #default="{ row }">
              <el-checkbox
                v-model="row.is_milestone"
                :disabled="!isEditing"
                @change="(val) => markTaskChanged(row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click.stop="editTask(row)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button type="danger" link size="small" @click.stop="deleteTask(row)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 里程碑管理弹窗 -->
    <el-dialog
      v-model="showMilestoneDialog"
      title="里程碑管理"
      width="600px"
      destroy-on-close
    >
      <el-table :data="milestones" style="width: 100%">
        <el-table-column prop="name" label="里程碑名称" width="180" />
        <el-table-column prop="plan_date" label="计划日期" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'info'" size="small">
              {{ row.status === 'completed' ? '已完成' : '待完成' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button v-if="row.status !== 'completed'" type="success" link size="small" @click="completeMilestone(row)">
              完成
            </el-button>
            <el-button type="danger" link size="small" @click="removeMilestone(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="showMilestoneDialog = false">关闭</el-button>
        <el-button type="primary" @click="showAddMilestoneDialog = true">
          <el-icon><Plus /></el-icon>
          添加里程碑
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加里程碑弹窗 -->
    <el-dialog
      v-model="showAddMilestoneDialog"
      title="添加里程碑"
      width="400px"
      destroy-on-close
    >
      <el-form :model="newMilestone" label-width="100px">
        <el-form-item label="里程碑名称" required>
          <el-input v-model="newMilestone.name" placeholder="请输入里程碑名称" />
        </el-form-item>
        <el-form-item label="计划日期" required>
          <el-date-picker
            v-model="newMilestone.plan_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="关联任务">
          <el-select v-model="newMilestone.task_id" placeholder="选择关联任务" style="width: 100%">
            <el-option
              v-for="task in allTasks"
              :key="task.id"
              :label="task.name"
              :value="task.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddMilestoneDialog = false">取消</el-button>
        <el-button type="primary" @click="addMilestone">确定</el-button>
      </template>
    </el-dialog>

    <!-- 任务详情弹窗 -->
    <el-dialog
      v-model="showTaskDialog"
      title="任务详情"
      width="560px"
      destroy-on-close
    >
      <el-form :model="editingTask" label-width="100px">
        <el-form-item label="任务名称" required>
          <el-input v-model="editingTask.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="任务描述">
          <el-input
            v-model="editingTask.description"
            type="textarea"
            :rows="3"
            placeholder="请输入任务描述"
          />
        </el-form-item>
        <el-form-item label="执行人">
          <el-select v-model="editingTask.assignee_id" placeholder="选择执行人" style="width: 100%">
            <el-option
              v-for="member in teamMembers"
              :key="member.id"
              :label="member.name"
              :value="member.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="前置任务">
          <el-select
            v-model="editingTask.dependency"
            multiple
            placeholder="选择前置任务"
            style="width: 100%"
          >
            <el-option
              v-for="task in allTasks.filter(t => t.id !== editingTask.id)"
              :key="task.id"
              :label="task.name"
              :value="task.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTaskDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTask">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document, ArrowLeft, Edit, Check, Promotion, Flag, Download,
  Plus, Top, Bottom, CopyDocument, DocumentCopy,
  Delete, ArrowDown, ArrowRight, Minus, Plus as PlusIcon, Close
} from '@element-plus/icons-vue'
import { getPlanById, getWBSTasks, addWBSTask, updateWBSTask, deleteWBSTask, getMilestones, addMilestone as addMilestoneApi, updateMilestone, deleteMilestone as deleteMilestoneApi } from '@/api/planning'

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const isEditing = ref(false)
const plan = ref({})
const wbsTasks = ref([])
const milestones = ref([])
const teamMembers = ref([])
const selectedTask = ref(null)
const copiedTask = ref(null)
const selections = ref([])

// 弹窗控制
const showMilestoneDialog = ref(false)
const showAddMilestoneDialog = ref(false)
const showTaskDialog = ref(false)

const newMilestone = reactive({
  name: '',
  plan_date: '',
  task_id: null
})

const editingTask = reactive({})

// 日期范围计算属性
const dateRange = computed({
  get: () => {
    if (plan.value.start_date && plan.value.end_date) {
      return [plan.value.start_date, plan.value.end_date]
    }
    return []
  },
  set: (val) => {
    if (val && val.length === 2) {
      plan.value.start_date = val[0]
      plan.value.end_date = val[1]
    }
  }
})

// 统计数据
const allTasks = computed(() => {
  const tasks = []
  const flatten = (taskList) => {
    taskList.forEach(task => {
      tasks.push(task)
      if (task.children && task.children.length) {
        flatten(task.children)
      }
    })
  }
  flatten(wbsTasks.value)
  return tasks
})

const completedTaskCount = computed(() => {
  return allTasks.value.filter(t => t.status === 'completed').length
})

const inProgressTaskCount = computed(() => {
  return allTasks.value.filter(t => t.status === 'in_progress').length
})

const overdueTaskCount = computed(() => {
  const now = new Date()
  return allTasks.value.filter(t => {
    if (!t.end_date) return false
    return new Date(t.end_date) < now && t.status !== 'completed'
  }).length
})

// 操作状态
const canUpgrade = computed(() => {
  if (!selectedTask.value) return false
  return selectedTask.value.level > 1
})

const canDowngrade = computed(() => {
  if (!selectedTask.value) return false
  const parent = findParent(selectedTask.value.id)
  return !!parent
})

const canMoveUp = computed(() => {
  if (!selectedTask.value) return false
  const parentTasks = getParentTasks(selectedTask.value)
  const index = parentTasks.findIndex(t => t.id === selectedTask.value.id)
  return index > 0
})

const canMoveDown = computed(() => {
  if (!selectedTask.value) return false
  const parentTasks = getParentTasks(selectedTask.value)
  const index = parentTasks.findIndex(t => t.id === selectedTask.value.id)
  return index < parentTasks.length - 1
})

// 方法
const loadPlan = async () => {
  loading.value = true
  try {
    const planId = route.params.id
    const [planData, tasksData, milestonesData] = await Promise.all([
      getPlanById(planId),
      getWBSTasks(planId),
      getMilestones(planId)
    ])
    plan.value = planData
    wbsTasks.value = buildTaskTree(tasksData)
    milestones.value = milestonesData
  } catch (error) {
    console.error('加载计划数据失败:', error)
    ElMessage.error('加载计划数据失败')
  } finally {
    loading.value = false
  }
}

const buildTaskTree = (tasks) => {
  const taskMap = {}
  const roots = []

  tasks.forEach(task => {
    task._expanded = false
    task._checked = task.status === 'completed'
    task.children = []
    taskMap[task.id] = task
  })

  tasks.forEach(task => {
    if (task.parent_id) {
      if (taskMap[task.parent_id]) {
        taskMap[task.parent_id].children.push(task)
      }
    } else {
      roots.push(task)
    }
  })

  return roots
}

const goBack = () => {
  router.push('/planning')
}

const toggleEdit = () => {
  isEditing.value = !isEditing.value
}

const savePlan = async () => {
  saving.value = true
  try {
    // 保存WBS任务变更
    const tasksToSave = allTasks.value.filter(t => t._changed)
    for (const task of tasksToSave) {
      await updateWBSTask(plan.value.id, task.id, {
        name: task.name,
        assignee_id: task.assignee_id,
        start_date: task.start_date,
        end_date: task.end_date,
        duration: task.duration,
        progress: task.progress,
        is_milestone: task.is_milestone
      })
    }
    ElMessage.success('保存成功')
    isEditing.value = false
    await loadPlan()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const publishPlan = async () => {
  try {
    await ElMessageBox.confirm('发布计划后将对所有相关人员可见，是否继续？', '确认发布', {
      confirmButtonText: '发布',
      cancelButtonText: '取消',
      type: 'warning'
    })
    plan.value.status = 'active'
    ElMessage.success('计划已发布')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('发布失败')
    }
  }
}

const exportPlan = () => {
  ElMessage.info('导出功能开发中')
}

// WBS操作
const handleRowClick = (row) => {
  selectedTask.value = row
}

const handleSelectionChange = (selection) => {
  selections.value = selection
}

const getTaskNumber = (row, index) => {
  return `${index + 1}`
}

const toggleExpand = (row) => {
  row._expanded = !row._expanded
}

const toggleTaskComplete = (row, completed) => {
  row.status = completed ? 'completed' : 'pending'
  row.progress = completed ? 100 : 0
  markTaskChanged(row)
}

const markTaskChanged = (task) => {
  task._changed = true
}

const findParent = (taskId, tasks = wbsTasks.value, parent = null) => {
  for (const task of tasks) {
    if (task.children && task.children.length) {
      const found = task.children.find(t => t.id === taskId)
      if (found) return task
      const result = findParent(taskId, task.children, task)
      if (result) return result
    }
  }
  return parent
}

const getParentTasks = (task) => {
  if (task.parent_id) {
    const parent = findParent(task.parent_id)
    return parent ? parent.children : wbsTasks.value
  }
  return wbsTasks.value
}

const addTask = async (parentId) => {
  if (!isEditing.value) return

  try {
    const newTask = await addWBSTask(plan.value.id, {
      name: '新任务',
      parent_id: parentId,
      start_date: plan.value.start_date,
      end_date: plan.value.end_date,
      duration: 1,
      progress: 0,
      is_milestone: false
    })
    ElMessage.success('任务已添加')
    await loadPlan()
  } catch (error) {
    console.error('添加任务失败:', error)
    ElMessage.error('添加任务失败')
  }
}

const addSiblingTask = () => {
  if (!selectedTask.value) return
  addTask(selectedTask.value.parent_id)
}

const addChildTask = () => {
  if (!selectedTask.value) return
  addTask(selectedTask.value.id)
}

const upgradeTask = () => {
  if (!selectedTask.value || !canUpgrade.value) return
  selectedTask.value.parent_id = selectedTask.value.parent?.parent_id || null
  selectedTask.value.level = selectedTask.value.parent_id ? 2 : 1
  markTaskChanged(selectedTask.value)
}

const downgradeTask = () => {
  if (!selectedTask.value || !canDowngrade.value) return
  const parent = findParent(selectedTask.value.id)
  if (parent) {
    selectedTask.value.parent_id = parent.id
    selectedTask.value.level = parent.level + 1
    markTaskChanged(selectedTask.value)
  }
}

const moveUpTask = () => {
  if (!selectedTask.value || !canMoveUp.value) return
  const parentTasks = getParentTasks(selectedTask.value)
  const index = parentTasks.findIndex(t => t.id === selectedTask.value.id)
  const temp = parentTasks[index - 1]
  parentTasks[index - 1] = parentTasks[index]
  parentTasks[index] = temp
  markTaskChanged(selectedTask.value)
}

const moveDownTask = () => {
  if (!selectedTask.value || !canMoveDown.value) return
  const parentTasks = getParentTasks(selectedTask.value)
  const index = parentTasks.findIndex(t => t.id === selectedTask.value.id)
  const temp = parentTasks[index]
  parentTasks[index] = parentTasks[index + 1]
  parentTasks[index + 1] = temp
  markTaskChanged(selectedTask.value)
}

const copyTask = () => {
  if (!selectedTask.value) return
  copiedTask.value = { ...selectedTask.value }
  ElMessage.info('任务已复制')
}

const pasteTask = async () => {
  if (!copiedTask.value) return
  try {
    await addWBSTask(plan.value.id, {
      name: copiedTask.value.name + '（副本）',
      parent_id: copiedTask.value.parent_id,
      start_date: copiedTask.value.start_date,
      end_date: copiedTask.value.end_date,
      duration: copiedTask.value.duration,
      progress: 0,
      is_milestone: copiedTask.value.is_milestone
    })
    ElMessage.success('任务已粘贴')
    await loadPlan()
  } catch (error) {
    ElMessage.error('粘贴失败')
  }
}

const deleteTask = async (task) => {
  if (!task && !selectedTask.value) return
  const taskToDelete = task || selectedTask.value

  try {
    await ElMessageBox.confirm(`确定要删除任务"${taskToDelete.name}"吗？`, '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteWBSTask(plan.value.id, taskToDelete.id)
    ElMessage.success('任务已删除')
    await loadPlan()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const editTask = (task) => {
  Object.assign(editingTask, task)
  showTaskDialog.value = true
}

const saveTask = async () => {
  try {
    await updateWBSTask(plan.value.id, editingTask.id, editingTask)
    ElMessage.success('任务已更新')
    showTaskDialog.value = false
    await loadPlan()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 里程碑操作
const addMilestone = async () => {
  if (!newMilestone.name || !newMilestone.plan_date) {
    ElMessage.warning('请填写必填项')
    return
  }

  try {
    await addMilestoneApi(plan.value.id, newMilestone)
    ElMessage.success('里程碑已添加')
    showAddMilestoneDialog.value = false
    Object.assign(newMilestone, { name: '', plan_date: '', task_id: null })
    await loadPlan()
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const completeMilestone = async (milestone) => {
  try {
    await updateMilestone(plan.value.id, milestone.id, { status: 'completed' })
    ElMessage.success('里程碑已完成')
    await loadPlan()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const removeMilestone = async (milestone) => {
  try {
    await ElMessageBox.confirm('确定要删除此里程碑吗？', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteMilestoneApi(plan.value.id, milestone.id)
    ElMessage.success('里程碑已删除')
    await loadPlan()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 工具方法
const getProgressColor = (progress) => {
  if (!progress || progress === 0) return '#909399'
  if (progress < 30) return '#F56C6C'
  if (progress < 70) return '#E6A23C'
  return '#67C23A'
}

// 键盘快捷键
const handleKeydown = (e) => {
  if (!isEditing.value) return

  if (e.ctrlKey || e.metaKey) {
    if (e.key === 'n') {
      e.preventDefault()
      addTask(null)
    } else if (e.shiftKey && e.key === 'N') {
      e.preventDefault()
      addChildTask()
    } else if (e.key === 'c') {
      e.preventDefault()
      copyTask()
    } else if (e.key === 'v') {
      e.preventDefault()
      pasteTask()
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault()
      upgradeTask()
    } else if (e.key === 'ArrowRight') {
      e.preventDefault()
      downgradeTask()
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      moveUpTask()
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      moveDownTask()
    }
  } else if (e.key === 'Delete') {
    e.preventDefault()
    deleteTask()
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (selectedTask.value) {
      editTask(selectedTask.value)
    }
  }
}

// 生命周期
onMounted(() => {
  loadPlan()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.planning-detail-page {
  padding: 24px;
  max-width: 1600px;
  margin: 0 auto;
}

.breadcrumb-nav {
  margin-bottom: 16px;
}

.page-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-right {
  display: flex;
  gap: 8px;
}

.plan-overview {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

.overview-card {
  height: fit-content;
}

.card-header {
  font-weight: 600;
}

.progress-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: #F5F7FA;
  border-radius: 8px;
}

.stat-item.success {
  background: #F6FFED;
}

.stat-item.primary {
  background: #E6F7FF;
}

.stat-item.warning {
  background: #FFF7E6;
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

.overall-progress {
  padding: 16px 0;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.progress-value {
  font-weight: 600;
  color: #1E5EB8;
}

.wbs-editor {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.wbs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #E8E8E8;
}

.wbs-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.wbs-toolbar {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  border-bottom: 1px solid #E8E8E8;
  background: #F5F7FA;
}

.wbs-tree-table {
  min-height: 400px;
}

.task-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.expand-icon {
  cursor: pointer;
  color: #8C8C8C;
}

.expand-icon.placeholder {
  cursor: default;
}

.milestone-icon {
  color: #FAAD14;
}

.task-checkbox {
  margin-right: 8px;
}

.task-name-input {
  flex: 1;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-cell .el-slider {
  flex: 1;
}

.progress-text {
  font-size: 12px;
  color: #595959;
  min-width: 40px;
}

@media screen and (max-width: 768px) {
  .planning-detail-page {
    padding: 16px;
  }

  .plan-overview {
    grid-template-columns: 1fr;
  }

  .progress-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .page-toolbar {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
