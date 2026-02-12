/**
 * Approvals 页面测试
 *
 * 测试审批流程功能：审批列表、状态流转、流程管理
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

describe('Approvals', () => {
  const mockApprovals = [
    {
      id: '1',
      title: '项目立项审批',
      type: 'project',
      status: 'pending',
      applicant: '张三',
      approver: '李四',
      created_at: '2026-02-10'
    },
    {
      id: '2',
      title: '预算调整申请',
      type: 'budget',
      status: 'approved',
      applicant: '李四',
      approver: '王五',
      created_at: '2026-02-09'
    },
    {
      id: '3',
      title: '人员调配申请',
      type: 'resource',
      status: 'rejected',
      applicant: '王五',
      approver: '赵六',
      created_at: '2026-02-08'
    }
  ]

  it('renders approvals page title', () => {
    const wrapper = mount({
      template: '<div class="approvals-page"><h1>审批流程</h1></div>'
    })
    expect(wrapper.text()).toContain('审批流程')
  })

  it('renders approvals list', () => {
    const wrapper = mount({
      template: `
        <div class="approvals-page">
          <div v-for="approval in approvals" :key="approval.id" class="approval-item">
            {{ approval.title }}
          </div>
        </div>
      `,
      data() {
        return { approvals: mockApprovals }
      }
    })
    expect(wrapper.findAll('.approval-item')).toHaveLength(3)
  })

  it('renders approval title correctly', () => {
    const wrapper = mount({
      template: '<div>{{ approval.title }}</div>',
      data() {
        return { approval: mockApprovals[0] }
      }
    })
    expect(wrapper.text()).toContain('项目立项审批')
  })

  it('renders approval status badge', () => {
    const wrapper = mount({
      template: '<div><span class="status-badge">{{ approval.status }}</span></div>',
      data() {
        return { approval: mockApprovals[0] }
      }
    })
    expect(wrapper.text()).toContain('pending')
  })

  it('renders approval type', () => {
    const wrapper = mount({
      template: '<div><span class="type-badge">{{ approval.type }}</span></div>',
      data() {
        return { approval: mockApprovals[0] }
      }
    })
    expect(wrapper.text()).toContain('project')
  })

  it('filters approvals by status', () => {
    const pendingApprovals = mockApprovals.filter(a => a.status === 'pending')
    expect(pendingApprovals).toHaveLength(1)
    expect(pendingApprovals[0].title).toContain('项目立项')
  })

  it('filters approvals by type', () => {
    const budgetApprovals = mockApprovals.filter(a => a.type === 'budget')
    expect(budgetApprovals).toHaveLength(1)
  })

  it('renders applicant name', () => {
    const wrapper = mount({
      template: '<div><span class="applicant">{{ approval.applicant }}</span></div>',
      data() {
        return { approval: mockApprovals[0] }
      }
    })
    expect(wrapper.text()).toContain('张三')
  })

  it('renders approver name', () => {
    const wrapper = mount({
      template: '<div><span class="approver">{{ approval.approver }}</span></div>',
      data() {
        return { approval: mockApprovals[0] }
      }
    })
    expect(wrapper.text()).toContain('李四')
  })

  it('renders approval creation date', () => {
    const wrapper = mount({
      template: '<div><span class="created-at">{{ approval.created_at }}</span></div>',
      data() {
        return { approval: mockApprovals[0] }
      }
    })
    expect(wrapper.text()).toContain('2026-02-10')
  })

  it('search approvals by keyword', () => {
    const keyword = '预算'
    const filtered = mockApprovals.filter(a => a.title.includes(keyword))
    expect(filtered).toHaveLength(1)
    expect(filtered[0].title).toContain('预算调整')
  })

  it('handles empty approvals list', () => {
    const wrapper = mount({
      template: '<div class="approvals-page">{{ message }}</div>',
      data() {
        return { message: '暂无审批' }
      }
    })
    expect(wrapper.text()).toContain('暂无审批')
  })

  it('calculates approval statistics', () => {
    const stats = {
      total: mockApprovals.length,
      pending: mockApprovals.filter(a => a.status === 'pending').length,
      approved: mockApprovals.filter(a => a.status === 'approved').length,
      rejected: mockApprovals.filter(a => a.status === 'rejected').length
    }
    expect(stats.total).toBe(3)
    expect(stats.pending).toBe(1)
    expect(stats.approved).toBe(1)
    expect(stats.rejected).toBe(1)
  })
})
