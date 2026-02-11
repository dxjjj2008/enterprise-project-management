<template>
  <div class="main-layout" @mousemove="handleMouseMove" @mouseup="handleMouseUp" @mouseleave="handleMouseUp">
    <!-- 移动端遮罩层 -->
    <div class="sidebar-mask" :class="{ 'is-visible': showMobileSidebar }" @click="closeMobileSidebar" />

    <!-- 侧边栏 -->
    <aside 
      class="sidebar-container" 
      :class="{ 
        'is-collapsed': collapsed,
        'is-mobile-open': showMobileSidebar
      }"
      :style="{ width: isMobile ? '100%' : (collapsed ? '64px' : sidebarWidth + 'px') }"
    >
      <div class="sidebar-header">
        <div class="logo" v-if="!collapsed || isMobile" @click="$router.push('/')">
          <el-icon :size="32" color="#1E5EB8"><Folder /></el-icon>
          <span class="logo-text">项目管理</span>
        </div>
        <el-icon v-if="!isMobile" :size="20" @click="collapsed = !collapsed" class="collapse-btn">
          <Fold v-if="!collapsed" />
          <Expand v-else />
        </el-icon>
        <!-- 移动端关闭按钮 -->
        <el-icon v-else :size="24" @click="closeMobileSidebar" class="mobile-close-btn">
          <Close />
        </el-icon>
      </div>
      
      <el-menu
        :default-active="currentRoute"
        :collapse="collapsed && !isMobile"
        :collapse-transition="false"
        router
        class="sidebar-menu"
        @select="onMenuSelect"
      >
        <el-menu-item index="/">
          <el-icon><Odometer /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>
        
        <el-menu-item index="/projects">
          <el-icon><Folder /></el-icon>
          <template #title>项目</template>
        </el-menu-item>
        
        <el-menu-item index="/planning">
          <el-icon><Document /></el-icon>
          <template #title>计划管理</template>
        </el-menu-item>
        
        <el-menu-item index="/resources">
          <el-icon><User /></el-icon>
          <template #title>资源</template>
        </el-menu-item>
        
        <el-menu-item index="/reports">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>报表</template>
        </el-menu-item>
        
        <el-menu-item index="/approvals">
          <el-icon><Stamp /></el-icon>
          <template #title>审批</template>
        </el-menu-item>
        
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>设置</template>
        </el-menu-item>
      </el-menu>
      
      <!-- 收起后的Logo -->
      <div class="sidebar-footer" v-if="collapsed && !isMobile">
        <el-icon :size="24" color="#1E5EB8"><Folder /></el-icon>
      </div>
    </aside>
    
    <!-- 拖拽调整手柄（桌面端） -->
    <div 
      v-if="!isMobile"
      class="resize-handle" 
      @mousedown="handleMouseDown"
      :class="{ 'is-collapsed': collapsed }"
    >
      <el-icon class="resize-icon"><MoreFilled /></el-icon>
    </div>
    
    <!-- 主内容区 -->
    <div class="main-wrapper">
      <!-- 顶部导航 -->
      <header class="header-container">
        <div class="header-left">
          <!-- 移动端菜单按钮 -->
          <el-button 
            v-if="isMobile" 
            :icon="Menu" 
            circle 
            @click="openMobileSidebar"
            class="mobile-menu-btn"
          />
          <el-breadcrumb separator="/" :class="{ 'is-hidden': isMobile && !currentPageTitle }">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentPageTitle">{{ currentPageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <!-- 平板/桌面搜索框 -->
          <div class="global-search" v-if="!isMobile">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索项目、任务..."
              :prefix-icon="Search"
              clearable
              size="default"
              @keyup.enter="handleSearch"
              @clear="handleClear"
              class="search-input"
            />
            <div class="search-dropdown" v-if="showSearchResults && searchKeyword">
              <div class="search-results">
                <div class="search-section">
                  <div class="search-section-title">项目</div>
                  <div class="search-item" v-for="p in searchResults.projects" :key="p.id" @click="goToProject(p.id)">
                    <el-icon><Folder /></el-icon>
                    <span>{{ p.name }}</span>
                  </div>
                  <div class="search-empty" v-if="!searchResults.projects.length">暂无结果</div>
                </div>
                <div class="search-section">
                  <div class="search-section-title">任务</div>
                  <div class="search-item" v-for="t in searchResults.tasks" :key="t.id" @click="goToTask(t.id)">
                    <el-icon><Tickets /></el-icon>
                    <span>{{ t.title }}</span>
                  </div>
                  <div class="search-empty" v-if="!searchResults.tasks.length">暂无结果</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 移动端快捷搜索按钮 -->
          <el-button v-if="isMobile" :icon="Search" circle @click="showMobileSearch = true" />
          
          <el-dropdown trigger="click">
            <div class="user-dropdown">
              <el-avatar :size="isMobile ? 28 : 32" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" />
              <span class="username" v-if="!isMobile">张经理</span>
              <el-icon v-if="!isMobile"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人中心</el-dropdown-item>
                <el-dropdown-item>设置</el-dropdown-item>
                <el-dropdown-item divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          
          <!-- 帮助按钮 -->
          <el-tooltip content="帮助文档" placement="bottom">
            <el-button :icon="QuestionFilled" circle @click="openHelp" />
          </el-tooltip>
        </div>
      </header>
      
      <!-- 页面内容 -->
      <main class="main-content">
        <router-view />
      </main>
    </div>

    <!-- 移动端搜索弹窗 -->
    <el-dialog
      v-model="showMobileSearch"
      title="搜索"
      width="90%"
      :show-close="false"
      class="mobile-search-dialog"
    >
      <el-input
        v-model="searchKeyword"
        placeholder="搜索项目、任务..."
        :prefix-icon="Search"
        clearable
        size="large"
        @keyup.enter="handleSearch"
        @clear="handleClear"
        autofocus
      />
      <div class="search-results" v-if="showSearchResults && searchKeyword">
        <div class="search-section">
          <div class="search-section-title">项目</div>
          <div class="search-item" v-for="p in searchResults.projects" :key="p.id" @click="goToProject(p.id); showMobileSearch = false">
            <el-icon><Folder /></el-icon>
            <span>{{ p.name }}</span>
          </div>
          <div class="search-empty" v-if="!searchResults.projects.length">暂无结果</div>
        </div>
        <div class="search-section">
          <div class="search-section-title">任务</div>
          <div class="search-item" v-for="t in searchResults.tasks" :key="t.id" @click="goToTask(t.id); showMobileSearch = false">
            <el-icon><Tickets /></el-icon>
            <span>{{ t.title }}</span>
          </div>
          <div class="search-empty" v-if="!searchResults.tasks.length">暂无结果</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showMobileSearch = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Folder, Odometer, Document, User, DataAnalysis,
  Stamp, Setting, Bell, ArrowDown, Fold, Expand, Search, Tickets, MoreFilled, QuestionFilled,
  Menu, Close
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const collapsed = ref(false)
const searchKeyword = ref('')
const showSearchResults = ref(false)
const isMobile = ref(false)
const showMobileSidebar = ref(false)
const showMobileSearch = ref(false)
const mobileBreakpoint = 768 // tabletPortrait

