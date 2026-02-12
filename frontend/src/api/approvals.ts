// 审批管理 API 客户端

// 审批数据类型定义
export interface Approval {
  id: number
  type: string
  title: string
  description: string
  applicant_id: number
  applicant_name: string
  applicant_avatar?: string
  project_id?: number
  project_name?: string
  status: 'pending' | 'processing' | 'approved' | 'rejected' | 'cancelled'
  current_node: string
  flow_nodes: FlowNode[]
  created_at: string
  updated_at: string
}

export interface FlowNode {
  name: string
  approver_id: number
  approver_name: string
  status: 'pending' | 'approved' | 'rejected'
  comment?: string
  approved_at?: string
}

export interface ApprovalStats {
  pending: number
  approved: number
  rejected: number
  processing: number
}

export interface PaginationResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 获取审批列表
export const getApprovals = async (params?: {
  page?: number
  pageSize?: number
  type?: string
  status?: string
  keyword?: string
  start_date?: string
  end_date?: string
}) => {
  try {
    const response = await http.get<PaginationResponse<Approval>>('approvals', params)
    return response
  } catch (error) {
    console.error('获取审批列表失败:', error)
    throw error
  }
}

// 获取审批详情
export const getApprovalDetail = async (id: number) => {
  try {
    const response = await http.get<Approval>(`approvals/${id}`)
    return response
  } catch (error) {
    console.error(`获取审批详情失败: ${id}`, error)
    throw error
  }
}

// 创建审批
export const createApproval = async (data: {
  type: string
  title: string
  project_id?: number
  description?: string
}) => {
  try {
    const response = await http.post<Approval>('approvals', data)
    return response
  } catch (error) {
    console.error('创建审批失败:', error)
    throw error
  }
}

// 审批通过
export const approveApproval = async (id: number, data?: { comment?: string }) => {
  try {
    const response = await http.post(`approvals/${id}/approve`, data || {})
    return response
  } catch (error) {
    console.error(`审批通过失败: ${id}`, error)
    throw error
  }
}

// 审批拒绝
export const rejectApproval = async (id: number, data: { comment: string }) => {
  try {
    const response = await http.post(`approvals/${id}/reject`, data)
    return response
  } catch (error) {
    console.error(`审批拒绝失败: ${id}`, error)
    throw error
  }
}

// 审批退回
export const returnApproval = async (id: number, data: { comment: string; to_node?: number }) => {
  try {
    const response = await http.post(`approvals/${id}/return`, data)
    return response
  } catch (error) {
    console.error(`审批退回失败: ${id}`, error)
    throw error
  }
}

// 撤销审批
export const cancelApproval = async (id: number) => {
  try {
    const response = await http.post(`approvals/${id}/cancel`)
    return response
  } catch (error) {
    console.error(`撤销审批失败: ${id}`, error)
    throw error
  }
}

// 获取审批统计
export const getApprovalStats = async (params?: {
  start_date?: string
  end_date?: string
}) => {
  try {
    const response = await http.get<ApprovalStats>('approvals/stats', params)
    return response
  } catch (error) {
    console.error('获取审批统计失败:', error)
    throw error
  }
}

// 获取审批类型列表
export const getApprovalTypes = async () => {
  try {
    const response = await http.get<{ value: string; label: string; icon: string; color: string }[]>('approvals/types')
    return response
  } catch (error) {
    console.error('获取审批类型失败:', error)
    throw error
  }
}

// 获取我的待办审批
export const getMyPendingApprovals = async (params?: {
  page?: number
  pageSize?: number
}) => {
  try {
    const response = await http.get<PaginationResponse<Approval>>('approvals/my/pending', params)
    return response
  } catch (error) {
    console.error('获取我的待办失败:', error)
    throw error
  }
}

// 获取我的已办审批
export const getMyProcessedApprovals = async (params?: {
  page?: number
  pageSize?: number
}) => {
  try {
    const response = await http.get<PaginationResponse<Approval>>('approvals/my/processed', params)
    return response
  } catch (error) {
    console.error('获取我的已办失败:', error)
    throw error
  }
}
