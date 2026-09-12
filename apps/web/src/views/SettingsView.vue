<script setup lang="ts">
import { ref } from 'vue'
import { getHealth, dispatchHealthCheckTask, TaskDispatchResponse } from '@/api/client'

const taskResult = ref<TaskDispatchResponse | null>(null)
const apiVersion = ref('loading...')

async function checkApi() {
  const health = await getHealth()
  apiVersion.value = health.version
}

async function runWorkerTask() {
  taskResult.value = await dispatchHealthCheckTask()
}

checkApi()
</script>

<template>
  <div class="settings">
    <div class="page-header">
      <h2>设置</h2>
      <p class="text-muted">系统配置与 WP-01 验收工具</p>
    </div>

    <div class="card">
      <div class="card-title">API 连接</div>
      <p>API 版本: <strong>{{ apiVersion }}</strong></p>
    </div>

    <div class="card">
      <div class="card-title">Worker 测试</div>
      <p class="text-muted">
        点击下方按钮投递一个测试任务到 Worker。如果 Worker 正常运行，任务将被消费。
      </p>
      <button class="btn btn-primary" @click="runWorkerTask">
        投递 Health Check 任务
      </button>
      <div v-if="taskResult" class="task-result">
        <pre>{{ JSON.stringify(taskResult, null, 2) }}</pre>
      </div>
    </div>

    <div class="card">
      <div class="card-title">WP-01 验收清单</div>
      <ul class="checklist">
        <li>Docker Compose 全部服务启动</li>
        <li>Web 可以访问 (http://localhost:5173)</li>
        <li>GET /api/v1/system/status 返回正常</li>
        <li>alembic upgrade head 成功</li>
        <li>Backend tests 全部通过</li>
        <li>Frontend typecheck/lint 通过</li>
        <li>Worker 测试任务消费成功</li>
        <li>重启 Docker Compose 后系统仍能正常工作</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.settings {
  max-width: 700px;
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

.card {
  margin-bottom: 16px;
}

.card p {
  font-size: 12px;
  color: #625e70;
  margin: 0 0 12px;
}

.task-result {
  margin-top: 12px;
  padding: 12px;
  background: #f8f7fa;
  border-radius: 8px;
}

.task-result pre {
  margin: 0;
  font-size: 11px;
  color: #302945;
  white-space: pre-wrap;
}

.checklist {
  list-style: none;
  padding: 0;
  margin: 8px 0 0;
}

.checklist li {
  padding: 6px 0;
  font-size: 12px;
  color: #625e70;
}

.checklist li::before {
  content: '○ ';
  color: #9994a6;
}
</style>
