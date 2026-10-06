<script setup lang="ts">
/**
 * 知识库页面。
 * 核心交互：
 * 1. 创建/查看知识库，分页文档列表，分类和公司筛选
 * 2. 上传文件并填写来源信息；显示排队、处理中、成功、失败及重试状态
 * 3. 在指定范围检索，展示摘录、来源、定位及未核验/部分结果等提示
 * 4. 确认退役文档，退役后新检索不再使用，但历史引用仍能解释
 */

import { computed, onMounted, ref, watch } from 'vue'
import {
  type KnowledgeBase,
  type KnowledgeDocument,
  type KnowledgeSearchResponse,
  type KnowledgeSearchResult,
  createKnowledgeBase,
  listKnowledgeBases,
  listKnowledgeDocuments,
  retireKnowledgeDocument,
  searchKnowledge,
  submitKnowledgeDocument,
  uploadKnowledgeDocument,
} from '@/api/client'

const bases = ref<KnowledgeBase[]>([])
const selectedBaseId = ref<string | null>(null)
const documents = ref<KnowledgeDocument[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const activeTab = ref('bases')

// Create form
const newBaseName = ref('')
const newBaseDescription = ref('')
const newBaseCategory = ref('COMPANY_INDUSTRY')
const creating = ref(false)

// Upload
const uploadFile = ref<File | null>(null)
const uploadTitle = ref('')
const uploading = ref(false)
const uploadSuccess = ref<string | null>(null)

// Search
const searchQuery = ref('')
const searchResults = ref<KnowledgeSearchResponse | null>(null)
const searching = ref(false)

const categoryLabels: Record<string, string> = {
  TRADING_METHOD: '交易方法',
  COMPANY_INDUSTRY: '公司/行业资料',
  POLICY_DOCUMENT: '政策资料',
  PERSONAL_REVIEW: '个人复盘',
}

const statusLabels: Record<string, string> = {
  PENDING: '排队中',
  SUBMITTING: '提交中',
  PROCESSING: '解析中',
  READY: '可检索',
  FAILED: '失败',
  RETIRED: '已退役',
}

const statusClass: Record<string, string> = {
  PENDING: 'status-pending',
  SUBMITTING: 'status-submitting',
  PROCESSING: 'status-processing',
  READY: 'status-ready',
  FAILED: 'status-failed',
  RETIRED: 'status-retired',
}

const selectedBase = computed(() =>
  bases.value.find((b) => b.id === selectedBaseId.value) ?? null,
)

function errorMessage(e: unknown): string {
  if (e && typeof e === 'object' && 'response' in e) {
    const resp = (e as { response?: { data?: { detail?: { message?: string } } } }).response
    return resp?.data?.detail?.message ?? '请求失败'
  }
  return e instanceof Error ? e.message : '请求失败'
}

async function fetchBases(): Promise<void> {
  loading.value = true
  error.value = null
  try {
    bases.value = await listKnowledgeBases()
    if (bases.value.length > 0 && !selectedBaseId.value) {
      selectedBaseId.value = bases.value[0].id
    }
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}

async function fetchDocuments(): Promise<void> {
  if (!selectedBaseId.value) return
  try {
    documents.value = await listKnowledgeDocuments(selectedBaseId.value)
  } catch (e) {
    error.value = errorMessage(e)
  }
}

async function handleCreateBase(): Promise<void> {
  if (!newBaseName.value.trim()) return
  creating.value = true
  error.value = null
  try {
    const kb = await createKnowledgeBase({
      name: newBaseName.value.trim(),
      description: newBaseDescription.value.trim() || undefined,
      category: newBaseCategory.value,
    })
    newBaseName.value = ''
    newBaseDescription.value = ''
    await fetchBases()
    selectedBaseId.value = kb.id
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    creating.value = false
  }
}

async function handleUpload(): Promise<void> {
  if (!uploadFile.value || !selectedBaseId.value) return
  uploading.value = true
  error.value = null
  uploadSuccess.value = null
  try {
    await uploadKnowledgeDocument(selectedBaseId.value, uploadFile.value, {
      title: uploadTitle.value || undefined,
    })
    uploadSuccess.value = '文件上传成功'
    uploadFile.value = null
    uploadTitle.value = ''
    const fileInput = document.getElementById('file-input') as HTMLInputElement | null
    if (fileInput) fileInput.value = ''
    await fetchDocuments()
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    uploading.value = false
  }
}

async function handleSubmit(doc: KnowledgeDocument): Promise<void> {
  error.value = null
  try {
    await submitKnowledgeDocument(doc.id, `submit-${doc.id}-${Date.now()}`)
    await fetchDocuments()
  } catch (e) {
    error.value = errorMessage(e)
  }
}

async function handleRetire(doc: KnowledgeDocument): Promise<void> {
  error.value = null
  try {
    await retireKnowledgeDocument(doc.id)
    await fetchDocuments()
  } catch (e) {
    error.value = errorMessage(e)
  }
}

async function handleSearch(): Promise<void> {
  if (!searchQuery.value.trim()) return
  searching.value = true
  error.value = null
  try {
    searchResults.value = await searchKnowledge({
      query: searchQuery.value.trim(),
      knowledge_base_ids: selectedBaseId.value ? [selectedBaseId.value] : undefined,
      limit: 10,
    })
  } catch (e) {
    error.value = errorMessage(e)
    searchResults.value = null
  } finally {
    searching.value = false
  }
}

function onFileChange(event: Event): void {
  const target = event.target as HTMLInputElement
  uploadFile.value = target.files?.[0] ?? null
}

watch(selectedBaseId, () => {
  fetchDocuments()
})

onMounted(() => {
  fetchBases()
})
</script>

<template>
  <div class="knowledge-view">
    <!-- Tab navigation -->
    <div class="tabs">
      <button
        class="tab"
        :class="{ active: activeTab === 'bases' }"
        @click="activeTab = 'bases'"
      >
        知识库
      </button>
      <button
        class="tab"
        :class="{ active: activeTab === 'search' }"
        @click="activeTab = 'search'"
      >
        检索
      </button>
    </div>

    <!-- Error banner -->
    <div v-if="error" class="error-banner">
      {{ error }}
      <button class="error-dismiss" @click="error = null">×</button>
    </div>

    <!-- ====== Bases Tab ====== -->
    <div v-if="activeTab === 'bases'">
      <!-- Create form -->
      <section class="card create-card">
        <h3>创建知识库</h3>
        <div class="form-row">
          <input
            v-model="newBaseName"
            class="input"
            placeholder="名称"
            maxlength="256"
          />
          <select v-model="newBaseCategory" class="input select">
            <option v-for="(label, key) in categoryLabels" :key="key" :value="key">
              {{ label }}
            </option>
          </select>
        </div>
        <textarea
          v-model="newBaseDescription"
          class="input textarea"
          placeholder="描述（可选）"
          rows="2"
        />
        <button class="btn btn-primary" :disabled="creating || !newBaseName.trim()" @click="handleCreateBase">
          {{ creating ? '创建中...' : '创建' }}
        </button>
      </section>

      <!-- Loading -->
      <div v-if="loading" class="loading">加载中...</div>

      <!-- Empty -->
      <div v-else-if="bases.length === 0" class="empty-state">
        <p>暂无知识库。创建一个开始使用知识检索功能。</p>
        <p class="hint">上传资料后，论衡会调用 WeKnora 进行解析和索引。</p>
      </div>

      <!-- Base list + documents -->
      <div v-else class="bases-layout">
        <section class="card bases-list">
          <h3>知识库列表</h3>
          <ul>
            <li
              v-for="kb in bases"
              :key="kb.id"
              class="base-item"
              :class="{ selected: kb.id === selectedBaseId }"
              @click="selectedBaseId = kb.id"
            >
              <div class="base-name">{{ kb.name }}</div>
              <div class="base-meta">
                <span class="badge">{{ categoryLabels[kb.category] ?? kb.category }}</span>
                <span class="badge status">{{ kb.status }}</span>
                <span class="count">{{ kb.document_count }} 文档</span>
              </div>
            </li>
          </ul>
        </section>

        <section class="card documents-card" v-if="selectedBase">
          <div class="documents-header">
            <h3>{{ selectedBase.name }} — 文档</h3>
            <div class="upload-area">
              <input
                id="file-input"
                type="file"
                @change="onFileChange"
                accept=".pdf,.txt,.md,.docx,.html"
              />
              <input
                v-model="uploadTitle"
                class="input"
                placeholder="标题（可选）"
              />
              <button
                class="btn btn-primary"
                :disabled="uploading || !uploadFile"
                @click="handleUpload"
              >
                {{ uploading ? '上传中...' : '上传' }}
              </button>
            </div>
          </div>
          <div v-if="uploadSuccess" class="success-msg">{{ uploadSuccess }}</div>

          <div v-if="documents.length === 0" class="empty-state small">
            该知识库暂无文档。
          </div>

          <table v-else class="doc-table">
            <thead>
              <tr>
                <th>标题</th>
                <th>大小</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doc in documents" :key="doc.id">
                <td class="doc-title">{{ doc.title }}</td>
                <td>{{ (doc.file_size_bytes / 1024).toFixed(1) }} KB</td>
                <td>
                  <span class="status-badge" :class="statusClass[doc.processing_status]">
                    {{ statusLabels[doc.processing_status] ?? doc.processing_status }}
                  </span>
                </td>
                <td class="doc-actions">
                  <button
                    v-if="doc.processing_status === 'PENDING'"
                    class="btn btn-small"
                    @click="handleSubmit(doc)"
                  >
                    提交处理
                  </button>
                  <button
                    v-if="doc.processing_status === 'FAILED'"
                    class="btn btn-small"
                    @click="handleSubmit(doc)"
                  >
                    重试
                  </button>
                  <button
                    v-if="doc.processing_status !== 'RETIRED'"
                    class="btn btn-small btn-danger"
                    @click="handleRetire(doc)"
                  >
                    退役
                  </button>
                  <span v-if="doc.last_error" class="error-hint" :title="doc.last_error">
                    ⚠ {{ doc.last_error }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </section>
      </div>
    </div>

    <!-- ====== Search Tab ====== -->
    <div v-if="activeTab === 'search'">
      <section class="card search-card">
        <h3>知识检索</h3>
        <div class="search-bar">
          <input
            v-model="searchQuery"
            class="input search-input"
            placeholder="输入检索词..."
            @keyup.enter="handleSearch"
          />
          <button class="btn btn-primary" :disabled="searching || !searchQuery.trim()" @click="handleSearch">
            {{ searching ? '检索中...' : '检索' }}
          </button>
        </div>
        <p class="search-hint">
          检索结果为原文摘录，不自动成为核验证据。上游 chunk_id 仅辅助追踪，不可冒充论衡引用。
        </p>
      </section>

      <div v-if="searchResults" class="search-results">
        <div class="results-header">
          <span>状态: {{ searchResults.status }}</span>
          <span v-if="searchResults.warnings.length > 0" class="warnings">
            <span v-for="(w, i) in searchResults.warnings" :key="i">⚠ {{ w }}</span>
          </span>
        </div>

        <div v-if="searchResults.results.length === 0" class="empty-state">
          <p>未找到匹配结果。</p>
          <p v-if="searchResults.status === 'NOT_CONFIGURED'" class="hint">
            WeKnora 知识服务未配置。请设置 WEKNORA_ENABLED=true 和 WEKNORA_HOST。
          </p>
        </div>

        <div
          v-for="result in searchResults.results"
          :key="result.ref_id"
          class="result-item card"
        >
          <div class="result-header">
            <span class="result-title">{{ result.title }}</span>
            <span class="result-score">{{ result.score_type }}: {{ result.score.toFixed(3) }}</span>
          </div>
          <p class="result-excerpt">{{ result.excerpt }}</p>
          <div class="result-meta">
            <span>引用: {{ result.ref_id }}</span>
            <span v-if="result.source_document_version_id">来源版本: {{ result.source_document_version_id }}</span>
            <span v-if="result.provider_document_id">上游文档: {{ result.provider_document_id }}</span>
            <span v-if="result.chunk_id">分块: {{ result.chunk_id }}</span>
            <span>定位精度: {{ result.locator_precision }}</span>
          </div>
          <div v-if="result.warnings.length > 0" class="result-warnings">
            <span v-for="(w, i) in result.warnings" :key="i">⚠ {{ w }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.knowledge-view {
  max-width: 1100px;
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.tab {
  padding: 8px 20px;
  border: 1px solid #e8e5ee;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
  color: #625e70;
  transition: all 0.15s;
}

.tab.active {
  background: #302945;
  color: #fff;
  border-color: #302945;
}

.card {
  background: #fff;
  border: 1px solid #e8e5ee;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
}

.card h3 {
  margin: 0 0 12px;
  font-size: 15px;
  color: #1d1a29;
}

.create-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-row {
  display: flex;
  gap: 10px;
}

.input {
  padding: 8px 12px;
  border: 1px solid #e8e5ee;
  border-radius: 8px;
  font-size: 13px;
  flex: 1;
}

.input.textarea {
  resize: vertical;
}

.input.select {
  flex: 0 0 180px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: opacity 0.15s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #302945;
  color: #fff;
}

.btn-small {
  padding: 4px 10px;
  font-size: 12px;
  background: #f4f1fa;
  color: #302945;
}

.btn-danger {
  background: #fef2f2;
  color: #dc2626;
}

.error-banner {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: 10px 14px;
  border-radius: 8px;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.error-dismiss {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #991b1b;
}

.loading, .empty-state {
  text-align: center;
  padding: 40px;
  color: #9994a6;
}

.empty-state.small {
  padding: 20px;
}

.hint {
  font-size: 12px;
  color: #9994a6;
  margin-top: 8px;
}

.bases-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 16px;
  align-items: start;
}

.bases-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.base-item {
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
  margin-bottom: 4px;
}

.base-item:hover {
  background: #f4f1fa;
}

.base-item.selected {
  background: #f4f1fa;
  border: 1px solid #d4cfe6;
}

.base-name {
  font-weight: 600;
  font-size: 13px;
  color: #1d1a29;
  margin-bottom: 6px;
}

.base-meta {
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
}

.badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  background: #f4f1fa;
  color: #625e70;
}

.badge.status {
  background: #e8e5ee;
  color: #302945;
}

.count {
  font-size: 11px;
  color: #9994a6;
}

.documents-header {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.upload-area {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.upload-area input[type="file"] {
  font-size: 12px;
}

.success-msg {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  margin-bottom: 10px;
}

.doc-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.doc-table th {
  text-align: left;
  padding: 8px;
  border-bottom: 1px solid #e8e5ee;
  color: #9994a6;
  font-weight: 600;
}

.doc-table td {
  padding: 8px;
  border-bottom: 1px solid #f4f1fa;
}

.doc-title {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
}

.status-pending { background: #fef3c7; color: #92400e; }
.status-submitting { background: #dbeafe; color: #1e40af; }
.status-processing { background: #e0e7ff; color: #3730a3; }
.status-ready { background: #d1fae5; color: #065f46; }
.status-failed { background: #fee2e2; color: #991b1b; }
.status-retired { background: #f3f4f6; color: #6b7280; }

.doc-actions {
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
}

.error-hint {
  font-size: 11px;
  color: #dc2626;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.search-card {
  margin-bottom: 16px;
}

.search-bar {
  display: flex;
  gap: 10px;
}

.search-input {
  flex: 1;
}

.search-hint {
  margin-top: 8px;
  font-size: 11px;
  color: #9994a6;
}

.results-header {
  font-size: 12px;
  color: #625e70;
  margin-bottom: 12px;
  display: flex;
  gap: 16px;
  align-items: center;
}

.warnings {
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: #dc2626;
}

.result-item {
  margin-bottom: 12px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.result-title {
  font-weight: 600;
  font-size: 14px;
  color: #1d1a29;
}

.result-score {
  font-size: 11px;
  color: #6c57dc;
  font-weight: 600;
}

.result-excerpt {
  font-size: 13px;
  color: #374151;
  line-height: 1.6;
  margin: 0 0 8px;
}

.result-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 11px;
  color: #9994a6;
}

.result-warnings {
  margin-top: 6px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 11px;
  color: #dc2626;
}
</style>
