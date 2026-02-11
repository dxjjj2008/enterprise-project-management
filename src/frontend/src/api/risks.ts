// 风险管理 API 客户端
import { http } from '@/api/index'

// 获取风险列表
export const getRisks = async (projectId: number, params?: Record<string, any>) => {
  try {
    const response = await http.get(`projects/${projectId}/risks`, params)
    return response
  } catch (error) {
    console.error('获取风险列表失败:', error)
    throw error
  }
}

// 获取风险详情
export const getRiskDetail = async (projectId: number, riskId: number) => {
  try {
    const response = await http.get(`projects/${projectId}/risks/${riskId}`)
    return response
  } catch (error) {
    console.error('获取风险详情失败:', error)
    throw error
  }
}

// 创建风险
export const createRisk = async (projectId: number, data: {
  title: string
  description?: string
  level?: string
  probability?: number
  impact?: number
  category?: string
  source?: string
  mitigation?: string
  contingency_plan?: string
  owner_id?: number
  task_id?: number
  due_date?: string
}) => {
  try {
    const response = await http.post(`projects/${projectId}/risks`, data)
    return response
  } catch (error) {
    console.error('创建风险失败:', error)
    throw error
  }
}

// 更新风险
export const updateRisk = async (projectId: number, riskId: number, data: {
  title?: string
  description?: string
  level?: string
  status?: string
  probability?: number
  impact?: number
  category?: string
  source?: string
  mitigation?: string
  contingency_plan?: string
  owner_id?: number
  task_id?: number
  due_date?: string
  closed_date?: string
}) => {
  try {
    const response = await http.put(`projects/${projectId}/risks/${riskId}`, data)
    return response
  } catch (error) {
    console.error('更新风险失败:', error)
    throw error
  }
}

// 删除风险
export const deleteRisk = async (projectId: number, riskId: number) => {
  try {
    const response = await http.delete(`projects/${projectId}/risks/${riskId}`)
    return response
  } catch (error) {
    console.error('删除风险失败:', error)
    throw error
  }
}

// 添加风险应对记录
export const addRiskResponse = async (projectId: number, riskId: number, data: {
  action: string
  result?: string
}) => {
  try {
    const response = await http.post(`projects/${projectId}/risks/${riskId}/responses`, data)
    return response
  } catch (error) {
    console.error('添加应对记录失败:', error)
    throw error
  }
}

// 获取风险统计
export const getRiskStats = async (params?: { project_id?: number }) => {
  try {
    const response = await http.get('risks/stats', params)
    return response
  } catch (error) {
    console.error('获取风险统计失败:', error)
    throw error
  }
}
