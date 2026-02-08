<template>
  <div class="login-page">
    <div class="login-header">
      <div class="logo">
        <el-icon :size="48" color="#1E5EB8"><Folder /></el-icon>
      </div>
      <h1>企业项目管理系统</h1>
      <p class="subtitle">登录您的账户</p>
    </div>
    
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      @submit.prevent="handleLogin"
    >
      <el-form-item label="邮箱" prop="email">
        <el-input
          v-model="form.email"
          type="email"
          placeholder="请输入邮箱"
          size="large"
          prefix-icon="Message"
        />
      </el-form-item>
      
      <el-form-item label="密码" prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          size="large"
          prefix-icon="Lock"
          show-password
        />
      </el-form-item>
      
      <el-form-item>
        <div class="form-options">
          <el-checkbox v-model="form.remember">记住我</el-checkbox>
          <el-link type="primary">忘记密码？</el-link>
        </div>
      </el-form-item>
      
      <el-form-item>
        <el-button
          type="primary"
          native-type="submit"
          :loading="loading"
          size="large"
          class="login-btn"
        >
          登录
        </el-button>
      </el-form-item>
    </el-form>
    
    <div class="login-footer">
      <span>还没有账户？</span>
      <router-link to="/auth/register">立即注册</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Message, Lock, Folder } from '@element-plus/icons-vue'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  email: '',
  password: '',
  remember: false
})

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      // TODO: 调用登录 API
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      ElMessage.success('登录成功')
      router.push('/')
    } catch (error) {
      ElMessage.error(error.message || '登录失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  margin-bottom: 16px;
}

.login-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 14px;
  color: #8C8C8C;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.login-btn {
  width: 100%;
}

.login-footer {
  text-align: center;
  font-size: 14px;
  color: #595959;
}

.login-footer a {
  margin-left: 4px;
}
</style>
