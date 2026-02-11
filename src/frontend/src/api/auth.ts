// 认证 API 客户端
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

// 配置 API 基础查询
const baseQuery = fetchBaseQuery({
  baseUrl: 'http://localhost:8000/api/v1/',
  prepareHeaders: (headers) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      headers.set('Authorization', `Bearer ${token}`)
    }
    return headers
  }
})

// 创建认证 API
export const authApi = createApi({
  reducerPath: 'authApi',
  baseQuery,
  endpoints: (builder) => ({
    login: builder.mutation({
      query: (credentials) => ({
        url: 'auth/login',
        method: 'POST',
        body: credentials
      })
    }),
    
    register: builder.mutation({
      query: (userData) => ({
        url: 'auth/register',
        method: 'POST',
        body: userData
      })
    }),
    
    getCurrentUser: builder.query({
      query: () => 'auth/me',
      providesTags: ['User']
    })
  })
})

export const { useLoginMutation, useRegisterMutation, useGetCurrentUserQuery } = authApi