// 侧边栏宽度拖拽
const sidebarWidth = ref(240)
const minSidebarWidth = 160
const maxSidebarWidth = 400
const isResizing = ref(false)
const startX = ref(0)
const startWidth = ref(0)

// 检测屏幕尺寸
const checkMobile = () => {
  isMobile.value = window.innerWidth < mobileBreakpoint
  if (isMobile.value) {
    collapsed.value = true
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

const handleMouseDown = (e) => {
  if (collapsed.value) return
  isResizing.value = true
  startX.value = e.clientX
  startWidth.value = sidebarWidth.value
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
}

const handleMouseMove = (e) => {
  if (!isResizing.value) return
  const diff = e.clientX - startX.value
  sidebarWidth.value = Math.min(Math.max(startWidth.value + diff, minSidebarWidth), maxSidebarWidth)
}

const handleMouseUp = () => {
  if (isResizing.value) {
    isResizing.value = false
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }
}

// 收起时重置宽度
watch(collapsed, (val) => {
  if (val && !isMobile.value) {
    sidebarWidth.value = 64
  } else if (!isMobile.value) {
    sidebarWidth.value = 240
  }
})

// 移动端侧边栏控制
const openMobileSidebar = () => {
  showMobileSidebar.value = true
  document.body.style.overflow = 'hidden'
}

const closeMobileSidebar = () => {
  showMobileSidebar.value = false
  document.body.style.overflow = ''
}

// 菜单选择时关闭移动端侧边栏
const onMenuSelect = () => {
  if (isMobile.value) {
    closeMobileSidebar()
  }
}

// 模拟搜索结果（实际对接后端API）
const searchResults = computed(() => {
  if (!searchKeyword.value) return { projects: [], tasks: [] }
  
  // 模拟数据
  const keyword = searchKeyword.value.toLowerCase()
  return {
    projects: [
      { id: 1, name: '企业项目管理系统 V1.0' },
      { id: 2, name: '技术架构升级项目' }
    ].filter(p => p.name.toLowerCase().includes(keyword)),
    tasks: [
      { id: 1, title: '完成需求文档编写' },
      { id: 2, title: '评审技术方案' }
    ].filter(t => t.title.toLowerCase().includes(keyword))
  }
})

const handleSearch = () => {
  if (searchKeyword.value) {
    showSearchResults.value = true
  }
}

const handleClear = () => {
  searchKeyword.value = ''
  showSearchResults.value = false
}

const goToProject = (id) => {
  router.push(`/projects/${id}`)
  showSearchResults.value = false
  searchKeyword.value = ''
}

const goToTask = (id) => {
  // 跳转到任务详情
  showSearchResults.value = false
  searchKeyword.value = ''
}

// 打开帮助文档
const openHelp = () => {
  window.open('/docs', '_blank')
}

// 点击外部关闭搜索结果
watch(() => route.path, () => {
  showSearchResults.value = false
  if (isMobile.value) {
    closeMobileSidebar()
  }
})

const currentRoute = computed(() => route.path)
const currentPageTitle = computed(() => route.meta.title || '页面')

// 菜单配置
const menuItems = [
  { path: '/', icon: Odometer, title: '仪表盘' },
  { path: '/projects', icon: Folder, title: '项目' },
  { path: '/planning', icon: Document, title: '计划管理' },
  { path: '/resources', icon: User, title: '资源' },
  { path: '/reports', icon: DataAnalysis, title: '报表' },
  { path: '/approvals', icon: Stamp, title: '审批' },
  { path: '/tasks/board', icon: Tickets, title: '任务看板' },
  { path: '/settings', icon: Setting, title: '设置' }
]
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar-container {
  width: 240px;
  min-width: 64px;
  background: #FFFFFF;
  border-right: 1px solid #F0F0F0;
  display: flex;
  flex-direction: column;
  transition: width 0.3s, min-width 0.3s;
  position: relative;
  z-index: 10;
}

.sidebar-container.is-collapsed {
  width: 64px;
  min-width: 64px;
}

.sidebar-header {
  height: 64px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #F0F0F0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
  cursor: pointer;
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  white-space: nowrap;
}

.collapse-btn {
  cursor: pointer;
  color: #8C8C8C;
  flex-shrink: 0;
}

.collapse-btn:hover {
  color: #1E5EB8;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  padding: 8px 0;
  overflow-y: auto;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 100%;
}

.sidebar-footer {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-top: 1px solid #F0F0F0;
}

/* 拖拽调整手柄 */
.resize-handle {
  width: 6px;
  height: 100vh;
  background: transparent;
  cursor: col-resize;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  position: relative;
  z-index: 20;
}

.resize-handle:hover {
  background: #1E5EB8;
}

.resize-handle.is-collapsed {
  cursor: default;
}

.resize-handle.is-collapsed:hover {
  background: transparent;
}

.resize-icon {
  color: #BFBFBF;
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.2s;
}

.resize-handle:hover .resize-icon {
  opacity: 1;
}

.resize-handle.is-collapsed .resize-icon {
  opacity: 0;
}

.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header-container {
  height: 64px;
  background: #FFFFFF;
  border-bottom: 1px solid #F0F0F0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

/* 全局搜索框 */
.global-search {
  position: relative;
  width: 280px;
}

.search-input {
  width: 100%;
}

.search-input :deep(.el-input__wrapper) {
  background: #F5F7FA;
  border: none;
  border-radius: 8px;
  box-shadow: none;
}

.search-input :deep(.el-input__inner) {
  background: transparent;
  color: #262626;
}

.search-input :deep(.el-input__inner::placeholder) {
  color: #8C8C8C;
}

.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 8px;
  background: #FFFFFF;
  border: 1px solid #E4E7ED;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 360px;
  overflow-y: auto;
}

.search-results {
  padding: 8px;
}

.search-section {
  margin-bottom: 8px;
}

.search-section:last-child {
  margin-bottom: 0;
}

.search-section-title {
  font-size: 12px;
  font-weight: 600;
  color: #8C8C8C;
  padding: 4px 8px;
}

.search-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #262626;
}

.search-item:hover {
  background: #F5F7FA;
}

.search-empty {
  padding: 8px 12px;
  font-size: 13px;
  color: #BFBFBF;
}

.notification-badge {
  cursor: pointer;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #262626;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  background: #F5F7FA;
  padding: 24px;
}

/* ========== 响应式布局 ========== */

/* 平板端 (768px - 1024px) */
@media screen and (min-width: 768px) and (max-width: 1024px) {
  .sidebar-container {
    width: 200px;
    min-width: 64px;
  }
  
  .sidebar-header {
    padding: 0 12px;
  }
  
  .logo-text {
    font-size: 14px;
  }
  
  .header-container {
    padding: 0 16px;
  }
  
  .global-search {
    width: 200px;
  }
  
  .username {
    display: none;
  }
  
  .main-content {
    padding: 16px;
  }
}

/* 移动端 (< 768px) */
@media screen and (max-width: 767px) {
  .main-layout {
    flex-direction: column;
  }
  
  /* 侧边栏 - 移动端 */
  .sidebar-container {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    width: 280px;
    max-width: 85vw;
    z-index: 1001;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  }
  
  .sidebar-container.is-mobile-open {
    transform: translateX(0);
  }
  
  .sidebar-header {
    height: 56px;
    padding: 0 16px;
  }
  
  .logo-text {
    font-size: 16px;
  }
  
  .sidebar-menu {
    padding: 8px 0;
  }
  
  .sidebar-footer {
    display: none;
  }
  
  .collapse-btn {
    display: none;
  }
  
  .mobile-close-btn {
    color: #8C8C8C;
  }
  
  /* 遮罩层 */
  .sidebar-mask {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 1000;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.3s, visibility 0.3s;
  }
  
  .sidebar-mask.is-visible {
    opacity: 1;
    visibility: visible;
  }
  
  /* 拖拽手柄 - 移动端隐藏 */
  .resize-handle {
    display: none;
  }
  
  /* 主内容区 */
  .main-wrapper {
    width: 100%;
    min-height: 100vh;
  }
  
  /* 顶部导航 */
  .header-container {
    height: 56px;
    padding: 0 12px;
    position: sticky;
    top: 0;
    z-index: 100;
  }
  
  .header-left {
    flex: 1;
    min-width: 0;
  }
  
  .mobile-menu-btn {
    margin-right: 8px;
  }
  
  .header-right {
    gap: 8px;
  }
  
  .global-search {
    display: none;
  }
  
  .username {
    display: none;
  }
  
  /* 面包屑 - 移动端 */
  .el-breadcrumb {
    font-size: 12px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  .el-breadcrumb.is-hidden {
    display: none;
  }
  
  /* 用户下拉 */
  .user-dropdown {
    padding: 4px;
  }
  
  /* 页面内容 */
  .main-content {
    padding: 12px;
    min-height: calc(100vh - 56px);
  }
  
  /* 搜索弹窗 */
  .mobile-search-dialog {
    margin: 20px;
  }
  
  .mobile-search-dialog :deep(.el-dialog) {
    margin: 0;
    max-width: calc(100vw - 40px);
  }
  
  .search-results {
    margin-top: 16px;
  }
}

/* 小屏移动端 (< 480px) */
@media screen and (max-width: 479px) {
  .header-container {
    padding: 0 8px;
  }
  
  .main-content {
    padding: 8px;
  }
  
  .sidebar-container {
    width: 260px;
    max-width: 80vw;
  }
}

/* 打印样式 */
@media print {
  .sidebar-container,
  .resize-handle,
  .header-container {
    display: none;
  }
  
  .main-wrapper {
    width: 100%;
  }
  
  .main-content {
    padding: 0;
    background: white;
  }
}
</style>
