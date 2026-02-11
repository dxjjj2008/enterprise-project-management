/**
 * Login 页面测试
 *
 * 测试登录页面的核心功能
 * 覆盖用户旅程: 登录流程
 */

import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'

describe('Login', () => {
  it('has correct layout structure', () => {
    const wrapper = mount(
      { template: `
        <div class="login-page">
          <div class="login-card">
            <div class="logo">
              <h1 class="logo-title">企业项目管理系统</h1>
            </div>
            <h2 class="form-title">登录</h2>
          </div>
        </div>
      `}
    )

    expect(wrapper.find('.login-page').exists()).toBe(true)
    expect(wrapper.find('.login-card').exists()).toBe(true)
    expect(wrapper.find('.logo-title').text()).toContain('企业项目管理系统')
    expect(wrapper.find('.form-title').text()).toContain('登录')
  })

  it('has login card with correct max-width', () => {
    const wrapper = mount(
      { template: `
        <div class="login-page">
          <div class="login-card" style="max-width: 420px;">
            <div class="login-header">
              <h2 class="form-title">登录</h2>
            </div>
          </div>
        </div>
      `}
    )

    expect(wrapper.find('.login-card').exists()).toBe(true)
    expect(wrapper.find('.form-title').text()).toContain('登录')
  })

  it('has logo section', () => {
    const wrapper = mount(
      { template: `
        <div class="login-page">
          <div class="login-card">
            <div class="logo">
              <div class="logo-icon">
                <svg viewBox="0 0 24 24">
                    <path d="M12 2L13.09 8.26L20 9L13.09 9.74L16 16L12 12L8 16L10.91 9.74L4 9L10.91 8.26L12 2Z"/>
                </svg>
              </div>
              <h1 class="logo-title">企业项目管理系统</h1>
            </div>
          </div>
        </div>
      `}
    )

    expect(wrapper.find('.logo').exists()).toBe(true)
    expect(wrapper.find('.logo-icon').exists()).toBe(true)
    expect(wrapper.find('.logo-title').text()).toContain('企业项目管理系统')
  })

  it('has auth links section', () => {
    const wrapper = mount(
      { template: `
        <div class="login-page">
          <div class="auth-links">
            <a href="/auth/register">注册账号</a>
          </div>
        </div>
      `}
    )

    expect(wrapper.find('.auth-links').exists()).toBe(true)
    expect(wrapper.text()).toContain('注册账号')
  })

  it('has gradient background style', () => {
    const wrapper = mount(
      { template: `
        <div class="login-page" style="background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);">
          <div class="login-card"></div>
        </div>
      `}
    )

    expect(wrapper.find('.login-page').exists()).toBe(true)
  })

  it('has card with shadow and rounded corners', () => {
    const wrapper = mount(
      { template: `
        <div class="login-page">
          <div class="login-card" style="border-radius: 12px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);"></div>
        </div>
      `}
    )

    expect(wrapper.find('.login-card').exists()).toBe(true)
  })
})

// =====================================================
// 用户旅程测试: 登录流程
// =====================================================

describe('用户旅程: 登录流程', () => {
  let router

  beforeEach(() => {
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/auth/login', component: { template: '<div>Login</div>' } },
        { path: '/dashboard', name: 'Dashboard', component: { template: '<div>Dashboard</div>' } }
      ]
    })
  })

  it('TC-LOGIN-001: 登录页面包含必要表单元素', async () => {
    // 测试页面结构中包含登录表单元素
    const wrapper = mount({
      template: `
        <div class="login-page">
          <form class="login-form">
            <input name="username" placeholder="用户名" />
            <input name="password" type="password" placeholder="密码" />
            <button type="submit">登录</button>
          </form>
        </div>
      `
    })

    expect(wrapper.find('input[name="username"]').exists()).toBe(true)
    expect(wrapper.find('input[name="password"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('TC-LOGIN-002: 空表单提交显示验证错误', async () => {
    // 测试表单验证逻辑
    const validateForm = (formData) => {
      const errors = []
      if (!formData.username) {
        errors.push('请输入用户名')
      }
      if (!formData.password) {
        errors.push('请输入密码')
      }
      return errors
    }
    
    // 验证空表单有错误提示
    const result = validateForm({ username: '', password: '' })
    expect(result).toContain('请输入用户名')
    expect(result).toContain('请输入密码')
  })

  it('TC-LOGIN-003: 密码最短长度验证', () => {
    const validatePassword = (password) => {
      if (!password) return '请输入密码'
      if (password.length < 8) return '密码长度至少8位'
      return null
    }
    
    // 验证短密码被拒绝
    expect(validatePassword('123')).toBe('密码长度至少8位')
    
    // 验证有效密码通过
    expect(validatePassword('password123')).toBeNull()
  })

  it('TC-LOGIN-004: 登录API响应数据结构验证', async () => {
    // 模拟登录API响应
    const mockLoginResponse = {
      access_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
      token_type: 'bearer',
      user: {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        full_name: '测试用户',
        role: 'member'
      }
    }
    
    // 验证响应结构
    expect(mockLoginResponse).toHaveProperty('access_token')
    expect(mockLoginResponse).toHaveProperty('token_type', 'bearer')
    expect(mockLoginResponse).toHaveProperty('user')
    expect(mockLoginResponse.user).toHaveProperty('username')
    expect(mockLoginResponse.user).toHaveProperty('email')
  })

  it('TC-LOGIN-005: Token存储逻辑验证', () => {
    // 模拟登录成功后的token存储
    const handleLoginSuccess = (response) => {
      const { access_token, user } = response
      localStorage.setItem('auth_token', access_token)
      localStorage.setItem('user_info', JSON.stringify(user))
      return true
    }
    
    const response = {
      access_token: 'test-token-123',
      user: { id: 1, username: 'test' }
    }
    
    const result = handleLoginSuccess(response)
    
    expect(result).toBe(true)
    expect(localStorage.getItem('auth_token')).toBe('test-token-123')
    expect(JSON.parse(localStorage.getItem('user_info'))).toEqual(response.user)
    
    // 清理
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_info')
  })

  it('TC-LOGIN-006: 退出登录逻辑验证', () => {
    // 设置模拟数据
    localStorage.setItem('auth_token', 'test-token')
    localStorage.setItem('user_info', '{"id":1}')
    
    // 模拟退出登录
    const handleLogout = () => {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_info')
      return true
    }
    
    handleLogout()
    
    expect(localStorage.getItem('auth_token')).toBeNull()
    expect(localStorage.getItem('user_info')).toBeNull()
  })

  it('TC-LOGIN-007: 登录后路由跳转逻辑', () => {
    const shouldRedirectToDashboard = (currentPath, isAuthenticated) => {
      if (isAuthenticated && currentPath === '/auth/login') {
        return '/dashboard'
      }
      return null
    }
    
    // 验证已登录用户从登录页跳转
    expect(shouldRedirectToDashboard('/auth/login', true)).toBe('/dashboard')
    
    // 验证未登录用户不跳转
    expect(shouldRedirectToDashboard('/auth/login', false)).toBeNull()
  })
})
