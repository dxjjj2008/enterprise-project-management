import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useLoginMutation, useRegisterMutation, useGetCurrentUserQuery } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const userInfo = ref<any>(JSON.parse(localStorage.getItem('user_info') || '{}'))
  
  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => userInfo.value?.role || 'guest')
  
  const { login } = useLoginMutation()
  const { register } = useRegisterMutation()
  const { getCurrentUser } = useGetCurrentUserQuery()
  
  const loginAction = async (credentials: { username: string; password: string }) => {
    try {
      const result = await login(credentials).unwrap()
      token.value = result.access_token
      localStorage.setItem('auth_token', result.access_token)
      
      const user = await getCurrentUser().unwrap()
      userInfo.value = user
      localStorage.setItem('user_info', JSON.stringify(user))
      
      return result
    } catch (error) {
      throw error
    }
  }
  
  const registerAction = async (userData: { username: string; email: string; password: string }) => {
    try {
      const result = await register(userData).unwrap()
      const loginResult = await login({ username: userData.username, password: userData.password }).unwrap()
      token.value = loginResult.access_token
      localStorage.setItem('auth_token', loginResult.access_token)
      
      userInfo.value = result.user
      localStorage.setItem('user_info', JSON.stringify(result.user))
      
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
  
  const initAuth = () => {
    if (token.value && !userInfo.value?.email) {
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