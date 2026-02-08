<template>
  <div class="docs-page">
    <div class="page-header">
      <h1 class="page-title">文档中心</h1>
      <p class="page-desc">企业项目管理系统的各类文档和资源</p>
    </div>

    <!-- 文档分类 -->
    <el-row :gutter="24" class="doc-sections">
      <!-- 用户手册 -->
      <el-col :xs="24" :lg="12">
        <div class="doc-card" @click="openDoc('/docs/manual/2026-02-08-user-manual.md')">
          <div class="doc-icon user-manual">
            <el-icon :size="32"><Reading /></el-icon>
          </div>
          <div class="doc-content">
            <h3 class="doc-title">用户手册</h3>
            <p class="doc-desc">系统使用指南，包括快速入门、各功能模块操作说明</p>
            <div class="doc-meta">
              <el-tag size="small">用户</el-tag>
              <span class="doc-date">2026-02-08</span>
            </div>
          </div>
          <el-icon class="doc-arrow"><ArrowRight /></el-icon>
        </div>
      </el-col>

      <!-- 需求文档 -->
      <el-col :xs="24" :lg="12">
        <div class="doc-card" @click="openDoc('/docs/requirements/2026-02-08-requirements.md')">
          <div class="doc-icon requirements">
            <el-icon :size="32"><Document /></el-icon>
          </div>
          <div class="doc-content">
            <h3 class="doc-title">需求文档</h3>
            <p class="doc-desc">功能需求清单、用户故事、业务流程说明</p>
            <div class="doc-meta">
              <el-tag type="info" size="small">产品</el-tag>
              <span class="doc-date">2026-02-08</span>
            </div>
          </div>
          <el-icon class="doc-arrow"><ArrowRight /></el-icon>
        </div>
      </el-col>

      <!-- UI/UX设计 -->
      <el-col :xs="24" :lg="12">
        <div class="doc-card" @click="openDoc('/docs/plans/2026-02-08-ui-ux-design.md')">
          <div class="doc-icon design">
            <el-icon :size="32"><Edit /></el-icon>
          </div>
          <div class="doc-content">
            <h3 class="doc-title">UI/UX设计</h3>
            <p class="doc-desc">界面设计规范、组件库、页面布局、交互说明</p>
            <div class="doc-meta">
              <el-tag type="warning" size="small">设计</el-tag>
              <span class="doc-date">2026-02-08</span>
            </div>
          </div>
          <el-icon class="doc-arrow"><ArrowRight /></el-icon>
        </div>
      </el-col>

      <!-- API文档 -->
      <el-col :xs="24" :lg="12">
        <div class="doc-card" @click="openApiDoc">
          <div class="doc-icon api">
            <el-icon :size="32"><Connection /></el-icon>
          </div>
          <div class="doc-content">
            <h3 class="doc-title">API文档</h3>
            <p class="doc-desc">接口定义、请求参数、响应格式、错误码说明</p>
            <div class="doc-meta">
              <el-tag type="success" size="small">开发</el-tag>
              <span class="doc-date">2026-02-08</span>
            </div>
          </div>
          <el-icon class="doc-arrow"><ArrowRight /></el-icon>
        </div>
      </el-col>

      <!-- 系统架构 -->
      <el-col :xs="24" :lg="12">
        <div class="doc-card" @click="openDoc('/docs/plans/2026-02-08-project-management-system-design.md')">
          <div class="doc-icon architecture">
            <el-icon :size="32"><Grid /></el-icon>
          </div>
          <div class="doc-content">
            <h3 class="doc-title">系统架构</h3>
            <p class="doc-desc">技术架构、数据库设计、模块划分、技术选型</p>
            <div class="doc-meta">
              <el-tag type="success" size="small">开发</el-tag>
              <span class="doc-date">2026-02-08</span>
            </div>
          </div>
          <el-icon class="doc-arrow"><ArrowRight /></el-icon>
        </div>
      </el-col>

      <!-- 模块设计 -->
      <el-col :xs="24" :lg="12">
        <div class="doc-card" @click="openDoc('/docs/plans/2026-02-08-project-plan-module-design.md')">
          <div class="doc-icon module">
            <el-icon :size="32"><Finished /></el-icon>
          </div>
          <div class="doc-content">
            <h3 class="doc-title">模块设计</h3>
            <p class="doc-desc">项目计划模块的详细设计，包括数据模型、流程设计</p>
            <div class="doc-meta">
              <el-tag type="success" size="small">开发</el-tag>
              <span class="doc-date">2026-02-08</span>
            </div>
          </div>
          <el-icon class="doc-arrow"><ArrowRight /></el-icon>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { Document, Reading, Edit, Connection, Grid, Finished, ArrowRight } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const openDoc = (path) => {
  router.push({ path: '/docs/viewer', query: { path } })
}

const openApiDoc = () => {
  router.push({ path: '/docs/viewer', query: { path: '/docs/api/2026-02-08-api.md' } })
}
</script>

<style scoped>
.docs-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 8px 0;
}

.page-desc {
  font-size: 14px;
  color: #8C8C8C;
  margin: 0;
}

.doc-sections {
  margin-bottom: 32px;
}

.doc-card {
  background: #FFFFFF;
  border: 1px solid #E4E7ED;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 16px;
}

.doc-card:hover {
  border-color: #1E5EB8;
  box-shadow: 0 4px 12px rgba(30, 94, 184, 0.1);
  transform: translateY(-2px);
}

.doc-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.doc-icon.user-manual {
  background: rgba(82, 196, 26, 0.1);
  color: #52C41A;
}

.doc-icon.requirements {
  background: rgba(24, 144, 255, 0.1);
  color: #1890FF;
}

.doc-icon.design {
  background: rgba(114, 46, 209, 0.1);
  color: #722ED1;
}

.doc-icon.api {
  background: rgba(250, 173, 20, 0.1);
  color: #FAAD14;
}

.doc-icon.architecture {
  background: rgba(19, 194, 194, 0.1);
  color: #13C2C2;
}

.doc-icon.module {
  background: rgba(235, 47, 150, 0.1);
  color: #EB2F96;
}

.doc-content {
  flex: 1;
}

.doc-title {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 8px 0;
}

.doc-desc {
  font-size: 13px;
  color: #8C8C8C;
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.doc-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.doc-date {
  font-size: 12px;
  color: #BFBFBF;
}

.doc-arrow {
  color: #8C8C8C;
  font-size: 20px;
  align-self: center;
  transition: color 0.2s;
}

.doc-card:hover .doc-arrow {
  color: #1E5EB8;
}
</style>
