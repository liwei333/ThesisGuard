import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

// 路由配置：所有视图组件使用懒加载，减少首屏体积
// meta.title 用于顶部栏标题展示
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/DashboardView.vue'),
    meta: { title: '总览' },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { title: '仪表盘' },
  },
  {
    path: '/watchlist',
    name: 'watchlist',
    component: () => import('@/views/WatchlistView.vue'),
    meta: { title: '自选池' },
  },
  {
    // 标的详情页，symbol 为路径参数，当前为 Mock 数据骨架
    path: '/stock/:symbol',
    name: 'stock-detail',
    component: () => import('@/views/StockDetailView.vue'),
    meta: { title: '标的详情' },
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/SettingsView.vue'),
    meta: { title: '设置' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
