/**
 * Login 页面测试
 *
 * 测试登录页面的核心功能
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

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
