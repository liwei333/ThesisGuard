<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getSystemStatus, SystemStatusResponse } from '@/api/client'

const systemStatus = ref<SystemStatusResponse | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

function errorMessage(e: unknown): string {
  return e instanceof Error ? e.message : 'Failed to fetch system status'
}

async function fetchStatus() {
  try {
    loading.value = true
    systemStatus.value = await getSystemStatus()
    error.value = null
  } catch (e: unknown) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStatus()
})

function statusColor(status: string): string {
  return status === 'ok' ? 'text-success' : 'text-danger'
}
</script>

<template>
  <div class="dashboard">
    <div class="page-header">
      <h2>系统仪表盘</h2>
      <p class="text-muted">
        ThesisGuard 工程骨架 WP-01 验收
      </p>
    </div>

    <div
      v-if="loading"
      class="loading"
    >
      加载中...
    </div>

    <div
      v-else-if="error"
      class="error-card"
    >
      <p class="text-danger">
        {{ error }}
      </p>
      <button
        class="btn"
        @click="fetchStatus"
      >
        重试
      </button>
    </div>

    <div
      v-else-if="systemStatus"
      class="status-grid"
    >
      <div class="card status-card overall">
        <div class="card-title">
          系统状态
        </div>
        <div
          class="status-value"
          :class="statusColor(systemStatus.status)"
        >
          {{ systemStatus.status === 'healthy' ? '运行正常' : '降级' }}
        </div>
        <div class="status-version">
          API v{{ systemStatus.api.version }}
        </div>
      </div>

      <div
        v-for="(service, name) in systemStatus.services"
        :key="name"
        class="card status-card"
      >
        <div class="card-title">
          {{
            name === 'postgres'
              ? 'PostgreSQL'
              : name === 'redis'
                ? 'Redis'
                : name === 'object_storage'
                  ? 'MinIO'
                  : 'Worker'
          }}
        </div>
        <div
          class="status-value"
          :class="statusColor(service.status)"
        >
          {{ service.status === 'ok' ? '正常' : '异常' }}
        </div>
        <div class="status-message text-muted">
          {{ service.message }}
        </div>
      </div>
    </div>

    <div class="card info-card">
      <div class="card-title">
        WP-01 工程骨架
      </div>
      <p class="text-muted">
        本页面通过 API 实时获取系统健康状态。所有服务正常即表示 WP-01 验收通过。
      </p>
      <ul class="checklist">
        <li>Docker Compose 全部服务启动</li>
        <li>FastAPI /api/v1/health 响应</li>
        <li>PostgreSQL 连接正常</li>
        <li>Redis 连接正常</li>
        <li>MinIO Bucket 可访问</li>
        <li>Worker 队列可达</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 4px;
  color: #1d1a29;
}

.page-header p {
  font-size: 12px;
  margin: 0;
}

.loading {
  padding: 40px;
  text-align: center;
  color: #9994a6;
}

.error-card {
  padding: 24px;
  background: #fff;
  border: 1px solid #f9d1d8;
  border-radius: 14px;
  text-align: center;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.status-card {
  text-align: center;
}

.status-value {
  font-size: 24px;
  font-weight: 800;
  margin: 8px 0;
}

.status-version,
.status-message {
  font-size: 11px;
}

.info-card {
  margin-top: 16px;
}

.checklist {
  list-style: none;
  padding: 0;
  margin: 12px 0 0;
}

.checklist li {
  padding: 6px 0;
  font-size: 12px;
  color: #625e70;
}

.checklist li::before {
  content: '✓ ';
  color: #1ca77b;
  font-weight: 700;
}
</style>
