<template>
  <div class="auth-layout">
    <div class="auth-background">
      <div class="auth-decoration auth-decoration-1"></div>
      <div class="auth-decoration auth-decoration-2"></div>
    </div>
    <div class="auth-card">
      <router-view v-slot="{ Component }">
        <transition name="fade-slide" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
  position: relative;
  overflow: hidden;
}

.auth-background {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.auth-decoration {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
}

.auth-decoration-1 {
  width: 800px;
  height: 800px;
  background: linear-gradient(135deg, #1E5EB8 0%, #4096FF 100%);
  top: -400px;
  right: -200px;
}

.auth-decoration-2 {
  width: 600px;
  height: 600px;
  background: linear-gradient(135deg, #4096FF 0%, #1E5EB8 100%);
  bottom: -300px;
  left: -150px;
}

.auth-card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 400px;
  margin: 16px;
  background: #FFFFFF;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

/* 过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* 响应式 */
@media (max-width: 480px) {
  .auth-card {
    margin: 8px;
    max-width: 100%;
  }
}
</style>
