<template>
  <div class="login-container">
    <div class="login-header">
      <div class="logo">
        <div class="logo-icon">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L13.09 8.26L20 9L13.09 9.74L16 16L12 12L8 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="currentColor"/>
            <path d="M12 18C14.21 18 16 16.21 16 14C16 11.79 14.21 10 12 10C9.79 10 8 11.79 8 14C8 16.21 9.79 18 12 18Z" fill="currentColor"/>
          </svg>
        </div>
        <h1 class="logo-title">企业项目管理系统</h1>
      </div>
      <h2 class="form-title">登录</h2>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      class="login-form"
    >
      <el-form-item label="用户名" prop="username">
        <el-input
          v-model="form.username"
          placeholder="请输入用户名"
          size="large"
          prefix-icon="User"
          clearable
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
          @keyup.enter="handleLogin"
        />
      </el-form-item>

      <el-form-item>
        <div class="form-options">
          <el-checkbox v-model="form.remember">记住我</el-checkbox>
        </div>
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          size="large"
          class="login-btn"
          :loading="loading"
          @click="handleLogin"
        >
          {{ loading ? '登录中...' : '登录' }}
        </el-button>
      </el-form-item>
    </el-form>

    <div class="auth-links">
      <el-link type="primary" @click="gotoRegister">注册账号</el-link>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { login } from '@/api'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  remember: false
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    // 调用后端OAuth2登录API (form-data格式)
    const response = await login(form.username, form.password)

    // 保存认证信息
    const { access_token, user } = response
    localStorage.setItem('auth_token', access_token)
    localStorage.setItem('user_info', JSON.stringify(user))

    ElMessage.success('登录成功！')
    router.push('/')
  } catch (error) {
    const msg = error.message || '登录失败，请检查用户名和密码'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}

const gotoRegister = () => {
  router.push('/auth/register')
}
</script>

<style scoped>
.login-container {
  padding: 32px 40px;
}

.login-header {
  text-align: center;
  margin-bottom: 28px;
}

.logo {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.logo-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: linear-gradient(135deg, #1E5EB8 0%, #4096FF 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.logo-title {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  margin: 0;
  line-height: 1.4;
}

.form-title {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

.login-form {
  margin-bottom: 20px;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 500;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.auth-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  font-size: 14px;
}

/* 响应式适配 */
@media (max-width: 480px) {
  .login-container {
    padding: 24px 20px;
  }

  .logo-icon {
    width: 48px;
    height: 48px;
  }

  .logo-title {
    font-size: 16px;
  }

  .form-title {
    font-size: 16px;
  }
}
</style>
