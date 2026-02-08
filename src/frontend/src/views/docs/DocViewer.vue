<template>
  <div class="doc-viewer-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <el-page-header @back="goBack">
          <template #content>
            <span class="page-title">{{ docTitle }}查看</span>
          </template>
        </el-page-header>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索文档内容..."
          :prefix-icon="Search"
          clearable
          size="default"
          @input="handleSearch"
          class="doc-search"
        />
      </div>
    </div>
    
    <!-- 文档区域 -->
    <div class="doc-layout">
      <!-- 左侧目录 -->
      <aside class="doc-sidebar" v-if="!sidebarCollapsed">
        <div class="sidebar-header">
          <span class="sidebar-title">目录</span>
          <el-button :icon="ArrowLeft" circle size="small" @click="sidebarCollapsed = true" title="收起目录" />
        </div>
        <ul class="sidebar-toc">
          <li 
            v-for="item in toc" 
            :key="item.id" 
            :class="['toc-item', 'toc-level-' + item.level, { active: activeHeading === item.id }]"
          >
            <a @click.prevent="scrollTo(item.id)">{{ item.text }}</a>
          </li>
        </ul>
      </aside>
      
      <!-- 目录收起时显示的展开按钮 -->
      <div class="sidebar-toggle" v-if="sidebarCollapsed">
        <el-button :icon="ArrowRight" circle size="large" @click="sidebarCollapsed = false" title="展开目录" />
      </div>
      
      <!-- 右侧内容 -->
      <div class="doc-content" ref="contentRef">
        <div class="markdown-body" v-html="renderedContent"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import { Search, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

// 简单计数器
let headingIndex = 0

// 配置 marked 为标题添加 id
marked.use({
  renderer: {
    heading(token) {
      const id = 'heading-' + headingIndex++
      const level = token.depth
      const text = token.text
      return `<h${level} id="${id}">${text}</h${level}>`
    }
  }
})

// 使用 vite 的 raw loader 导入 markdown 文件
import userManual from '@/docs/2026-02-08-user-manual.md?raw'
import requirements from '@/docs/2026-02-08-requirements.md?raw'
import uiDesign from '@/docs/2026-02-08-ui-ux-design.md?raw'
import systemDesign from '@/docs/2026-02-08-project-management-system-design.md?raw'
import moduleDesign from '@/docs/2026-02-08-project-plan-module-design.md?raw'
import apiDoc from '@/docs/2026-02-08-api.md?raw'

const route = useRoute()
const router = useRouter()
const contentRef = ref(null)
const activeHeading = ref('')
const searchKeyword = ref('')
const sidebarCollapsed = ref(false)

const originalTitle = document.title

const docMap = {
  '/docs/manual/2026-02-08-user-manual.md': { title: '用户手册', content: userManual },
  '/docs/requirements/2026-02-08-requirements.md': { title: '需求文档', content: requirements },
  '/docs/plans/2026-02-08-ui-ux-design.md': { title: 'UI/UX设计', content: uiDesign },
  '/docs/plans/2026-02-08-project-management-system-design.md': { title: '系统架构', content: systemDesign },
  '/docs/plans/2026-02-08-project-plan-module-design.md': { title: '模块设计', content: moduleDesign },
  '/docs/api/2026-02-08-api.md': { title: 'API文档', content: apiDoc }
}

const docTitle = computed(() => {
  const path = route.query.path || ''
  const title = docMap[path]?.title || '文档'
  return title
})

const pageTitle = computed(() => {
  return `${docTitle.value}查看 - 企业项目管理系统`
})

// 解析内容并提取目录
const parsedContent = computed(() => {
  // 重置索引
  headingIndex = 0
  
  const path = route.query.path || ''
  const doc = docMap[path]
  if (!doc) return { html: '', toc: [] }
  
  // 解析 markdown
  const html = marked.parse(doc.content || '')
  
  // 提取目录
  const toc = []
  const headingRegex = /<h([1-6])[^>]*id="([^"]+)"[^>]*>([^<]+)<\/h[1-6]>/g
  let match
  while ((match = headingRegex.exec(html)) !== null) {
    const level = parseInt(match[1])
    const text = match[3].trim()
    const id = match[2]
    toc.push({ level, id, text })
  }
  
  return { html, toc }
})

const renderedContent = computed(() => {
  return parsedContent.value.html
})

const toc = computed(() => parsedContent.value.toc)

const goBack = () => {
  router.push('/docs')
}

