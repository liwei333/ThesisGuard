<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  addWatchlistItem,
  deleteWatchlistItem,
  listWatchlist,
  searchInstruments,
  type Instrument,
  type WatchlistItem,
} from '@/api/client'

const watchlistItems = ref<WatchlistItem[]>([])
const searchResults = ref<Instrument[]>([])
const activeTab = ref('全部')
const query = ref('301128')
const loading = ref(true)
const adding = ref(false)
const error = ref<string | null>(null)

const classifications = computed(() => {
  const existing = watchlistItems.value.map((item) => item.classification)
  return ['全部', ...Array.from(new Set(existing))]
})

const filteredItems = computed(() => {
  if (activeTab.value === '全部') {
    return watchlistItems.value
  }
  return watchlistItems.value.filter(
    (item) => item.classification === activeTab.value,
  )
})

function displayClassification(classification: string): string {
  const labels: Record<string, string> = {
    INSTITUTIONAL_TREND: '机构趋势',
    HOT_MONEY: '游资情绪',
    HYBRID: '混合驱动',
    EVENT_DRIVEN: '事件驱动',
  }
  return labels[classification] ?? classification
}

function errorMessage(e: unknown): string {
  return e instanceof Error ? e.message : '请求失败'
}

async function fetchWatchlist(): Promise<void> {
  try {
    loading.value = true
    watchlistItems.value = await listWatchlist()
    error.value = null
  } catch (e: unknown) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}

async function runSearch(): Promise<void> {
  if (!query.value.trim()) {
    searchResults.value = []
    return
  }
  try {
    searchResults.value = await searchInstruments(query.value.trim())
    error.value = null
  } catch (e: unknown) {
    error.value = errorMessage(e)
  }
}

async function addToWatchlist(searchQuery = query.value): Promise<void> {
  if (!searchQuery.trim()) {
    return
  }
  try {
    adding.value = true
    const item = await addWatchlistItem(searchQuery.trim())
    const existingIndex = watchlistItems.value.findIndex(
      (entry) => entry.id === item.id,
    )
    if (existingIndex >= 0) {
      watchlistItems.value[existingIndex] = item
    } else {
      watchlistItems.value.unshift(item)
    }
    query.value = item.instrument.symbol
    await runSearch()
    error.value = null
  } catch (e: unknown) {
    error.value = errorMessage(e)
  } finally {
    adding.value = false
  }
}

async function removeItem(item: WatchlistItem): Promise<void> {
  await deleteWatchlistItem(item.id)
  watchlistItems.value = watchlistItems.value.filter(
    (entry) => entry.id !== item.id,
  )
}

onMounted(async () => {
  await Promise.all([fetchWatchlist(), runSearch()])
})
</script>

