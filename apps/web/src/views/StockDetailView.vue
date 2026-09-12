<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const symbol = computed(() => route.params.symbol as string)

// Mock data — will be replaced with real API in WP-02/03
const stock = computed(() => ({
  symbol: symbol.value,
  name: '强瑞技术',
  price: 45.67,
  change: '+2.34',
  changePercent: '+5.4%',
  healthScore: 78,
}))
</script>

<template>
  <div class="stock-detail">
    <div class="stock-hero">
      <div class="ticker">
        <strong>{{ stock.name }}</strong>
        <span>{{ stock.symbol }}</span>
      </div>
      <div class="price-section">
        <span class="price">{{ stock.price }}</span>
        <span class="change up">{{ stock.change }} ({{ stock.changePercent }})</span>
      </div>
      <div class="health-section">
        <div class="health-item">
          <strong>{{ stock.healthScore }}%</strong>
          <span>Thesis 健康度</span>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">标的详情</div>
      <p class="text-muted">
        标的详情页将在 WP-02 (Instrument + Watchlist) 和 WP-03 (Research Package) 中实现。
        WP-01 仅建立路由骨架。
      </p>
    </div>
  </div>
</template>

<style scoped>
.stock-detail {
  max-width: 900px;
  margin: 0 auto;
}

.stock-hero {
  display: flex;
  align-items: center;
  gap: 20px;
  background: #fff;
  border: 1px solid #e8e5ee;
  border-radius: 14px;
  padding: 16px 20px;
  margin-bottom: 16px;
}

.ticker strong {
  font-size: 18px;
  color: #1d1a29;
}

.ticker span {
  display: block;
  font-size: 11px;
  color: #9994a6;
}

.price-section {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.price {
  font-size: 24px;
  font-weight: 800;
  color: #1d1a29;
}

.change {
  font-size: 12px;
  font-weight: 700;
}

.change.up {
  color: #dc5363;
}

.change.down {
  color: #158967;
}

.health-section {
  margin-left: auto;
}

.health-item {
  text-align: center;
}

.health-item strong {
  display: block;
  font-size: 18px;
  color: #4d409f;
}

.health-item span {
  font-size: 10px;
  color: #9994a6;
}
</style>
