// 问题跟踪 API 客户端
import { http } from '@/api/index'

// 获取问题列表
export const getIssues = async (projectId: number, params?: Record<string, any>) => {
  try {
    const response = await http.get(`projects/${projectId}/issues`, params)
    return response
  } catch (error) {
    console.error('获取问题列表失败:', error)
    throw error
  }
}

// 获取问题详情
export const getIssueDetail = async (projectId: number, issueId: number) => {
  try {
    const response = await http.get(`projects/${projectId}/issues/${issueId}`)
    return response
  } catch (error) {
    console.error('获取问题详情失败:', error)
    throw error
  }
}

// 创建问题
export const createIssue = async (projectId: number, data: {
  title: string
  description?: string
  issue_type?: string
  priority?: string
  severity?: string
  assignee_id?: number
  task_id?: number
  due_date?: string
  tags?: string[]
}) => {
  try {
    const response = await http.post(`projects/${projectId}/issues`, data)
    return response
  } catch (error) {
    console.error('创建问题失败:', error)
    throw error
  }
}

// 更新问题
export const updateIssue = async (projectId: number, issueId: number, data: {
  title?: string
  description?: string
  status?: string
  issue_type?: string
  priority?: string
  severity?: string
  assignee_id?: number
  task_id?: number
  due_date?: string
  resolved_at?: string
  closed_at?: string
  tags?: string[]
}) => {
  try {
    const response = await http.put(`projects/${projectId}/issues/${issueId}`, data)
    return response
  } catch (error) {
    console.error('更新问题失败:', error)
    throw error
  }
}

// 删除问题
export const deleteIssue = async (projectId: number, issueId: number) => {
  try {
    const response = await http.delete(`projects/${projectId}/issues/${issueId}`)
    return response
  } catch (error) {
    console.error('删除问题失败:', error)
    throw error
  }
}

// 添加问题评论
export const addIssueComment = async (projectId: number, issueId: number, data: {
  content: string
  parent_id?: number
}) => {
  try {
    const response = await http.post(`projects/${projectId}/issues/${issueId}/comments`, data)
    return response
  } catch (error) {
    console.error('添加评论失败:', error)
    throw error
  }
}

// 获取问题统计
export const getIssueStats = async (params?: { project_id?: number }) => {
  try {
    const response = await http.get('issues/stats', params)
    return response
  } catch (error) {
    console.error('获取问题统计失败:', error)
    throw error
  }
}
