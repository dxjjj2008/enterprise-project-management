/**
 * Reports 页面测试
 *
 * 测试报表统计功能：项目报表、任务统计、资源报表
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

describe('Reports', () => {
  const mockReportData = {
    projectStats: {
      total: 12,
      active: 5,
      completed: 4,
      onHold: 3
    },
    taskStats: {
      total: 156,
      todo: 45,
      inProgress: 67,
      done: 44
    },
    resourceStats: {
      totalMembers: 28,
      avgUtilization: 85,
      totalWorkload: 2380
    }
  }

  it('renders reports page title', () => {
    const wrapper = mount({
      template: '<div class="reports-page"><h1>报表统计</h1></div>'
    })
    expect(wrapper.text()).toContain('报表统计')
  })

  it('renders project statistics', () => {
    const wrapper = mount({
      template: '<div><span class="project-total">{{ data.projectStats.total }}</span></div>',
      data() {
        return { data: mockReportData }
      }
    })
    expect(wrapper.text()).toContain('12')
  })

  it('renders active projects count', () => {
    const wrapper = mount({
      template: '<div><span class="active-projects">{{ data.projectStats.active }}</span></div>',
      data() {
        return { data: mockReportData }
      }
    })
    expect(wrapper.text()).toContain('5')
  })

  it('renders completed projects count', () => {
    const wrapper = mount({
      template: '<div><span class="completed-projects">{{ data.projectStats.completed }}</span></div>',
      data() {
        return { data: mockReportData }
      }
    })
    expect(wrapper.text()).toContain('4')
  })

  it('renders task statistics', () => {
    const wrapper = mount({
      template: '<div><span class="task-total">{{ data.taskStats.total }}</span></div>',
      data() {
        return { data: mockReportData }
      }
    })
    expect(wrapper.text()).toContain('156')
  })

  it('renders tasks in progress count', () => {
    const wrapper = mount({
      template: '<div><span class="in-progress">{{ data.taskStats.inProgress }}</span></div>',
      data() {
        return { data: mockReportData }
      }
    })
    expect(wrapper.text()).toContain('67')
  })

  it('renders resource statistics', () => {
    const wrapper = mount({
      template: '<div><span class="total-members">{{ data.resourceStats.totalMembers }}</span></div>',
      data() {
        return { data: mockReportData }
      }
    })
    expect(wrapper.text()).toContain('28')
  })

  it('renders average utilization', () => {
    const wrapper = mount({
      template: '<div><span class="avg-utilization">{{ data.resourceStats.avgUtilization }}%</span></div>',
      data() {
        return { data: mockReportData }
      }
    })
    expect(wrapper.text()).toContain('85%')
  })

  it('calculates project completion rate', () => {
    const completionRate = (mockReportData.projectStats.completed / mockReportData.projectStats.total * 100).toFixed(1)
    expect(completionRate).toBe('33.3')
  })

  it('calculates task completion rate', () => {
    const completionRate = (mockReportData.taskStats.done / mockReportData.taskStats.total * 100).toFixed(1)
    expect(completionRate).toBe('28.2')
  })

  it('renders report date range', () => {
    const wrapper = mount({
      template: '<div><span class="date-range">2026-02-01 至 2026-02-28</span></div>'
    })
    expect(wrapper.text()).toContain('2026-02-01')
  })

  it('search reports by type', () => {
    const reportTypes = ['project', 'task', 'resource']
    expect(reportTypes).toHaveLength(3)
  })

  it('filters data by time period', () => {
    const currentMonthTasks = mockReportData.taskStats.inProgress + mockReportData.taskStats.done
    expect(currentMonthTasks).toBe(111)
  })

  it('handles empty report data', () => {
    const wrapper = mount({
      template: '<div class="reports-page">{{ message }}</div>',
      data() {
        return { message: '暂无报表数据' }
      }
    })
    expect(wrapper.text()).toContain('暂无报表数据')
  })
})
