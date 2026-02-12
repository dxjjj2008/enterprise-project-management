// 甘特图 API 客户端

// 甘特图任务类型定义
export interface GanttTask {
  id: number
  project_id: number
  parent_id: number | null
  title: string
  description?: string
  status: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  assignee_id?: number
  assignee_name?: string
  assignee_avatar?: string
  start_date: string | null
  due_date: string | null
  completed_at?: string
  progress: number
  is_milestone: boolean
  is_group: boolean
  dependencies: number[]
  estimated_hours?: number
  created_at: string
  updated_at: string
  children?: GanttTask[]
  expanded?: boolean
  selected?: boolean
}

// 甘特图配置
export interface GanttConfig {
  view_mode: 'day' | 'week' | 'month'
  day_width: number
  row_height: number
  show_weekends: boolean
  show_today: boolean
  show_progress: boolean
  show_dependencies: boolean
}

// 甘特图筛选参数
export interface GanttFilter {
  status?: string
  priority?: string
  assignee_id?: number
  keyword?: string
}

// 获取甘特图任务列表
export const getGanttTasks = async (projectId: number, params?: GanttFilter) => {
  try {
    const response = await http.get<{ items: GanttTask[] }>(`projects/${projectId}/gantt`, params)
    return response
  } catch (error) {
    console.error('获取甘特图任务失败:', error)
    throw error
  }
}

// 获取甘特图配置
export const getGanttConfig = async (projectId: number) => {
  try {
    const response = await http.get<GanttConfig>(`projects/${projectId}/gantt/config`)
    return response
  } catch (error) {
    console.error('获取甘特图配置失败:', error)
    throw error
  }
}

// 更新甘特图配置
export const updateGanttConfig = async (projectId: number, config: Partial<GanttConfig>) => {
  try {
    const response = await http.put<GanttConfig>(`projects/${projectId}/gantt/config`, config)
    return response
  } catch (error) {
    console.error('更新甘特图配置失败:', error)
    throw error
  }
}

// 更新任务日期（拖拽调整）
export const updateTaskDates = async (
  projectId: number,
  taskId: number,
  data: {
    start_date?: string
    due_date?: string
    duration?: number
  }
) => {
  try {
    const response = await http.put(`projects/${projectId}/tasks/${taskId}/dates`, data)
    return response
  } catch (error) {
    console.error('更新任务日期失败:', error)
    throw error
  }
}

// 更新任务进度
export const updateTaskProgress = async (projectId: number, taskId: number, progress: number) => {
  try {
    const response = await http.put(`projects/${projectId}/tasks/${taskId}/progress`, { progress })
    return response
  } catch (error) {
    console.error('更新任务进度失败:', error)
    throw error
  }
}

// 添加任务依赖
export const addTaskDependency = async (
  projectId: number,
  taskId: number,
  dependencyId: number,
  type: 'fs' | 'ss' | 'ff' | 'sf' = 'fs'
) => {
  try {
    const response = await http.post(`projects/${projectId}/tasks/${taskId}/dependencies`, {
      dependent_id: dependencyId,
      type
    })
    return response
  } catch (error) {
    console.error('添加任务依赖失败:', error)
    throw error
  }
}

// 删除任务依赖
export const removeTaskDependency = async (projectId: number, taskId: number, dependencyId: number) => {
  try {
    const response = await http.delete(`projects/${projectId}/tasks/${taskId}/dependencies/${dependencyId}`)
    return response
  } catch (error) {
    console.error('删除任务依赖失败:', error)
    throw error
  }
}

// 获取里程碑列表
export const getMilestones = async (projectId: number) => {
  try {
    const response = await http.get(`projects/${projectId}/milestones`)
    return response
  } catch (error) {
    console.error('获取里程碑列表失败:', error)
    throw error
  }
}

// 导出甘特图
export const exportGantt = async (
  projectId: number,
  format: 'png' | 'pdf' | 'xlsx' | 'csv'
) => {
  try {
    const response = await http.get(`projects/${projectId}/gantt/export`, {
      format,
      responseType: 'blob'
    })
    return response
  } catch (error) {
    console.error('导出甘特图失败:', error)
    throw error
  }
}

// 甘特图统计
export interface GanttStats {
  total_tasks: number
  completed_tasks: number
  in_progress_tasks: number
  overdue_tasks: number
  overall_progress: number
  milestones_completed: number
  milestones_total: number
  critical_path: number[]
}

export const getGanttStats = async (projectId: number) => {
  try {
    const response = await http.get<GanttStats>(`projects/${projectId}/gantt/stats`)
    return response
  } catch (error) {
    console.error('获取甘特图统计失败:', error)
    throw error
  }
}
