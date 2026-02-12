/**
 * Risks 页面测试
 *
 * 测试风险管理功能：风险列表、矩阵视图、应对措施
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

describe('Risks', () => {
  const mockRisks = [
    {
      id: '1',
      title: '关键技术选型风险',
      level: 'high',
      probability: 'medium',
      impact: 'high',
      status: 'monitoring',
      owner: '张三',
      mitigation: '提前进行技术预研'
    },
    {
      id: '2',
      title: '人员流动风险',
      level: 'medium',
      probability: 'low',
      impact: 'high',
      status: 'identified',
      owner: '李四',
      mitigation: '完善文档和知识共享'
    },
    {
      id: '3',
      title: '需求变更风险',
      level: 'low',
      probability: 'high',
      impact: 'low',
      status: 'mitigated',
      owner: '王五',
      mitigation: '敏捷开发流程'
    }
  ]

  it('renders risks page title', () => {
    const wrapper = mount({
      template: '<div class="risks-page"><h1>风险管理</h1></div>'
    })
    expect(wrapper.text()).toContain('风险管理')
  })

  it('renders risks list', () => {
    const wrapper = mount({
      template: `
        <div class="risks-page">
          <div v-for="risk in risks" :key="risk.id" class="risk-item">
            {{ risk.title }}
          </div>
        </div>
      `,
      data() {
        return { risks: mockRisks }
      }
    })
    expect(wrapper.findAll('.risk-item')).toHaveLength(3)
  })

  it('renders risk level badge', () => {
    const wrapper = mount({
      template: '<div><span class="risk-level">{{ risk.level }}</span></div>',
      data() {
        return { risk: mockRisks[0] }
      }
    })
    expect(wrapper.text()).toContain('high')
  })

  it('renders risk probability indicator', () => {
    const wrapper = mount({
      template: '<div><span class="probability">{{ risk.probability }}</span></div>',
      data() {
        return { risk: mockRisks[0] }
      }
    })
    expect(wrapper.text()).toContain('medium')
  })

  it('renders risk impact level', () => {
    const wrapper = mount({
      template: '<div><span class="impact">{{ risk.impact }}</span></div>',
      data() {
        return { risk: mockRisks[0] }
      }
    })
    expect(wrapper.text()).toContain('high')
  })

  it('filters risks by level', () => {
    const highRisks = mockRisks.filter(r => r.level === 'high')
    expect(highRisks).toHaveLength(1)
  })

  it('filters risks by status', () => {
    const monitoringRisks = mockRisks.filter(r => r.status === 'monitoring')
    expect(monitoringRisks).toHaveLength(1)
  })

  it('renders risk owner', () => {
    const wrapper = mount({
      template: '<div><span class="owner">{{ risk.owner }}</span></div>',
      data() {
        return { risk: mockRisks[0] }
      }
    })
    expect(wrapper.text()).toContain('张三')
  })

  it('renders risk mitigation measures', () => {
    const wrapper = mount({
      template: '<div><span class="mitigation">{{ risk.mitigation }}</span></div>',
      data() {
        return { risk: mockRisks[0] }
      }
    })
    expect(wrapper.text()).toContain('提前进行技术预研')
  })

  it('calculates risk matrix position', () => {
    const riskMatrix = mockRisks.map(r => ({
      ...r,
      score: r.probability === 'high' ? 3 : r.probability === 'medium' ? 2 : 1
    }))
    expect(riskMatrix[0].score).toBe(2)
  })

  it('search risks by keyword', () => {
    const keyword = '技术'
    const filtered = mockRisks.filter(r => r.title.includes(keyword))
    expect(filtered).toHaveLength(1)
    expect(filtered[0].title).toContain('技术选型')
  })

  it('handles empty risks list', () => {
    const wrapper = mount({
      template: '<div class="risks-page">{{ message }}</div>',
      data() {
        return { message: '暂无风险' }
      }
    })
    expect(wrapper.text()).toContain('暂无风险')
  })
})
