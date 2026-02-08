<template>
  <el-drawer
    v-model="visible"
    :title="isNew ? '新建任务' : '任务详情'"
    size="560px"
    destroy-on-close
    @close="handleClose"
  >
    <div class="task-detail" v-if="task">
      <!-- 任务标题 -->
      <el-form-item label="任务标题">
        <el-input
          v-model="task.title"
          placeholder="请输入任务标题"
          :disabled="!isEditMode"
        />
      </el-form-item>

      <!-- 任务描述 -->
      <el-form-item label="任务描述">
        <el-input
          v-model="task.description"
          type="textarea"
          :rows="3"
          placeholder="请输入任务描述"
          :disabled="!isEditMode"
        />
      </el-form-item>

      <!-- 基本信息行 -->
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="状态">
            <el-select v-model="task.status" style="width: 100%" :disabled="!isEditMode">
              <el-option label="待办" value="todo" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="审核中" value="review" />
              <el-option label="已完成" value="done" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="优先级">
            <el-select v-model="task.priority" style="width: 100%" :disabled="!isEditMode">
              <el-option label="紧急" value="urgent">
                <el-tag type="danger" size="small">紧急</el-tag>
              </el-option>
              <el-option label="高" value="high">
                <el-tag type="warning" size="small">高</el-tag>
              </el-option>
              <el-option label="中" value="medium">
                <el-tag size="small">中</el-tag>
              </el-option>
              <el-option label="低" value="low">
                <el-tag type="info" size="small">低</el-tag>
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 日期和负责人 -->
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="开始日期">
            <el-date-picker
              v-model="task.startDate"
              type="date"
              placeholder="选择开始日期"
              style="width: 100%"
              :disabled="!isEditMode"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="截止日期">
            <el-date-picker
              v-model="task.dueDate"
              type="date"
              placeholder="选择截止日期"
              style="width: 100%"
              :disabled="!isEditMode"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="负责人">
        <el-select
          v-model="task.assigneeId"
          placeholder="选择负责人"
          style="width: 100%"
          :disabled="!isEditMode"
        >
          <el-option
            v-for="member in members"
            :key="member.id"
            :label="member.name"
            :value="member.id"
          >
            <el-avatar :size="20" style="margin-right: 8px">{{ member.name.charAt(0) }}</el-avatar>
            {{ member.name }}
          </el-option>
        </el-select>
      </el-form-item>

      <!-- 标签 -->
      <el-form-item label="标签">
        <div class="label-list">
          <el-tag
            v-for="(label, index) in task.labels"
            :key="index"
            size="small"
            closable
            @close="removeLabel(index)"
            :disabled="!isEditMode"
          >
            {{ label }}
          </el-tag>
          <el-input
            v-if="showLabelInput"
            v-model="newLabel"
            size="small"
            style="width: 80px"
            @keyup.enter="addLabel"
            @blur="addLabel"
            ref="labelInput"
          />
          <el-button
            v-else
            size="small"
            @click="showLabelInput = true"
            :disabled="!isEditMode"
          >
            + 添加
          </el-button>
        </div>
      </el-form-item>

      <!-- 预估工时 -->
      <el-form-item label="预估工时">
        <el-input-number
          v-model="task.estimatedHours"
          :min="0"
          :step="0.5"
          :precision="1"
          :disabled="!isEditMode"
        />
        <span style="margin-left: 8px; color: #8C8C8C">小时</span>
      </el-form-item>

      <!-- 子任务 -->
      <el-form-item label="子任务">
        <div class="subtask-list">
          <div
            v-for="(subtask, index) in task.subtasks"
            :key="index"
            class="subtask-item"
          >
            <el-checkbox
              v-model="subtask.done"
              :disabled="!isEditMode"
            />
            <el-input
              v-model="subtask.title"
              size="small"
              :disabled="!isEditMode"
            />
            <el-button
              v-if="isEditMode"
              size="small"
              type="danger"
              circle
              :icon="Delete"
              @click="removeSubtask(index)"
            />
          </div>
          <el-button
            v-if="isEditMode"
            size="small"
            @click="addSubtask"
            style="margin-top: 8px"
          >
            + 添加子任务
          </el-button>
        </div>
      </el-form-item>

      <!-- 进度 -->
      <el-form-item label="进度">
        <el-slider
          v-model="task.progress"
          :show-input="true"
          :disabled="!isEditMode"
        />
      </el-form-item>

      <!-- 评论 -->
      <el-form-item label="评论">
        <div class="comment-list">
          <div
            v-for="(comment, index) in task.comments"
            :key="index"
            class="comment-item"
          >
            <el-avatar :size="32">{{ comment.user.name.charAt(0) }}</el-avatar>
            <div class="comment-content">
              <div class="comment-header">
                <span class="comment-user">{{ comment.user.name }}</span>
                <span class="comment-time">{{ comment.time }}</span>
              </div>
              <p class="comment-text">{{ comment.content }}</p>
            </div>
          </div>
        </div>
        <div class="comment-input">
          <el-input
            v-model="newComment"
            type="textarea"
            :rows="2"
            placeholder="添加评论..."
          />
          <el-button type="primary" size="small" @click="addComment">发送</el-button>
        </div>
      </el-form-item>

      <!-- 操作按钮 -->
      <div class="drawer-footer">
        <el-button @click="toggleEdit">
          {{ isEditMode ? '取消编辑' : '编辑' }}
        </el-button>
        <el-button type="primary" @click="saveTask" v-if="isEditMode">
          保存
        </el-button>
        <el-button type="danger" @click="confirmDelete" v-if="!isNew">
          删除任务
        </el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({
  modelValue: Boolean,
  task: Object
})

