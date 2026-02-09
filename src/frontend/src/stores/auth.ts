// 认证状态管理
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useLoginMutation, useRegisterMutation, useGetCurrentUserQuery } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const userInfo = ref<any>(JSON.parse(localStorage.getItem('user_info') || '{}'))
  
  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => userInfo.value?.role || 'guest')
  
  // API hooks
  const { login } = useLoginMutation()
  const { register } = useRegisterMutation()
  const { getCurrentUser } = useGetCurrentUserQuery()
  
  // 动作
  const loginAction = async (credentials: { email: string; password: string }) => {
    try {
      const result = await login(credentials).unwrap()
      token.value = result.data.access_token
      localStorage.setItem('auth_token', result.data.access_token)
      
      // 获取用户信息
      const user = await getCurrentUser().unwrap()
      userInfo.value = user.data
      localStorage.setItem('user_info', JSON.stringify(user.data))
      
      return result
    } catch (error) {
      throw error
    }
  }
  
  const registerAction = async (userData: { username: string; email: string; password: string }) => {
    try {
      const result = await register(userData).unwrap()
      token.value = result.data.access_token
      localStorage.setItem('auth_token', result.data.access_token)
      
      // 获取用户信息
      const user = await getCurrentUser().unwrap()
      userInfo.value = user.data
      localStorage.setItem('user_info', JSON.stringify(user.data))
      
      return result
    } catch (error) {
      throw error
    }
  }
  
  const logout = () => {
    token.value = null
    userInfo.value = {}
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_info')
  }
  
  // 初始化
  const initAuth = () => {
    if (token.value && !userInfo.value?.email) {
      // 尝试获取用户信息
      getCurrentUser()
    }
  }
  
  return {
    token,
    userInfo,
    isAuthenticated,
    userRole,
    loginAction,
    registerAction,
    logout,
    initAuth
  }
})