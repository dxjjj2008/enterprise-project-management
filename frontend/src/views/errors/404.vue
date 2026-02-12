<template>
  <div class="error-page">
    <div class="error-content">
      <h1>404</h1>
      <p>页面未找到</p>
      <router-link to="/">
        <el-button type="primary">返回首页</el-button>
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.error-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F5F7FA;
}
.error-content {
  text-align: center;
}
.error-content h1 {
  font-size: 120px;
  font-weight: 700;
  color: #1E5EB8;
  margin-bottom: 16px;
  line-height: 1;
}
.error-content p {
  font-size: 18px;
  color: #595959;
  margin-bottom: 32px;
}
</style>
