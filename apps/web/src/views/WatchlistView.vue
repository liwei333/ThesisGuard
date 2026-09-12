<script setup lang="ts">
import { ref } from 'vue'

// Mock data for WP-01 — will be replaced with real API calls in WP-02
const watchlistItems = ref([
  {
    symbol: '301128',
    name: '强瑞技术',
    classification: '机构趋势',
    score: 82,
    thesis: 'AI服务器液冷业务进入快速放量周期',
  },
  {
    symbol: '002594',
    name: '比亚迪',
    classification: '机构趋势',
    score: 76,
    thesis: '海外扩张+高端化驱动盈利增长',
  },
])

const classifications = ['全部', '机构趋势', '游资情绪', '混合驱动', '事件驱动']
const activeTab = ref('全部')
</script>

<template>
  <div class="watchlist">
    <div class="page-header">
      <h2>自选池</h2>
      <p class="text-muted">
        标的加入自选后将自动建档、分类并生成 Thesis。WP-01 使用 Mock 数据展示。
      </p>
    </div>

    <div class="tabs">
      <button
        v-for="tab in classifications"
        :key="tab"
        class="tab"
        :class="{ active: activeTab === tab }"
        @click="activeTab = tab"
      >
        {{ tab }}
      </button>
    </div>

    <div class="stock-grid">
      <div v-for="item in watchlistItems" :key="item.symbol" class="card stock-card">
        <div class="stock-header">
          <div class="stock-name">
            <strong>{{ item.name }}</strong>
            <span>{{ item.symbol }}</span>
          </div>
          <div class="stock-score">{{ item.score }}</div>
        </div>
        <div class="thesis">{{ item.thesis }}</div>
        <div class="stock-footer">
          <span class="tag purple">{{ item.classification }}</span>
          <span class="tag green">Thesis Active</span>
        </div>
      </div>

      <div class="card add-card">
        <div class="add-placeholder">
          <span class="add-icon">+</span>
          <p>加入自选</p>
          <span class="text-muted">输入股票代码开始研究</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.watchlist {
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

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.tab {
  border: none;
  background: #ebe8f1;
  color: #777080;
  border-radius: 999px;
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

.stock-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
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

.thesis {
  margin-top: 10px;
  font-size: 12px;
  line-height: 1.5;
  color: #625d6c;
  flex: 1;
}

.stock-footer {
  display: flex;
  gap: 6px;
  margin-top: 12px;
}

.tag {
  display: inline-flex;
  align-items: center;
  padding: 3px 8px;
  border-radius: 999px;
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

.add-card {
  display: grid;
  place-items: center;
  min-height: 146px;
  border: 1px dashed #cfc8dc;
  background: #faf9fc;
  cursor: pointer;
  transition: border-color 0.15s;
}

.add-card:hover {
  border-color: #6c57dc;
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
</style>