const emit = defineEmits(['update:modelValue', 'update', 'delete', 'close'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const isNew = computed(() => !props.task || !props.task.id)

const isEditMode = ref(false)
const showLabelInput = ref(false)
const newLabel = ref('')
const newComment = ref('')
const labelInput = ref(null)

const members = ref([
  { id: 1, name: '张三' },
  { id: 2, name: '李四' },
  { id: 3, name: '王五' },
  { id: 4, name: '赵六' }
])

watch(visible, (val) => {
  if (val) {
    isEditMode.value = isNew.value
    showLabelInput.value = false
    newLabel.value = ''
    newComment.value = ''
  }
})

watch(showLabelInput, (val) => {
  if (val) {
    nextTick(() => {
      labelInput.value?.focus()
    })
  }
})

const addLabel = () => {
  if (newLabel.value.trim()) {
    props.task.labels = props.task.labels || []
    props.task.labels.push(newLabel.value.trim())
    newLabel.value = ''
    showLabelInput.value = false
  }
}

const removeLabel = (index) => {
  props.task.labels.splice(index, 1)
}

const addSubtask = () => {
  props.task.subtasks = props.task.subtasks || []
  props.task.subtasks.push({ id: Date.now(), title: '', done: false })
}

const removeSubtask = (index) => {
  props.task.subtasks.splice(index, 1)
}

const addComment = () => {
  if (!newComment.value.trim()) return
  
  props.task.comments = props.task.comments || []
  props.task.comments.push({
    user: { name: '张经理' },
    content: newComment.value.trim(),
    time: new Date().toLocaleString()
  })
  newComment.value = ''
}

const toggleEdit = () => {
  if (isEditMode.value && !isNew.value) {
    // 取消编辑，重新获取原始数据
    isEditMode.value = false
  } else {
    isEditMode.value = true
  }
}

const saveTask = () => {
  if (!props.task.title.trim()) {
    ElMessage.warning('请输入任务标题')
    return
  }
  emit('update', props.task)
  isEditMode.value = false
  ElMessage.success('保存成功')
}

const confirmDelete = async () => {
  try {
    await ElMessageBox.confirm('确定要删除此任务吗？此操作不可恢复。', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    emit('delete', props.task)
    visible.value = false
    ElMessage.success('删除成功')
  } catch {
    // 取消删除
  }
}

const handleClose = () => {
  emit('close')
}
</script>

<style scoped>
.task-detail {
  padding: 0 8px;
}

.label-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.subtask-list {
  width: 100%;
}

.subtask-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.subtask-item .el-input {
  flex: 1;
}

/* 评论样式 */
.comment-list {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 16px;
}

.comment-item {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
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
  margin: 0;
  font-size: 14px;
  color: #595959;
  line-height: 1.5;
}

.comment-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.comment-input .el-button {
  align-self: flex-end;
}

.drawer-footer {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #F0F0F0;
}
</style>
