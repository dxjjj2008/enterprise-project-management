<template>
  <div class="auth-layout">
    <div class="auth-container">
      <div class="auth-card">
        <router-view />
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #F5F7FA 0%, #E6F4FF 100%);
}

.auth-container {
  width: 100%;
  max-width: 400px;
  padding: 24px;
}

.auth-card {
  background: #FFFFFF;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  padding: 40px;
}
</style>
