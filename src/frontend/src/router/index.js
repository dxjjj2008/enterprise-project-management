/**
 * Vue Router 路由配置
 * 
 * 企业项目管理系统
 */

import { createRouter, createWebHistory } from 'vue-router'

// 路由配置
const routes = [
  // 认证模块
  {
    path: '/auth',
    component: () => import('@/views/auth/Layout.vue'),
    children: [
      {
        path: 'login',
        name: 'Login',
        component: () => import('@/views/auth/Login.vue'),
        meta: { title: '登录' }
      },
      {
        path: 'register',
        name: 'Register',
        component: () => import('@/views/auth/Register.vue'),
        meta: { title: '注册' }
      }
    ]
  },

  // 主布局
  {
    path: '/',
    component: () => import('@/views/layout/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/Index.vue'),
        meta: { title: '仪表盘', icon: 'Odometer' }
      },
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('@/views/projects/List.vue'),
        meta: { title: '项目', icon: 'Folder' }
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetail',
        component: () => import('@/views/projects/Detail.vue'),
        meta: { title: '项目详情' }
      },
      {
        path: 'projects/:id/board',
        name: 'ProjectBoard',
        component: () => import('@/views/projects/Board.vue'),
        meta: { title: '任务看板' }
      },
      {
        path: 'projects/:id/gantt',
        name: 'ProjectGantt',
        component: () => import('@/views/projects/Gantt.vue'),
        meta: { title: '甘特图' }
      },
      {
        path: 'planning',
        name: 'Planning',
        component: () => import('@/views/planning/List.vue'),
        meta: { title: '计划管理', icon: 'Document' }
      },
      {
        path: 'resources',
        name: 'Resources',
        component: () => import('@/views/resources/Index.vue'),
        meta: { title: '资源管理', icon: 'User' }
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('@/views/reports/Index.vue'),
        meta: { title: '报表统计', icon: 'DataAnalysis' }
      },
      {
        path: 'approvals',
        name: 'Approvals',
        component: () => import('@/views/approvals/List.vue'),
        meta: { title: '审批', icon: 'Stamp' }
      },
      {
        path: 'tasks/board',
        name: 'TaskBoard',
        component: () => import('@/views/tasks/Board.vue'),
        meta: { title: '任务看板', icon: 'Tickets' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/settings/Index.vue'),
        meta: { title: '设置', icon: 'Setting' }
      },
      {
        path: 'docs',
        name: 'Docs',
        component: () => import('@/views/docs/Index.vue'),
        meta: { title: '文档中心', icon: 'Document' }
      },
      {
        path: 'docs/viewer',
        name: 'DocViewer',
        component: () => import('@/views/docs/DocViewer.vue'),
        meta: { title: '文档查看' }
      }
    ]
  },

  // 404
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/errors/404.vue'),
    meta: { title: '页面未找到' }
  }
]

// 创建路由
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 企业项目管理系统`
  } else {
    document.title = '企业项目管理系统'
  }
  
  next()
})

export default router
