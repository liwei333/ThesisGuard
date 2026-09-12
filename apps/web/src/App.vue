<script setup lang="ts">
import { RouterView, RouterLink, useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()

const navItems = [
  { path: '/', label: '总览', icon: '◫' },
  { path: '/dashboard', label: '仪表盘', icon: '◰' },
  { path: '/watchlist', label: '自选', icon: '☆' },
  { path: '/settings', label: '设置', icon: '⚙' },
]

const isActive = (path: string) => computed(() => route.path === path)
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-logo">论</div>
        <div class="brand-text">
          <span class="brand-name">ThesisGuard</span>
          <span class="brand-tag">论衡</span>
        </div>
      </div>
      <nav class="nav">
        <RouterLink
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path).value }"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </RouterLink>
      </nav>
      <div class="sidebar-footer">
        <span class="status-dot ok"></span>
        <span class="status-text">系统运行中</span>
      </div>
    </aside>
    <main class="main-content">
      <header class="topbar">
        <div class="topbar-title">
          <h1>{{ (route.meta?.title as string) || 'ThesisGuard' }}</h1>
        </div>
        <div class="topbar-actions">
          <span class="api-status" title="API Status">● API Online</span>
        </div>
      </header>
      <div class="workspace">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  display: grid;
  grid-template-columns: 220px 1fr;
  height: 100vh;
  background: #f8f7fb;
}

.sidebar {
  display: flex;
  flex-direction: column;
  background: #fff;
  border-right: 1px solid #e8e5ee;
  padding: 20px 16px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 32px;
}

.brand-logo {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(145deg, #302945, #6c57dc);
  color: #fff;
  font-weight: 800;
  font-size: 18px;
  display: grid;
  place-items: center;
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-size: 14px;
  font-weight: 700;
  color: #1d1a29;
}

.brand-tag {
  font-size: 11px;
  color: #9994a6;
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 10px;
  color: #625e70;
  font-size: 13px;
  text-decoration: none;
  transition: background 0.15s;
}

.nav-item:hover {
  background: #f4f1fa;
  color: #302945;
}

.nav-item.active {
  background: #302945;
  color: #fff;
}

.nav-icon {
  font-size: 16px;
}

.sidebar-footer {
  margin-top: auto;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 0;
  font-size: 11px;
  color: #9994a6;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.ok {
  background: #1ca77b;
  box-shadow: 0 0 0 4px rgba(28, 167, 123, 0.15);
}

.main-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.topbar {
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #e8e5ee;
  display: flex;
  align-items: center;
  padding: 0 24px;
  flex-shrink: 0;
}

.topbar-title h1 {
  font-size: 16px;
  font-weight: 700;
  color: #1d1a29;
  margin: 0;
}

.topbar-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
}

.api-status {
  font-size: 11px;
  color: #1ca77b;
  font-weight: 600;
}

.workspace {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}
</style>
