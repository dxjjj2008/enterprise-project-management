<template>
  <div class="settings-page">
    <div class="page-header">
      <h2 class="page-title">系统设置</h2>
      <p class="page-desc">管理您的账户和系统偏好</p>
    </div>

    <div class="settings-container">
      <!-- 用户信息卡片 -->
      <el-card class="settings-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><User /></el-icon>
            <span>个人信息</span>
          </div>
        </template>
        
        <el-form :model="userForm" label-position="top" class="settings-form">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="用户名">
                <el-input v-model="userForm.username" placeholder="请输入用户名" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="邮箱">
                <el-input v-model="userForm.email" placeholder="请输入邮箱" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="手机号">
                <el-input v-model="userForm.phone" placeholder="请输入手机号" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="角色">
                <el-select v-model="userForm.role" placeholder="请选择角色" disabled>
                  <el-option label="管理员" value="admin" />
                  <el-option label="项目经理" value="manager" />
                  <el-option label="普通用户" value="user" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item>
            <el-button type="primary" @click="saveUserInfo">保存信息</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 密码修改卡片 -->
      <el-card class="settings-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><Lock /></el-icon>
            <span>修改密码</span>
          </div>
        </template>
        
        <el-form :model="passwordForm" label-position="top" class="settings-form">
          <el-form-item label="当前密码">
            <el-input v-model="passwordForm.currentPassword" type="password" placeholder="请输入当前密码" show-password />
          </el-form-item>
          <el-form-item label="新密码">
            <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" show-password />
          </el-form-item>
          <el-form-item label="确认新密码">
            <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="changePassword">修改密码</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 通知设置卡片 -->
      <el-card class="settings-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><Bell /></el-icon>
            <span>通知设置</span>
          </div>
        </template>
        
        <div class="notification-settings">
          <div class="notification-item">
            <div class="notification-info">
              <span class="notification-title">项目更新通知</span>
              <span class="notification-desc">当项目状态发生变化时接收通知</span>
            </div>
            <el-switch v-model="notifications.projectUpdates" />
          </div>
          <div class="notification-item">
            <div class="notification-info">
              <span class="notification-title">任务分配通知</span>
              <span class="notification-desc">当有新任务分配给您时接收通知</span>
            </div>
            <el-switch v-model="notifications.taskAssignments" />
          </div>
          <div class="notification-item">
            <div class="notification-info">
              <span class="notification-title">截止日期提醒</span>
              <span class="notification-desc">任务截止日期前接收提醒</span>
            </div>
            <el-switch v-model="notifications.deadlineReminders" />
          </div>
          <div class="notification-item">
            <div class="notification-info">
              <span class="notification-title">审批通知</span>
              <span class="notification-desc">当有审批请求时接收通知</span>
            </div>
            <el-switch v-model="notifications.approvals" />
          </div>
          <div class="notification-item">
            <div class="notification-info">
              <span class="notification-title">系统公告</span>
              <span class="notification-desc">接收系统更新和维护公告</span>
            </div>
            <el-switch v-model="notifications.systemAnnouncements" />
          </div>
        </div>
      </el-card>

      <!-- 界面设置卡片 -->
      <el-card class="settings-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><Setting /></el-icon>
            <span>界面设置</span>
          </div>
        </template>
        
        <div class="ui-settings">
          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-title">主题颜色</span>
              <span class="setting-desc">选择界面主题颜色</span>
            </div>
            <el-radio-group v-model="uiSettings.theme">
              <el-radio-button label="light">浅色</el-radio-button>
              <el-radio-button label="dark">深色</el-radio-button>
              <el-radio-button label="system">跟随系统</el-radio-button>
            </el-radio-group>
          </div>
          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-title">语言</span>
              <span class="setting-desc">选择界面语言</span>
            </div>
            <el-select v-model="uiSettings.language" placeholder="请选择语言">
              <el-option label="简体中文" value="zh-CN" />
              <el-option label="English" value="en-US" />
            </el-select>
          </div>
          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-title">每页显示条数</span>
              <span class="setting-desc">列表页面每页显示的数据条数</span>
            </div>
            <el-select v-model="uiSettings.pageSize" placeholder="请选择">
              <el-option :value="10" label="10 条/页" />
              <el-option :value="20" label="20 条/页" />
              <el-option :value="50" label="50 条/页" />
            </el-select>
          </div>
          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-title">紧凑模式</span>
              <span class="setting-desc">减小列表和表格的间距</span>
            </div>
            <el-switch v-model="uiSettings.compactMode" />
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { User, Lock, Bell, Setting } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 用户信息表单
const userForm = reactive({
  username: '张三',
  email: 'zhangsan@example.com',
  phone: '13800138000',
  role: 'manager'
})

// 密码修改表单
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 通知设置
const notifications = reactive({
  projectUpdates: true,
  taskAssignments: true,
  deadlineReminders: true,
  approvals: true,
  systemAnnouncements: false
})

// 界面设置
const uiSettings = reactive({
  theme: 'light',
  language: 'zh-CN',
  pageSize: 20,
  compactMode: false
})

// 保存用户信息
const saveUserInfo = () => {
  ElMessage.success('个人信息保存成功')
}

// 修改密码
const changePassword = () => {
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  if (passwordForm.newPassword.length < 6) {
    ElMessage.error('密码长度不能小于6位')
    return
  }
  ElMessage.success('密码修改成功')
  passwordForm.currentPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
}
</script>

<style lang="scss" scoped>
.settings-page {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.page-header {
  margin-bottom: 24px;
  
  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px 0;
  }
  
  .page-desc {
    font-size: 14px;
    color: #909399;
    margin: 0;
  }
}

.settings-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 1000px;
}

.settings-card {
  :deep(.el-card__header) {
    padding: 16px 20px;
    border-bottom: 1px solid #ebeef5;
    background-color: #fafafa;
  }
  
  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    font-weight: 500;
    color: #303133;
    
    .el-icon {
      font-size: 20px;
      color: #409eff;
    }
  }
}

.settings-form {
  padding: 10px 0;
}

.notification-settings {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 10px 0;
}

.notification-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
  
  &:last-child {
    border-bottom: none;
  }
  
  .notification-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  
  .notification-title {
    font-size: 14px;
    font-weight: 500;
    color: #303133;
  }
  
  .notification-desc {
    font-size: 12px;
    color: #909399;
  }
}

.ui-settings {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 10px 0;
}

.setting-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
  
  &:last-child {
    border-bottom: none;
  }
  
  .setting-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  
  .setting-title {
    font-size: 14px;
    font-weight: 500;
    color: #303133;
  }
  
  .setting-desc {
    font-size: 12px;
    color: #909399;
  }
}
</style>
