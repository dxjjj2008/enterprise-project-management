// 项目管理 API 客户端
import { http } from '@/api/index'
import { ProjectResponse, PaginationResponse } from '@/schemas/project'

// 获取项目列表
export const getProjects = async (page: number = 1, pageSize: number = 10) => {
  try {
    const response = await http.get<PaginationResponse<ProjectResponse>>(
      `projects`,
      { page, limit: pageSize }
    )
    return response
  } catch (error) {
    console.error('获取项目列表失败:', error)
    throw error
  }
}

// 创建项目 - 不需要传key，后端自动生成
export const createProject = async (projectData: {
  name: string
  description?: string
  start_date?: string
  end_date?: string
}) => {
  try {
    // 使用FormData格式发送数据（不含key，后端自动生成）
    const formData = new URLSearchParams()
    formData.append('name', projectData.name)
    if (projectData.description) {
      formData.append('description', projectData.description)
    }
    if (projectData.start_date) {
      formData.append('start_date', projectData.start_date)
    }
    if (projectData.end_date) {
      formData.append('end_date', projectData.end_date)
    }

    const response = await http.post<ProjectResponse>(`projects`, formData)
    return response
  } catch (error) {
    console.error('创建项目失败:', error)
    throw error
  }
}

// 获取下一个可用的项目Key（预览用）
export const getNextProjectKey = async () => {
  try {
    const response = await http.get<{ key: string; format: string; description: string }>(`projects/next-key`)
    return response
  } catch (error) {
    console.error('获取项目Key失败:', error)
    throw error
  }
}

// 获取项目详情
export const getProjectById = async (id: number) => {
  try {
    const response = await http.get<ProjectResponse>(`projects/${id}`)
    return response
  } catch (error) {
    console.error(`获取项目 ${id} 失败:`, error)
    throw error
  }
}

// 更新项目
export const updateProject = async (id: number, projectData: any) => {
  try {
    const response = await http.put<ProjectResponse>(`projects/${id}`, projectData)
    return response
  } catch (error) {
    console.error(`更新项目 ${id} 失败:`, error)
    throw error
  }
}

// 删除项目
export const deleteProject = async (id: number) => {
  try {
    const response = await http.delete(`projects/${id}`)
    return response
  } catch (error) {
    console.error(`删除项目 ${id} 失败:`, error)
    throw error
  }
}