const scrollTo = (id) => {
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

// 文档内搜索
const handleSearch = () => {
  if (!searchKeyword.value) {
    document.querySelectorAll('.markdown-body mark').forEach(el => {
      el.outerHTML = el.innerHTML
    })
    return
  }
  
  const content = document.querySelector('.markdown-body')
  const text = content.innerHTML
  
  // 清除之前的高亮
  document.querySelectorAll('.markdown-body mark').forEach(el => {
    el.outerHTML = el.innerHTML
  })
  
  // 高亮搜索词
  const regex = new RegExp(`(${searchKeyword.value})`, 'gi')
  content.innerHTML = text.replace(regex, '<mark>$1</mark>')
  
  // 跳转到第一个匹配
  const firstMatch = document.querySelector('.markdown-body mark')
  if (firstMatch) {
    firstMatch.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

// 监听滚动，高亮当前标题
const handleScroll = () => {
  const headings = document.querySelectorAll('.markdown-body h1, .markdown-body h2, .markdown-body h3')
  for (let i = headings.length - 1; i >= 0; i--) {
    const rect = headings[i].getBoundingClientRect()
    if (rect.top <= 100) {
      activeHeading.value = headings[i].id
      return
    }
  }
}

onMounted(() => {
  document.title = pageTitle.value
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  document.title = originalTitle
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.doc-viewer-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0;
}

/* 页面标题 - 固定在最上方 */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
  background: #f5f5f5;
  padding: 12px 20px;
  margin: 0;
  border-bottom: 1px solid #E8E8E8;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  width: 240px;
}

.doc-search {
  width: 100%;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
}

/* 布局 */
.doc-layout {
  display: flex;
  height: calc(100vh - 56px);
  overflow: hidden;
}

/* 左侧目录 - 独立滚动 */
.doc-sidebar {
  width: 220px;
  flex-shrink: 0;
  background: #FAFAFA;
  overflow-y: auto;
  padding: 12px 16px;
  border-right: 1px solid #E8E8E8;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
}

.sidebar-toc {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-item {
  margin-bottom: 2px;
}

.toc-item a {
  display: block;
  padding: 6px 8px;
  font-size: 13px;
  color: #595959;
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.2s;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.toc-item a:hover {
  color: #1E5EB8;
  background: #E6F4FF;
}

.toc-item.active a {
  color: #1E5EB8;
  background: #E6F4FF;
  font-weight: 500;
}

.toc-level-1 { padding-left: 0; }
.toc-level-2 { padding-left: 12px; }
.toc-level-3 { padding-left: 24px; font-size: 12px; }
.toc-level-4 { padding-left: 36px; font-size: 12px; }

/* 目录收起按钮 */
.sidebar-toggle {
  width: 40px;
  flex-shrink: 0;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 12px;
  background: #FAFAFA;
  border-right: 1px solid #E8E8E8;
}

/* 右侧内容 - 独立滚动 */
.doc-content {
  flex: 1;
  background: #FFFFFF;
  border-left: 1px solid #E4E7ED;
  padding: 32px;
  min-width: 0;
  overflow-y: auto;
  height: 100%;
}

.markdown-body {
  line-height: 1.8;
  font-size: 14px;
  color: #262626;
}

.markdown-body :deep(h1) {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #E8E8E8;
}

.markdown-body :deep(h2) {
  font-size: 20px;
  font-weight: 600;
  margin-top: 32px;
  margin-bottom: 16px;
}

.markdown-body :deep(h3) {
  font-size: 16px;
  font-weight: 600;
  margin-top: 24px;
  margin-bottom: 12px;
}

.markdown-body :deep(p) {
  margin-bottom: 16px;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin-bottom: 16px;
  padding-left: 24px;
}

.markdown-body :deep(li) {
  margin-bottom: 8px;
}

.markdown-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 24px;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid #E8E8E8;
  padding: 12px 16px;
  text-align: left;
}

.markdown-body :deep(th) {
  background: #FAFAFA;
  font-weight: 600;
}

.markdown-body :deep(code) {
  background: #F5F7FA;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
}

.markdown-body :deep(pre) {
  background: #F5F7FA;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin-bottom: 16px;
}

.markdown-body :deep(pre code) {
  background: transparent;
  padding: 0;
}

.markdown-body :deep(a) {
  color: #1E5EB8;
}

.markdown-body :deep(.highlight) {
  background: #FFF7E6;
  padding: 2px 4px;
  border-radius: 2px;
}

/* 响应式 */
@media (max-width: 900px) {
  .doc-sidebar {
    display: none;
  }
}
</style>
