// 全局 API 配置 - 使用原生 fetch

// 根据环境动态设置 API 地址
const getApiBaseUrl = () => {
  // 如果有 VITE_API_URL 环境变量则使用它
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  // 默认使用本地后端地址
  return 'http://localhost:8000/api/v1/'
}

const API_BASE_URL = getApiBaseUrl()

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  body?: Record<string, unknown> | FormData | URLSearchParams
  headers?: Record<string, string>
  params?: Record<string, string | number | boolean>
}

// 创建 API 请求函数
async function apiClient<T = unknown>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { method = 'GET', body, headers = {}, params } = options

  // 构建查询参数
  let url = endpoint
  if (params) {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      searchParams.append(key, String(value))
    })
    url += `?${searchParams.toString()}`
  }

  // 获取认证 token
  const token = localStorage.getItem('auth_token')

  // 设置请求头
  const requestHeaders: Record<string, string> = {
    ...headers,
  }

  // 如果有 token，添加到请求头
  if (token) {
    requestHeaders['Authorization'] = `Bearer ${token}`
  }

  // 构建请求选项
  const requestOptions: RequestInit = {
    method,
    headers: requestHeaders,
  }

  // 添加 body
  if (body) {
    if (body instanceof FormData) {
      requestOptions.body = body
    } else if (body instanceof URLSearchParams) {
      requestOptions.body = body.toString()
      requestHeaders['Content-Type'] = 'application/x-www-form-urlencoded'
    } else {
      requestHeaders['Content-Type'] = 'application/json'
      requestOptions.body = JSON.stringify(body)
    }
  }

  // 发送请求
  console.log('API请求:', { method, url: `${API_BASE_URL}${url}` })  // 调试日志
  const response = await fetch(`${API_BASE_URL}${url}`, requestOptions)
  console.log('API响应状态:', response.status)  // 调试日志

  // 处理 401 错误
  if (response.status === 401) {
    console.warn('API 401错误，token可能无效')  // 调试日志
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_info')
    window.location.href = '/auth/login'
    throw new Error('Unauthorized')
  }

  // 处理其他错误
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `HTTP Error: ${response.status}`)
  }

  // 返回 JSON 数据
  return response.json()
}

// 封装常用方法
export const http = {
  get: <T = unknown>(endpoint: string, params?: Record<string, string | number | boolean>, headers?: Record<string, string>) =>
    apiClient<T>(endpoint, { method: 'GET', params, headers }),

  post: <T = unknown>(endpoint: string, body?: Record<string, unknown> | FormData, params?: Record<string, string | number | boolean>, headers?: Record<string, string>) =>
    apiClient<T>(endpoint, { method: 'POST', body, params, headers }),

  put: <T = unknown>(endpoint: string, body?: Record<string, unknown>, params?: Record<string, string | number | boolean>, headers?: Record<string, string>) =>
    apiClient<T>(endpoint, { method: 'PUT', body, params, headers }),

  delete: <T = unknown>(endpoint: string, params?: Record<string, string | number | boolean>, headers?: Record<string, string>) =>
    apiClient<T>(endpoint, { method: 'DELETE', params, headers }),
}

// OAuth2 登录专用函数（发送 form-data）
export const login = async (username: string, password: string) => {
  const formData = new URLSearchParams()
  formData.append('username', username)
  formData.append('password', password)
  
  return apiClient<{ access_token: string; token_type: string; user: Record<string, unknown> }>(
    'auth/login',
    { method: 'POST', body: formData }
  )
}

export default apiClient