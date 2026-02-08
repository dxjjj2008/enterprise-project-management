<template>
  <div class="auth-page">
    <div class="auth-container">
      <h1>用户注册</h1>
      <p>创建您的账户</p>
      
      <el-form :model="form" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="邮箱">
          <el-input v-model="form.email" type="email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        
        <el-form-item label="确认密码">
          <el-input v-model="form.passwordConfirm" type="password" placeholder="请再次输入密码" show-password />
        </el-form-item>
        
        <el-button type="primary" size="large" style="width: 100%">注册</el-button>
      </el-form>
      
      <div class="auth-footer">
        <span>已有账户？</span>
        <router-link to="/auth/login">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

const form = reactive({
  username: '',
  email: '',
  password: '',
  passwordConfirm: ''
})
</script>

<style scoped>
.auth-page {
  text-align: center;
}
.auth-container h1 {
  margin-bottom: 8px;
}
.auth-container p {
  color: #8C8C8C;
  margin-bottom: 32px;
}
.auth-footer {
  margin-top: 24px;
  font-size: 14px;
  color: #595959;
}
</style>
