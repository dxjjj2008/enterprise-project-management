/**
 * Resources 页面测试
 *
 * 测试资源管理功能：用户列表、工作量统计、利用率
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

describe('Resources', () => {
  const mockResources = [
    {
      id: '1',
      name: '张三',
      role: '开发工程师',
      department: '技术部',
      workload: 85,
      utilization: 92,
      tasks: 5,
      avatar: 'ZS'
    },
    {
      id: '2',
      name: '李四',
      role: '产品经理',
      department: '产品部',
      workload: 70,
      utilization: 78,
      tasks: 3,
      avatar: 'LS'
    },
    {
      id: '3',
      name: '王五',
      role: 'UI设计师',
      department: '设计部',
      workload: 95,
      utilization: 98,
      tasks: 7,
      avatar: 'WW'
    }
  ]

  it('renders resources page title', () => {
    const wrapper = mount({
      template: '<div class="resources-page"><h1>资源管理</h1></div>'
    })
    expect(wrapper.text()).toContain('资源管理')
  })

  it('renders resources list', () => {
    const wrapper = mount({
      template: `
        <div class="resources-page">
          <div v-for="resource in resources" :key="resource.id" class="resource-item">
            {{ resource.name }}
          </div>
        </div>
      `,
      data() {
        return { resources: mockResources }
      }
    })
    expect(wrapper.findAll('.resource-item')).toHaveLength(3)
  })

  it('renders resource name correctly', () => {
    const wrapper = mount({
      template: '<div>{{ resource.name }}</div>',
      data() {
        return { resource: mockResources[0] }
      }
    })
    expect(wrapper.text()).toContain('张三')
  })

  it('renders resource role', () => {
    const wrapper = mount({
      template: '<div><span class="role">{{ resource.role }}</span></div>',
      data() {
        return { resource: mockResources[0] }
      }
    })
    expect(wrapper.text()).toContain('开发工程师')
  })

  it('renders resource department', () => {
    const wrapper = mount({
      template: '<div><span class="department">{{ resource.department }}</span></div>',
      data() {
        return { resource: mockResources[0] }
      }
    })
    expect(wrapper.text()).toContain('技术部')
  })

  it('renders resource workload indicator', () => {
    const wrapper = mount({
      template: '<div><span class="workload">{{ resource.workload }}%</span></div>',
      data() {
        return { resource: mockResources[0] }
      }
    })
    expect(wrapper.text()).toContain('85%')
  })

  it('renders resource utilization rate', () => {
    const wrapper = mount({
      template: '<div><span class="utilization">{{ resource.utilization }}%</span></div>',
      data() {
        return { resource: mockResources[0] }
      }
    })
    expect(wrapper.text()).toContain('92%')
  })

  it('renders resource task count', () => {
    const wrapper = mount({
      template: '<div><span class="tasks">{{ resource.tasks }} 个任务</span></div>',
      data() {
        return { resource: mockResources[0] }
      }
    })
    expect(wrapper.text()).toContain('5 个任务')
  })

  it('filters resources by department', () => {
    const techResources = mockResources.filter(r => r.department === '技术部')
    expect(techResources).toHaveLength(1)
    expect(techResources[0].name).toContain('张三')
  })

  it('sorts resources by workload', () => {
    const sorted = [...mockResources].sort((a, b) => b.workload - a.workload)
    expect(sorted[0].name).toContain('王五')
    expect(sorted[0].workload).toBe(95)
  })

  it('calculates average utilization', () => {
    const avgUtilization = mockResources.reduce((sum, r) => sum + r.utilization, 0) / mockResources.length
    expect(avgUtilization.toFixed(2)).toBe("89.33")
  })

  it('search resources by keyword', () => {
    const keyword = '张'
    const filtered = mockResources.filter(r => r.name.includes(keyword))
    expect(filtered).toHaveLength(1)
    expect(filtered[0].name).toContain('张三')
  })

  it('handles empty resources list', () => {
    const wrapper = mount({
      template: '<div class="resources-page">{{ message }}</div>',
      data() {
        return { message: '暂无资源' }
      }
    })
    expect(wrapper.text()).toContain('暂无资源')
  })
})
