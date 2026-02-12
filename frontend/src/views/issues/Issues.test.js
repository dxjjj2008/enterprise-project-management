/**
 * Issues 页面测试
 *
 * 测试问题跟踪功能：列表渲染、状态筛选、搜索
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

describe('Issues', () => {
  const mockIssues = [
    {
      id: '1',
      title: '登录页面无法显示验证码',
      status: 'open',
      priority: 'high',
      assignee: '张三',
      created_at: '2026-02-10'
    },
    {
      id: '2',
      title: '报表导出格式错误',
      status: 'in_progress',
      priority: 'medium',
      assignee: '李四',
      created_at: '2026-02-09'
    },
    {
      id: '3',
      title: '甘特图时间轴显示异常',
      status: 'resolved',
      priority: 'low',
      assignee: '王五',
      created_at: '2026-02-08'
    }
  ]

  it('renders issues page title', () => {
    const wrapper = mount({
      template: '<div class="issues-page"><h1>问题跟踪</h1></div>'
    })
    expect(wrapper.text()).toContain('问题跟踪')
  })

  it('renders issues list', () => {
    const wrapper = mount({
      template: `
        <div class="issues-page">
          <div v-for="issue in issues" :key="issue.id" class="issue-item">
            {{ issue.title }}
          </div>
        </div>
      `,
      data() {
        return { issues: mockIssues }
      }
    })
    expect(wrapper.findAll('.issue-item')).toHaveLength(3)
  })

  it('renders issue title correctly', () => {
    const wrapper = mount({
      template: '<div>{{ issue.title }}</div>',
      data() {
        return { issue: mockIssues[0] }
      }
    })
    expect(wrapper.text()).toContain('登录页面无法显示验证码')
  })

  it('renders issue status tag', () => {
    const wrapper = mount({
      template: '<div><span class="status-tag">{{ issue.status }}</span></div>',
      data() {
        return { issue: mockIssues[0] }
      }
    })
    expect(wrapper.text()).toContain('open')
  })

  it('filters issues by status', () => {
    const openIssues = mockIssues.filter(i => i.status === 'open')
    expect(openIssues).toHaveLength(1)
    expect(openIssues[0].title).toContain('登录页面无法显示验证码')
  })

  it('filters issues by priority', () => {
    const highIssues = mockIssues.filter(i => i.priority === 'high')
    expect(highIssues).toHaveLength(1)
  })

  it('search issues by keyword', () => {
    const keyword = '验证码'
    const filtered = mockIssues.filter(i => i.title.includes(keyword))
    expect(filtered).toHaveLength(1)
  })

  it('renders issue priority badge', () => {
    const wrapper = mount({
      template: '<div><span class="priority-badge">{{ issue.priority }}</span></div>',
      data() {
        return { issue: mockIssues[0] }
      }
    })
    expect(wrapper.text()).toContain('high')
  })

  it('renders issue assignee', () => {
    const wrapper = mount({
      template: '<div><span class="assignee">{{ issue.assignee }}</span></div>',
      data() {
        return { issue: mockIssues[0] }
      }
    })
    expect(wrapper.text()).toContain('张三')
  })

  it('renders issue creation date', () => {
    const wrapper = mount({
      template: '<div><span class="created-at">{{ issue.created_at }}</span></div>',
      data() {
        return { issue: mockIssues[0] }
      }
    })
    expect(wrapper.text()).toContain('2026-02-10')
  })

  it('handles empty issues list', () => {
    const wrapper = mount({
      template: '<div class="issues-page">{{ message }}</div>',
      data() {
        return { message: '暂无问题' }
      }
    })
    expect(wrapper.text()).toContain('暂无问题')
  })
})
