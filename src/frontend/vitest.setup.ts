// Vitest 测试初始化配置
import { config } from '@vue/test-utils'
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import 'element-plus/dist/index.css'

// 全局注册 Element Plus 组件
const app = createApp({})
app.use(ElementPlus)

// 注册所有图标组件
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 配置 Vue Test Utils
config.global.components = {
  ...config.global.components,
  'ElRow': ElementPlus.ElRow,
  'ElCol': ElementPlus.ElCol,
  'ElButton': ElementPlus.ElButton,
  'ElInput': ElementPlus.ElInput,
  'ElForm': ElementPlus.ElForm,
  'ElFormItem': ElementPlus.ElFormItem,
  'ElTable': ElementPlus.ElTable,
  'ElTableColumn': ElementPlus.ElTableColumn,
  'ElDialog': ElementPlus.ElDialog,
  'ElSelect': ElementPlus.ElSelect,
  'ElOption': ElementPlus.ElOption,
  'ElPagination': ElementPlus.ElPagination,
  'ElProgress': ElementPlus.ElProgress,
  'ElTag': ElementPlus.ElTag,
  'ElDropdown': ElementPlus.ElDropdown,
  'ElDropdownMenu': ElementPlus.ElDropdownMenu,
  'ElDropdownItem': ElementPlus.ElDropdownItem,
  'ElAvatar': ElementPlus.ElAvatar,
  'ElIcon': ElementPlus.ElIcon,
  'ElBadge': ElementPlus.ElBadge,
  'ElCard': ElementPlus.ElCard,
  'ElTabs': ElementPlus.ElTabs,
  'ElTabPane': ElementPlus.ElTabPane,
  'ElAlert': ElementPlus.ElAlert,
  'ElMessage': ElementPlus.ElMessage,
  'ElMessageBox': ElementPlus.ElMessageBox,
  'ElLoading': ElementPlus.ElLoading,
  'ElTooltip': ElementPlus.ElTooltip,
  'ElPopover': ElementPlus.ElPopover,
  'ElDrawer': ElementPlus.ElDrawer,
  'ElRadioGroup': ElementPlus.ElRadioGroup,
  'ElRadioButton': ElementPlus.ElRadioButton,
  'ElCheckbox': ElementPlus.ElCheckbox,
  'ElCheckboxGroup': ElementPlus.ElCheckboxGroup,
  'ElSwitch': ElementPlus.ElSwitch,
  'ElDatePicker': ElementPlus.ElDatePicker,
  'ElTimePicker': ElementPlus.ElTimePicker,
  'ElUpload': ElementPlus.ElUpload,
  'ElImage': ElementPlus.ElImage,
  'ElCarousel': ElementPlus.ElCarousel,
  'ElCarouselItem': ElementPlus.ElCarouselItem,
  'ElSteps': ElementPlus.ElSteps,
  'ElStep': ElementPlus.ElStep,
  'ElRate': ElementPlus.ElRate,
  'ElSlider': ElementPlus.ElSlider,
  'ElColorPicker': ElementPlus.ElColorPicker,
  'ElTransfer': ElementPlus.ElTransfer,
  'ElTree': ElementPlus.ElTree,
  'ElCascader': ElementPlus.ElCascader,
  'ElBreadcrumb': ElementPlus.ElBreadcrumb,
  'ElBreadcrumbItem': ElementPlus.ElBreadcrumbItem,
  'ElPageHeader': ElementPlus.ElPageHeader,
  'ElBacktop': ElementPlus.ElBacktop,
  'ElInfiniteScroll': ElementPlus.ElInfiniteScroll,
  'ElAutocomplete': ElementPlus.ElAutocomplete,
  'ElInputNumber': ElementPlus.ElInputNumber,
  'ElSelectV2': ElementPlus.ElSelectV2,
  'ElTreeSelect': ElementPlus.ElTreeSelect,
  'ElVirtualList': ElementPlus.ElVirtualList,
  'ElText': ElementPlus.ElText,
  'ElLink': ElementPlus.ElLink,
  'ElDivider': ElementPlus.ElDivider,
  'ElSkeleton': ElementPlus.ElSkeleton,
  'ElEmpty': ElementPlus.ElEmpty,
  'ElResult': ElementPlus.ElResult,
  'ElPopconfirm': ElementPlus.ElPopconfirm,
  'ElTimeline': ElementPlus.ElTimeline,
  'ElTimelineItem': ElementPlus.ElTimelineItem,
  'ElWatermark': ElementPlus.ElWatermark,
  'ElAffix': ElementPlus.ElAffix,
  'ElConfigProvider': ElementPlus.ElConfigProvider,
  'ElSpace': ElementPlus.ElSpace,
  'ElStatistic': ElementPlus.ElStatistic,
  'ElDescriptions': ElementPlus.ElDescriptions,
  'ElDescriptionsItem': ElementPlus.ElDescriptionsItem,
  'ElDynamicInput': ElementPlus.ElDynamicInput,
  'ElQRCode': ElementPlus.ElQRCode,
  'ElCountdown': ElementPlus.ElCountdown,
  'ElImagePreview': ElementPlus.ElImagePreview,
  'ElTour': ElementPlus.ElTour,
  'ElTourStep': ElementPlus.ElTourStep,
  'ElCalendar': ElementPlus.ElCalendar
}