// 报表统计 API 客户端

// 统计数据类型定义
export interface Statistics {
  project_total: number
  project_active: number
  project_completed: number
  project_overdue: number
  task_total: number
  task_completed: number
  task_overdue: number
  avg_progress: number
  budget_usage: number
  resource_usage: number
}

export interface ChartData {
  chart_type: string
  title: string
  x_axis: string[]
  series: { name: string; data: number[] }[]
  legend: string[]
  tooltip: object
}

export interface TableData {
  table_type: string
  headers: { key: string; label: string }[]
  rows: object[]
  total: number
}

export interface ProjectRank {
  id: number
  name: string
  manager: string
  progress: number
  task_completed: number
  task_total: number
  status: string
  updated_at: string
}

export interface TaskStats {
  id: number
  name: string
  assignee: string
  status: string
  progress: number
  due_date: string
  project: string
}

export interface ResourceUsage {
  id: number
  name: string
  department: string
  project_count: number
  planned_hours: number
  actual_hours: number
  utilization: number
  status: 'normal' | 'high' | 'low'
}

export interface DepartmentStats {
  id: number
  name: string
  project_count: number
  completed_count: number
  avg_progress: number
  member_count: number
}

// 获取核心统计数据
export const getStatistics = async (params?: {
  start_date?: string
  end_date?: string
  project_id?: number
}) => {
  try {
    const response = await http.get<Statistics>('reports/stats', params)
    return response
  } catch (error) {
    console.error('获取统计数据失败:', error)
    throw error
  }
}

// 获取图表数据
export const getChartData = async (chartType: string, params?: object) => {
  try {
    const response = await http.get<ChartData>(`reports/charts/${chartType}`, params)
    return response
  } catch (error) {
    console.error(`获取图表数据失败: ${chartType}`, error)
    throw error
  }
}

// 获取项目排行榜
export const getProjectRank = async (params?: {
  page?: number
  pageSize?: number
  order?: string
  start_date?: string
  end_date?: string
}) => {
  try {
    const response = await http.get<{ items: ProjectRank[]; total: number }>('reports/project-rank', params)
    return response
  } catch (error) {
    console.error('获取项目排行榜失败:', error)
    throw error
  }
}

// 获取任务统计
export const getTaskStats = async (params?: {
  page?: number
  pageSize?: number
  project_id?: number
  status?: string
}) => {
  try {
    const response = await http.get<{ items: { id: number; name: string; assignee: string; status: string; progress: number; due_date: string; project: string }[]; total: number }>('reports/task-stats', params)
    return response
  } catch (error) {
    console.error('获取任务统计失败:', error)
    throw error
  }
}

// 获取资源使用情况
export const getResourceUsage = async (params?: {
  page?: number
  pageSize?: number
  department_id?: number
}) => {
  try {
    const response = await http.get<{ items: ResourceUsage[]; total: number }>('reports/resource-usage', params)
    return response
  } catch (error) {
    console.error('获取资源使用情况失败:', error)
    throw error
  }
}

// 获取部门统计数据
export const getDepartmentStats = async () => {
  try {
    const response = await http.get<DepartmentStats[]>('reports/department-stats')
    return response
  } catch (error) {
    console.error('获取部门统计失败:', error)
    throw error
  }
}

// 导出报表
export const exportReport = async (params: {
  format: 'pdf' | 'excel' | 'csv'
  report_type: string
  start_date?: string
  end_date?: string
  project_id?: number
  include_charts?: boolean
}) => {
  try {
    const response = await http.get('reports/export', params)
    return response
  } catch (error) {
    console.error('导出报表失败:', error)
    throw error
  }
}

// 获取报表模板列表
export const getReportTemplates = async () => {
  try {
    const response = await http.get<{ id: number; name: string; type: string; description: string }[]>('reports/templates')
    return response
  } catch (error) {
    console.error('获取报表模板失败:', error)
    throw error
  }
}
