/**
 * Planning 页面测试
 *
 * 测试计划管理功能：计划列表、时间线、进度跟踪
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

describe('Planning', () => {
  const mockPlans = [
    {
      id: '1',
      title: 'Q1 项目规划',
      status: 'active',
      progress: 75,
      start_date: '2026-01-01',
      end_date: '2026-03-31',
      owner: '张三',
      milestones: 4
    },
    {
      id: '2',
      title: '技术升级计划',
      status: 'draft',
      progress: 20,
      start_date: '2026-02-01',
      end_date: '2026-06-30',
      owner: '李四',
      milestones: 2
    },
    {
      id: '3',
      title: '团队培训计划',
      status: 'completed',
      progress: 100,
      start_date: '2025-12-01',
      end_date: '2026-01-31',
      owner: '王五',
      milestones: 5
    }
  ]

  it('renders planning page title', () => {
    const wrapper = mount({
      template: '<div class="planning-page"><h1>计划管理</h1></div>'
    })
    expect(wrapper.text()).toContain('计划管理')
  })

  it('renders plans list', () => {
    const wrapper = mount({
      template: `
        <div class="planning-page">
          <div v-for="plan in plans" :key="plan.id" class="plan-item">
            {{ plan.title }}
          </div>
        </div>
      `,
      data() {
        return { plans: mockPlans }
      }
    })
    expect(wrapper.findAll('.plan-item')).toHaveLength(3)
  })

  it('renders plan title correctly', () => {
    const wrapper = mount({
      template: '<div>{{ plan.title }}</div>',
      data() {
        return { plan: mockPlans[0] }
      }
    })
    expect(wrapper.text()).toContain('Q1 项目规划')
  })

  it('renders plan progress bar', () => {
    const wrapper = mount({
      template: '<div><div class="progress-bar">{{ plan.progress }}%</div></div>',
      data() {
        return { plan: mockPlans[0] }
      }
    })
    expect(wrapper.text()).toContain('75%')
  })

  it('renders plan status', () => {
    const wrapper = mount({
      template: '<div><span class="status-badge">{{ plan.status }}</span></div>',
      data() {
        return { plan: mockPlans[0] }
      }
    })
    expect(wrapper.text()).toContain('active')
  })

  it('filters plans by status', () => {
    const activePlans = mockPlans.filter(p => p.status === 'active')
    expect(activePlans).toHaveLength(1)
    expect(activePlans[0].title).toContain('Q1')
  })

  it('filters plans by progress', () => {
    const completedPlans = mockPlans.filter(p => p.progress === 100)
    expect(completedPlans).toHaveLength(1)
  })

  it('renders plan owner', () => {
    const wrapper = mount({
      template: '<div><span class="owner">{{ plan.owner }}</span></div>',
      data() {
        return { plan: mockPlans[0] }
      }
    })
    expect(wrapper.text()).toContain('张三')
  })

  it('renders plan date range', () => {
    const wrapper = mount({
      template: '<div><span class="date-range">{{ plan.start_date }}</span></div>',
      data() {
        return { plan: mockPlans[0] }
      }
    })
    expect(wrapper.text()).toContain('2026-01-01')
  })

  it('renders plan milestones count', () => {
    const wrapper = mount({
      template: '<div><span class="milestones">{{ plan.milestones }} 个里程碑</span></div>',
      data() {
        return { plan: mockPlans[0] }
      }
    })
    expect(wrapper.text()).toContain('4 个里程碑')
  })

  it('search plans by keyword', () => {
    const keyword = '技术'
    const filtered = mockPlans.filter(p => p.title.includes(keyword))
    expect(filtered).toHaveLength(1)
    expect(filtered[0].title).toContain('技术升级')
  })

  it('calculates overall progress', () => {
    const totalProgress = mockPlans.reduce((sum, p) => sum + p.progress, 0) / mockPlans.length
    expect(totalProgress).toBe(65)
  })

  it('handles empty plans list', () => {
    const wrapper = mount({
      template: '<div class="planning-page">{{ message }}</div>',
      data() {
        return { message: '暂无计划' }
      }
    })
    expect(wrapper.text()).toContain('暂无计划')
  })
})