<template>
  <div class="watchlist">
    <div class="page-header">
      <div>
        <h2>自选池</h2>
        <p class="text-muted">
          输入代码或名称，系统识别标的、自动分类，并写入可持续维护的研究队列。
        </p>
      </div>
      <form
        class="add-form"
        @submit.prevent="addToWatchlist()"
      >
        <input
          v-model="query"
          type="search"
          placeholder="301128 / 强瑞技术"
          @input="runSearch"
        >
        <button
          class="btn primary"
          type="submit"
          :disabled="adding"
        >
          {{ adding ? '加入中' : '加入自选' }}
        </button>
      </form>
    </div>

    <div
      v-if="searchResults.length"
      class="search-strip"
    >
      <button
        v-for="instrument in searchResults"
        :key="instrument.id"
        class="search-result"
        @click="addToWatchlist(instrument.symbol)"
      >
        <strong>{{ instrument.name }}</strong>
        <span>{{ instrument.symbol }} · {{ instrument.exchange }}</span>
      </button>
    </div>

    <div
      v-if="error"
      class="error-card"
    >
      {{ error }}
    </div>

    <div class="tabs">
      <button
        v-for="tab in classifications"
        :key="tab"
        class="tab"
        :class="{ active: activeTab === tab }"
        @click="activeTab = tab"
      >
        {{ displayClassification(tab) }}
      </button>
    </div>

    <div
      v-if="loading"
      class="loading"
    >
      加载中...
    </div>

    <div
      v-else
      class="stock-grid"
    >
      <div
        v-for="item in filteredItems"
        :key="item.id"
        class="card stock-card"
      >
        <div class="stock-header">
          <div class="stock-name">
            <strong>{{ item.instrument.name }}</strong>
            <span>{{ item.instrument.symbol }} · {{ item.instrument.exchange }}</span>
          </div>
          <div class="stock-score">
            {{ item.research_score ?? item.classification_confidence }}
          </div>
        </div>
        <div class="thesis">
          {{ item.thesis_summary }}
        </div>
        <div class="classification-reason">
          {{ item.classification_reason }}
        </div>
        <div class="stock-footer">
          <span class="tag purple">{{ displayClassification(item.classification) }}</span>
          <span class="tag green">Research {{ item.research_status }}</span>
        </div>
        <div class="stock-actions">
          <span>{{ item.agent_action }}</span>
          <button
            class="text-btn"
            @click="removeItem(item)"
          >
            移除
          </button>
        </div>
      </div>

      <div
        v-if="!filteredItems.length"
        class="card add-card"
      >
        <div class="add-placeholder">
          <span class="add-icon">+</span>
          <p>加入 301128</p>
          <span class="text-muted">验证证券识别、分类和 Research ACTIVE 状态</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.watchlist {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
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

.add-form {
  display: flex;
  gap: 8px;
  min-width: 320px;
}

.add-form input {
  min-width: 0;
  flex: 1;
  border: 1px solid #ded9e8;
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 12px;
  color: #302a3f;
  background: #fff;
}

.search-strip {
  display: flex;
  gap: 8px;
  margin-bottom: 14px;
  overflow-x: auto;
}

.search-result {
  border: 1px solid #e3deec;
  background: #fff;
  border-radius: 8px;
  padding: 8px 10px;
  text-align: left;
  cursor: pointer;
  min-width: 160px;
}

.search-result strong,
.search-result span {
  display: block;
}

.search-result strong {
  color: #241f31;
  font-size: 12px;
}

.search-result span {
  margin-top: 2px;
  color: #8c849a;
  font-size: 11px;
}

.error-card {
  border: 1px solid #f2c6ce;
  background: #fff6f8;
  color: #bd4056;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 12px;
  margin-bottom: 12px;
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.tab {
  border: none;
  background: #ebe8f1;
  color: #777080;
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.tab.active {
  background: #312a43;
  color: #fff;
}

.loading {
  padding: 40px;
  text-align: center;
  color: #9994a6;
}

.stock-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.stock-card {
  display: flex;
  flex-direction: column;
}

.stock-header {
  display: flex;
  align-items: flex-start;
}

.stock-name strong {
  display: block;
  font-size: 14px;
  color: #1d1a29;
}

.stock-name span {
  font-size: 11px;
  color: #9994a6;
}

.stock-score {
  margin-left: auto;
  font-size: 20px;
  font-weight: 800;
  color: #4d409f;
}

.thesis,
.classification-reason {
  margin-top: 10px;
  font-size: 12px;
  line-height: 1.5;
  color: #625d6c;
}

.classification-reason {
  color: #827b90;
}

.stock-footer,
.stock-actions {
  display: flex;
  gap: 6px;
  margin-top: 12px;
  align-items: center;
}

.stock-actions {
  justify-content: space-between;
  font-size: 11px;
  color: #6c6478;
}

.tag {
  display: inline-flex;
  align-items: center;
  padding: 3px 8px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 700;
}

.tag.purple {
  background: #ede8fb;
  color: #5d49c8;
}

.tag.green {
  background: #e6f7f1;
  color: #16805e;
}

.text-btn {
  border: none;
  background: transparent;
  color: #6c57dc;
  cursor: pointer;
  font-size: 11px;
  font-weight: 700;
}

.add-card {
  display: grid;
  place-items: center;
  min-height: 178px;
  border: 1px dashed #cfc8dc;
  background: #faf9fc;
}

.add-placeholder {
  text-align: center;
}

.add-icon {
  font-size: 24px;
  color: #9994a6;
}

.add-placeholder p {
  font-size: 13px;
  color: #5e586a;
  margin: 8px 0 4px;
}

@media (max-width: 720px) {
  .page-header,
  .add-form {
    flex-direction: column;
  }

  .add-form {
    min-width: 0;
  }
}
</style>
