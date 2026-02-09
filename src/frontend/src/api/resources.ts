// 资源管理 API 客户端
import { http } from '@/api'

// 获取用户列表
export const getUsers = async (params?: { role?: string; is_active?: boolean }) => {
  try {
    const response = await http.get('resources/users', params)
    return response
  } catch (error) {
    console.error('获取用户列表失败:', error)
    throw error
  }
}

// 获取用户详情
export const getUserDetail = async (userId: number) => {
  try {
    const response = await http.get(`resources/users/${userId}`)
    return response
  } catch (error) {
    console.error(`获取用户 ${userId} 详情失败:`, error)
    throw error
  }
}

// 获取团队工作负载
export const getTeamWorkload = async () => {
  try {
    const response = await http.get('resources/workload')
    return response
  } catch (error) {
    console.error('获取团队工作负载失败:', error)
    throw error
  }
}

// 获取资源利用率
export const getResourceUtilization = async (projectId?: number) => {
  try {
    const params = projectId ? { project_id: projectId } : undefined
    const response = await http.get('resources/utilization', params)
    return response
  } catch (error) {
    console.error('获取资源利用率失败:', error)
    throw error
  }
}
