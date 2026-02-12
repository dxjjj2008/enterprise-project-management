<template>
  <div class="register-container">
    <div class="register-header">
      <div class="logo">
        <div class="logo-icon">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L13.09 8.26L20 9L13.09 9.74L16 16L12 12L8 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="currentColor"/>
            <path d="M12 18C14.21 18 16 16.21 16 14C16 11.79 14.21 10 12 10C9.79 10 8 11.79 8 14C8 16.21 9.79 18 12 18Z" fill="currentColor"/>
          </svg>
        </div>
        <h1 class="logo-title">企业项目管理系统</h1>
      </div>
      <h2 class="form-title">注册账号</h2>
    </div>

    <el-form :model="form" label-position="top" class="register-form">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" placeholder="请输入用户名" size="large" />
      </el-form-item>

      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" type="email" placeholder="请输入邮箱地址" size="large" />
      </el-form-item>

      <el-form-item label="密码" prop="password">
        <el-input v-model="form.password" type="password" placeholder="请输入密码" size="large" show-password />
      </el-form-item>

      <el-form-item label="确认密码" prop="passwordConfirm">
        <el-input v-model="form.passwordConfirm" type="password" placeholder="请再次输入密码" size="large" show-password />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" :loading="loading" @click="handleRegister" class="submit-btn" size="large">
          注册
        </el-button>
      </el-form-item>
    </el-form>

    <div class="auth-links">
      <el-link type="primary" @click="gotoLogin">已有账号？立即登录</el-link>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { http } from '@/api'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
  passwordConfirm: ''
})

const handleRegister = async () => {
  if (form.password !== form.passwordConfirm) {
    ElMessage.error('两次输入的密码不一致')
    return
  }

  if (form.password.length < 6) {
    ElMessage.error('密码长度至少6个字符')
    return
  }

  loading.value = true
  try {
    // 调用后端注册API (使用JSON请求体)
    await http.post('auth/register', {
      username: form.username,
      email: form.email,
      password: form.password
    })

    ElMessage.success('注册成功！请登录')
    router.push('/auth/login')
  } catch (error) {
    const msg = error.message || '注册失败，请重试'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}

const gotoLogin = () => {
  router.push('/auth/login')
}
</script>

<style scoped>
.register-container {
  padding: 32px 40px;
}

.register-header {
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

.register-form {
  margin-bottom: 20px;
}

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 500;
}

.auth-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  font-size: 14px;
}

@media (max-width: 480px) {
  .register-container {
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
