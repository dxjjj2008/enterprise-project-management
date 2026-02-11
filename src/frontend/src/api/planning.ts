// 计划管理 API 客户端

// 计划数据类型定义
export interface Plan {
  id: number
  name: string
  project_id: number
  project_name: string
  status: 'draft' | 'active' | 'completed' | 'on_hold' | 'archived'
  progress: number
  start_date: string
  end_date: string
  description?: string
  owner_id: number
  owner_name: string
  owner_avatar?: string
  task_count: number
  completed_task_count: number
  created_at: string
  updated_at: string
}

export interface WBSTask {
  id: number
  plan_id: number
  parent_id: number | null
  name: string
  level: number
  sort_order: number
  assignee_id?: number
  assignee_name?: string
  assignee_avatar?: string
  start_date: string
  end_date: string
  duration: number
  progress: number
  dependency?: number[]
  is_milestone: boolean
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  children?: WBSTask[]
}

export interface Milestone {
  id: number
  plan_id: number
  name: string
  task_id: number
  plan_date: string
  status: 'pending' | 'completed'
}

export interface PaginationResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 获取计划列表
export const getPlans = async (params?: {
  page?: number
  pageSize?: number
  project_id?: number
  status?: string
  keyword?: string
  start_date?: string
  end_date?: string
}) => {
  try {
    const response = await http.get<PaginationResponse<Plan>>('plans', params)
    return response
  } catch (error) {
    console.error('获取计划列表失败:', error)
    throw error
  }
}

// 获取计划详情
export const getPlanById = async (id: number) => {
  try {
    const response = await http.get<Plan>(`plans/${id}`)
    return response
  } catch (error) {
    console.error(`获取计划 ${id} 失败:`, error)
    throw error
  }
}

// 创建计划
export const createPlan = async (planData: {
  name: string
  project_id: number
  description?: string
  start_date?: string
  end_date?: string
}) => {
  try {
    const response = await http.post<Plan>('plans', planData)
    return response
  } catch (error) {
    console.error('创建计划失败:', error)
    throw error
  }
}

// 更新计划
export const updatePlan = async (id: number, planData: Partial<Plan>) => {
  try {
    const response = await http.put<Plan>(`plans/${id}`, planData)
    return response
  } catch (error) {
    console.error(`更新计划 ${id} 失败:`, error)
    throw error
  }
}

// 删除计划
export const deletePlan = async (id: number) => {
  try {
    const response = await http.delete(`plans/${id}`)
    return response
  } catch (error) {
    console.error(`删除计划 ${id} 失败:`, error)
    throw error
  }
}

// 获取WBS任务列表
export const getWBSTasks = async (planId: number) => {
  try {
    const response = await http.get<WBSTask[]>(`plans/${planId}/wbs`)
    return response
  } catch (error) {
    console.error(`获取WBS任务失败:`, error)
    throw error
  }
}

// 添加WBS任务
export const addWBSTask = async (planId: number, taskData: Partial<WBSTask>) => {
  try {
    const response = await http.post<WBSTask>(`plans/${planId}/wbs`, taskData)
    return response
  } catch (error) {
    console.error('添加WBS任务失败:', error)
    throw error
  }
}

// 更新WBS任务
export const updateWBSTask = async (planId: number, taskId: number, taskData: Partial<WBSTask>) => {
  try {
    const response = await http.put<WBSTask>(`plans/${planId}/wbs/${taskId}`, taskData)
    return response
  } catch (error) {
    console.error(`更新WBS任务 ${taskId} 失败:`, error)
    throw error
  }
}

// 删除WBS任务
export const deleteWBSTask = async (planId: number, taskId: number) => {
  try {
    const response = await http.delete(`plans/${planId}/wbs/${taskId}`)
    return response
  } catch (error) {
    console.error(`删除WBS任务 ${taskId} 失败:`, error)
    throw error
  }
}

// 获取里程碑列表
export const getMilestones = async (planId: number) => {
  try {
    const response = await http.get<Milestone[]>(`plans/${planId}/milestones`)
    return response
  } catch (error) {
    console.error(`获取里程碑失败:`, error)
    throw error
  }
}

// 添加里程碑
export const addMilestone = async (planId: number, milestoneData: Partial<Milestone>) => {
  try {
    const response = await http.post<Milestone>(`plans/${planId}/milestones`, milestoneData)
    return response
  } catch (error) {
    console.error('添加里程碑失败:', error)
    throw error
  }
}

// 更新里程碑
export const updateMilestone = async (planId: number, milestoneId: number, milestoneData: Partial<Milestone>) => {
  try {
    const response = await http.put<Milestone>(`plans/${planId}/milestones/${milestoneId}`, milestoneData)
    return response
  } catch (error) {
    console.error(`更新里程碑 ${milestoneId} 失败:`, error)
    throw error
  }
}

// 删除里程碑
export const deleteMilestone = async (planId: number, milestoneId: number) => {
  try {
    const response = await http.delete(`plans/${planId}/milestones/${milestoneId}`)
    return response
  } catch (error) {
    console.error(`删除里程碑 ${milestoneId} 失败:`, error)
    throw error
  }
}

// 获取项目列表（用于筛选）
export const getProjectsForPlan = async () => {
  try {
    const response = await http.get<{ id: number; name: string }[]>('projects/list')
    return response
  } catch (error) {
    console.error('获取项目列表失败:', error)
    throw error
  }
}
