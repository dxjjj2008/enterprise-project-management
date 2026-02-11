// 任务管理 API 客户端
import { http } from '@/api'

export interface Task {
  id: number
  project_id: number
  parent_id: number | null
  title: string
  description: string | null
  status: string
  priority: string
  assignee_id: number | null
  created_by_id: number
  start_date: string | null
  due_date: string | null
  completed_at: string | null
  estimated_hours: number | null
  progress: number
  created_at: string
  updated_at: string
}

export interface TaskResponse {
  task: Task
  subtasks: Task[]
  comments: Comment[]
  labels: Label[]
}

export interface Comment {
  id: number
  task_id: number
  author_id: number
  content: string
  created_at: string
}

export interface Label {
  id: number
  name: string
  color: string
}

// 获取任务列表
export const getTasks = async (projectId: number, params?: { status?: string; priority?: string; assignee_id?: number }) => {
  try {
    const response = await http.get(`projects/${projectId}/tasks`, params)
    return response
  } catch (error) {
    console.error('获取任务列表失败:', error)
    throw error
  }
}

// 创建任务
export const createTask = async (projectId: number, taskData: {
  title: string
  description?: string
  parent_id?: number
  priority?: string
  assignee_id?: number
  start_date?: string
  due_date?: string
  estimated_hours?: number
}) => {
  try {
    const response = await http.post(`projects/${projectId}/tasks`, taskData)
    return response
  } catch (error) {
    console.error('创建任务失败:', error)
    throw error
  }
}

// 获取任务详情
export const getTaskDetail = async (projectId: number, taskId: number) => {
  try {
    const response = await http.get<TaskResponse>(`projects/${projectId}/tasks/${taskId}`)
    return response
  } catch (error) {
    console.error(`获取任务 ${taskId} 详情失败:`, error)
    throw error
  }
}

// 更新任务
export const updateTask = async (projectId: number, taskId: number, taskData: Partial<{
  title: string
  description: string
  status: string
  priority: string
  assignee_id: number
  start_date: string
  due_date: string
  estimated_hours: number
  progress: number
}>) => {
  try {
    const response = await http.put(`projects/${projectId}/tasks/${taskId}`, taskData)
    return response
  } catch (error) {
    console.error(`更新任务 ${taskId} 失败:`, error)
    throw error
  }
}

// 删除任务
export const deleteTask = async (projectId: number, taskId: number) => {
  try {
    const response = await http.delete(`projects/${projectId}/tasks/${taskId}`)
    return response
  } catch (error) {
    console.error(`删除任务 ${taskId} 失败:`, error)
    throw error
  }
}

// 添加评论
export const addComment = async (projectId: number, taskId: number, content: string) => {
  try {
    const response = await http.post(`projects/${projectId}/tasks/${taskId}/comments`, { content })
    return response
  } catch (error) {
    console.error('添加评论失败:', error)
    throw error
  }
}

// 获取评论列表
export const getComments = async (projectId: number, taskId: number) => {
  try {
    const response = await http.get(`projects/${projectId}/tasks/${taskId}/comments`)
    return response
  } catch (error) {
    console.error('获取评论列表失败:', error)
    throw error
  }
}

// 获取标签列表
export const getLabels = async (projectId: number) => {
  try {
    const response = await http.get(`projects/${projectId}/labels`)
    return response
  } catch (error) {
    console.error('获取标签列表失败:', error)
    throw error
  }
}

// 创建标签
export const createLabel = async (projectId: number, labelData: { name: string; color?: string }) => {
  try {
    const response = await http.post(`projects/${projectId}/labels`, labelData)
    return response
  } catch (error) {
    console.error('创建标签失败:', error)
    throw error
  }
}
