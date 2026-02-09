<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">项目列表</h1>
      <el-button type="primary" @click="openCreateDialog">
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
      <el-table :data="filteredProjects" style="width: 100%" v-loading="loading" stripe highlight-current-row>
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
                    v-for="(member, idx) in row.members.slice(0, 3)"
                    :key="idx"
                    :size="24"
                    :src="member.avatar"
                    loading="lazy"
                  />
                </div>
              </template>
            </el-table-column>
        <el-table-column prop="endDate" label="截止日期" width="120" />
         <el-table-column label="操作" width="180" fixed="right">
           <template #default="{ row }">
             <el-button type="primary" link size="small" @click="goToDetail(row.id)">详情</el-button>
             <el-button type="success" link size="small" @click="editProject(row)">编辑</el-button>
             <el-button type="danger" link size="small" @click="handleDelete(row.id)">删除</el-button>
           </template>
         </el-table-column>
       </el-table>
     </div>
   </div>
 
   <!-- 新建/编辑项目弹窗 -->
   <el-dialog
     v-model="formVisible"
     :title="isEdit ? '编辑项目' : '新建项目'"
     width="560px"
     destroy-on-close
   >
     <el-form :model="projectForm" :rules="formRules" ref="formRef" label-width="80px">
       <el-form-item label="项目名称" prop="name">
         <el-input v-model="projectForm.name" placeholder="请输入项目名称" />
       </el-form-item>
       <el-form-item label="项目描述" prop="description">
         <el-input v-model="projectForm.description" type="textarea" :rows="3" placeholder="请输入项目描述" />
       </el-form-item>
       <el-form-item label="负责人" prop="ownerId">
         <el-select v-model="projectForm.ownerId" placeholder="选择负责人" style="width: 100%">
           <el-option label="张经理" value="1" />
           <el-option label="李开发" value="2" />
           <el-option label="王测试" value="3" />
         </el-select>
       </el-form-item>
       <el-form-item label="状态" prop="status">
         <el-select v-model="projectForm.status" placeholder="选择状态" style="width: 100%">
           <el-option label="规划中" value="planning" />
           <el-option label="进行中" value="active" />
           <el-option label="已完成" value="completed" />
           <el-option label="已归档" value="archived" />
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
 </template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Grid, List, MoreFilled } from '@element-plus/icons-vue'
import { getProjects, createProject, updateProject, deleteProject } from '@/api/projects'

const searchKeyword = ref('')
const statusFilter = ref('')
const viewMode = ref('card')
const loading = ref(false)

const projects = ref([])

// 表单相关
const formVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)

const projectForm = reactive({
  id: null,
  name: '',
  description: '',
  ownerId: '',
  status: 'planning'
})

const formRules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 100, message: '项目名称长度为 2-100 个字符', trigger: 'blur' }
  ]
}

// 加载项目数据
const loadProjects = async () => {
  loading.value = true
  try {
    const response = await getProjects(1, 20)
    projects.value = response.items || []
  } catch (error) {
    console.error('加载项目失败:', error)
  } finally {
    loading.value = false
  }
}

// 打开新建对话框
const openCreateDialog = () => {
  isEdit.value = false
  Object.assign(projectForm, {
    id: null,
    name: '',
    description: '',
    ownerId: '',
    status: 'planning'
  })
  formVisible.value = true
}

// 编辑项目
const editProject = (project) => {
  isEdit.value = true
  Object.assign(projectForm, {
    id: project.id,
    name: project.name,
    description: project.description || '',
    ownerId: project.ownerId || '',
    status: project.status || 'planning'
  })
  formVisible.value = true
}

// 提交表单
const submitForm = async () => {
  submitLoading.value = true
  try {
    if (isEdit.value) {
      await updateProject(projectForm.id, projectForm)
      ElMessage.success('项目更新成功')
    } else {
      await createProject(projectForm)
      ElMessage.success('项目创建成功')
    }
    formVisible.value = false
    loadProjects()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败，请重试')
  } finally {
    submitLoading.value = false
  }
}

// 删除项目
const handleDelete = async (id) => {
  try {
    await deleteProject(id)
    ElMessage.success('项目删除成功')
    loadProjects()
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败，请重试')
  }
}

// 跳转到详情页
const goToDetail = (id) => {
  window.location.href = `/projects/${id}`
}

onMounted(() => {
  loadProjects()
})
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
  flex-wrap: wrap;
}

.dialog-form {
  padding: 20px 0;
}

/* ========== 响应式布局 ========== */

/* 平板端 (768px - 1024px) */
@media screen and (min-width: 768px) and (max-width: 1024px) {
  .filter-section {
    gap: 12px;
  }
  
  .project-card {
    padding: 16px;
  }
}

/* 移动端 (< 768px) */
@media screen and (max-width: 767px) {
  .filter-section {
    gap: 8px;
    margin-bottom: 16px;
  }
  
  .filter-section .el-select {
    width: 100px;
  }
  
  .el-table {
    font-size: 13px;
  }
  
  .pagination-container {
    justify-content: center;
    display: flex;
  }
}

/* 小屏移动端 (< 480px) */
@media screen and (max-width: 479px) {
  .page-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .filter-section {
    flex-direction: column;
  }
  
  .filter-section .el-select {
    width: 100%;
  }
}
</style>
