/**
 * Vue 应用入口文件
 * 
 * 企业项目管理系统
 * https://github.com/element-plus/element-plus
 */

import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

// 样式
import 'element-plus/dist/index.css'
import './styles/element-variables.scss'
import './styles/index.css'

// 路由
import router from './router'

// Pinia 状态管理
import { createPinia } from 'pinia'

// 应用
import App from './App.vue'

// 创建应用
const app = createApp(App)

// 使用插件
app.use(ElementPlus, { locale: zhCn })
app.use(createPinia())
app.use(router)

// 挂载
app.mount('#app')

// 开发环境热更新
if (import.meta.hot) {
  import.meta.hot.accept(() => {
    window.location.reload()
  })
}
