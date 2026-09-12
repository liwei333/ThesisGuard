# 论衡 ThesisGuard V1 技术架构设计（TAD）

> 版本：V1.0 Draft  
> 日期：2026-09-12  
> 产品：论衡 ThesisGuard  
> 定位：个人交易研究与决策系统  
> 核心：Build the thesis. Test the thesis. Guard the downside.

---

# 1. 文档目标

本文用于指导 ThesisGuard V1 的工程实现。

本阶段不追求：

- 全自动交易
- 高频量化
- 多券商直接下单
- 复杂多 Agent 自治
- 大规模微服务
- 全市场毫秒级行情
- 替用户“预测涨跌”

本阶段核心目标是将产品原型中的 **Thesis Lifecycle** 真正落地为可运行系统：

```text
发现标的
↓
建立 Thesis
↓
收集事实与机构预期
↓
持续验证 Thesis
↓
发现预期差
↓
Bull / Base / Bear 估值
↓
判断 Price-In
↓
市场风险过滤
↓
制定并冻结交易计划
↓
催化剂持续验证
↓
交易执行记录
↓
复盘
↓
更新个人交易模型
```

---

# 2. 核心设计原则

## 2.1 Thesis 是第一领域对象

系统核心不是 Stock，也不是 Chat Session。

系统核心对象是：

```text
Instrument
  └── Thesis
        ├── ThesisVersion
        ├── Evidence
        ├── CounterEvidence
        ├── ValidationRule
        ├── InvalidationRule
        └── ThesisScoreLedger
```

股票只是 Thesis 的载体。

---

## 2.2 LLM 不是系统事实源

LLM 可以负责：

- 理解
- 摘要
- 分类建议
- 证据关联建议
- 多空辩论
- 解释
- 反驳
- 生成研究初稿

LLM 不直接负责：

- 写最终财务事实
- 计算仓位
- 计算估值
- 修改冻结交易计划
- 修改历史 Thesis
- 决定市场情绪分数
- 直接改数据库

所有最终业务状态必须由确定性 Domain Service 写入。

---

## 2.3 结构化事实优先于 RAG

数据分层：

```text
PostgreSQL
= 最新事实 / 当前状态 / 业务对象 / 评分账本

pgvector
= 语义检索索引

MinIO / S3
= PDF / 公告 / 研报 / 调研纪要 / 原始文件

Redis
= Cache / Queue / Event Stream
```

原则：

> DB 回答“现在是什么”。  
> RAG 回答“为什么”。  
> 原始文件回答“证据原文在哪里”。

---

## 2.4 不可覆盖历史

以下对象全部版本化：

- Thesis
- Trade Plan
- Research Package
- 盈利预测快照
- Bull/Base/Bear 场景
- 用户交易规则
- Agent Prompt

禁止用最新值覆盖历史值。

---

## 2.5 模块化单体优先

V1 使用：

```text
Modular Monolith
```

不拆微服务。

理由：

- 个人项目
- 业务边界仍在演进
- 运维成本需要保持低
- 事件驱动可以先在单体内部完成
- 后续可按热点模块拆分

---

# 3. 推荐技术栈

## 3.1 Web

```text
Vue 3
TypeScript
Vite
Pinia
Vue Router
Axios / Fetch
ECharts（正式产品允许使用）
TradingView Lightweight Charts（K线）
```

原型仍保持纯 HTML。

正式产品建议使用 ECharts，不继续手搓所有 SVG。

---

## 3.2 API

```text
Python 3.12+
FastAPI
Pydantic v2
SQLAlchemy 2
Alembic
```

---

## 3.3 Worker

```text
Python
Dramatiq 或 ARQ
Redis
```

V1 推荐：

```text
Dramatiq + Redis
```

---

## 3.4 Database

```text
PostgreSQL 17
pgvector
```

可选：

```text
TimescaleDB
```

用于：

- 分钟 K 线
- 市场宽度
- 涨跌停数量
- 情绪指标序列

V1 也可以先不启用。

---

## 3.5 Object Storage

```text
MinIO
```

兼容 S3 API。

---

## 3.6 Infrastructure

```text
Docker Compose
Nginx / Caddy
```

开发与个人服务器统一：

```bash
docker compose up -d
```

---

# 4. 总体架构

```text
┌──────────────────────────────────────────────────────┐
│                  ThesisGuard Web                     │
│              Vue3 + TypeScript + Pinia               │
└──────────────────────┬───────────────────────────────┘
                       │
                REST / SSE / WS
                       │
┌──────────────────────▼───────────────────────────────┐
│                ThesisGuard Core API                  │
│                     FastAPI                          │
│                                                     │
│ Instrument     Watchlist       Research             │
│ Thesis         Evidence        Expectation          │
│ Valuation      Price-In        Catalyst             │
│ Portfolio      Trade Plan      Discipline           │
│ Market Regime  Intelligence   Notification         │
│ Agent Runtime / Tool Registry / Policy Layer        │
└───────┬──────────────┬──────────────┬───────────────┘
        │              │              │
        ▼              ▼              ▼
 PostgreSQL        Redis          MinIO / S3
 pgvector          Cache          PDF / Report
                  Queue
                  Streams
        ▲
        │
┌───────┴──────────────────────────────────────────────┐
│                  Async Workers                      │
│                                                     │
│ 行情 │ 公告 │ 财报 │ 研报 │ 新闻 │ 政策 │ MCP     │
│                                                     │
│ Normalize → Dedup → Extract → Store → Event         │
└─────────────────────────────────────────────────────┘
```

---

# 5. 核心模块边界

## 5.1 Instrument

负责：

- 股票
- ETF
- 行业
- 指数
- 事件篮子

核心表：

```text
instrument
instrument_alias
instrument_tag
instrument_relation
```

---

## 5.2 Watchlist

负责：

- 加入自选
- 删除自选
- 标的自动分类
- 研究建档触发
- 自选状态

分类：

```text
INSTITUTIONAL_TREND
HOT_MONEY
HYBRID
EVENT_DRIVEN
```

注意：

分类结果必须可解释。

---

## 5.3 Research

负责：

- Research Package
- 首次全量研究
- 增量更新
- 模块新鲜度
- 版本管理

研究模块建议：

```text
COMPANY
BUSINESS
INDUSTRY
ORDER
FINANCIAL
EXPECTATION
VALUATION
RISK
CATALYST
COMPETITOR
MANAGEMENT
```

---

## 5.4 Evidence

负责：

- 信息类型
- 来源等级
- 原始来源
- 证据有效期
- Thesis 关联

信息类型：

```text
FACT
ESTIMATE
THESIS_INFERENCE
USER_HYPOTHESIS
```

来源等级：

```text
S = 公司公告 / 财报
A = 交易所 / 监管 / 官方数据
B = 公司投资者交流 / 机构调研
C = 券商研报
D = 权威财经媒体
E = 社交媒体
F = 传闻 / 未验证
```

硬规则：

```text
F 级信息不得直接进入核心 Thesis。
```

---

## 5.5 Thesis Engine

负责：

- 建立 Thesis
- Thesis Version
- Evidence 关联
- 反方证据
- Validation
- Invalidation
- Health Score
- Score Ledger

状态：

```text
SUPPORTED
NEUTRAL
WEAKENING
INVALIDATED
PENDING
```

---

## 5.6 Expectation Engine

负责：

- 机构预测
- 盈利预期历史
- 券商差异
- Consensus Snapshot
- 上调 / 下调检测

---

## 5.7 Valuation Engine

负责：

- Bull / Base / Bear
- PE / PS / EV/EBITDA 等参数
- 目标市值计算
- 风险收益比

V1 先支持：

```text
利润 × PE
```

---

## 5.8 Expectation Gap

负责：

```text
盈利预测变化
股价变化
估值变化
```

输出：

```text
HUGE_POSITIVE
POSITIVE
MATCHED
FULLY_PRICED
NEGATIVE
```

---

## 5.9 Price-In Engine

负责：

- 市场已交易哪些预期
- 尚未充分交易哪些预期
- 计价程度

采用：

```text
Quant Layer
+
Reasoning Layer
```

---

## 5.10 Market Regime

负责：

```text
PANIC
ICE
REPAIR
NORMAL
ACTIVE
EUPHORIC
RETREAT
```

输入：

- 上涨家数
- 下跌家数
- 涨停
- 跌停
- 炸板率
- 连板高度
- 成交额
- 成交额相对 20 日均额
- 指数趋势
- 情绪斜率

输出：

- regime
- score
- risk budget
- position cap

禁止 LLM 决定分数。

---

## 5.11 Portfolio

负责：

- 持仓
- 仓位
- 现金
- 行业暴露
- 相关性
- 最大持仓数

硬规则：

```text
默认最多 4 只
第 5 只必须做 Position Replacement PK
```

---

## 5.12 Trade Plan

负责：

- 买入区
- 初始仓位
- 加仓条件
- 止损
- 失效条件
- 目标情景
- 冻结
- 版本变更

核心原则：

> Freeze 后不可 UPDATE 原版本。

---

## 5.13 Catalyst

负责：

- 财报
- FOMC
- 订单公告
- 产业事件
- 政策
- 产品发布

Catalyst 不是日历装饰。

每个 Catalyst 包含 Validation Rules。

---

## 5.14 Discipline

负责：

- 追高
- 止损延迟
- 计划外交易
- 亏损补仓
- 仓位超限
- 纪律评分
- 行为统计

---

## 5.15 Agent Runtime

负责：

- Context Builder
- Tool Registry
- Prompt Router
- Model Router
- Policy Layer
- Streaming Response

Agent 不直接写数据库。

---

# 6. 关键数据模型

下面为 V1 建议核心表。

---

## 6.1 instrument

```sql
id
symbol
name
exchange
asset_type
industry
status
created_at
updated_at
```

---

## 6.2 watchlist_item

```sql
id
instrument_id
classification
classification_reason
classification_confidence
status
added_at
```

---

## 6.3 research_package

```sql
id
instrument_id
version
status
started_at
completed_at
last_verified_at
```

status：

```text
ACTIVE
STALE
UPDATING
FAILED
```

---

## 6.4 research_module

```sql
id
research_package_id
module_type
version
status
summary
last_verified_at
stale_after
```

---

## 6.5 evidence

```sql
id
instrument_id

information_type
source_grade
source_type

title
content

source_url
source_file_id
source_date

effective_from
effective_to

verification_status
created_at
```

---

## 6.6 thesis

```sql
id
instrument_id
title
current_version_id
status
health_score
created_at
last_verified_at
```

---

## 6.7 thesis_version

```sql
id
thesis_id
version_no

statement
status

health_before
health_after

change_summary

created_at
```

---

## 6.8 thesis_evidence

```sql
id
thesis_version_id
evidence_id

direction
impact_weight
reason

created_at
```

direction：

```text
SUPPORT
CONTRADICT
NEUTRAL
```

---

## 6.9 thesis_validation_rule

```sql
id
thesis_id

rule_type
metric
operator
threshold
description

is_invalidation_rule
```

---

## 6.10 thesis_score_ledger

```sql
id
thesis_id
thesis_version_id
evidence_id

delta
reason

created_at
```

---

## 6.11 broker_report

```sql
id
instrument_id
broker
analyst
report_date
rating
target_price
source_file_id
```

---

## 6.12 broker_estimate

```sql
id
broker_report_id
fiscal_year

revenue
net_profit
eps

created_at
```

---

## 6.13 expectation_snapshot

```sql
id
instrument_id
snapshot_date

consensus_revenue
consensus_profit
consensus_eps

broker_count

upgrade_count
maintain_count
downgrade_count
```

---

## 6.14 valuation_scenario

```sql
id
instrument_id
version

scenario
fiscal_year

profit_assumption
pe_assumption

target_market_cap
upside_downside

assumption_note
created_at
```

scenario：

```text
BEAR
BASE
BULL
```

---

## 6.15 price_in_snapshot

```sql
id
instrument_id
snapshot_date

quant_score
reasoning_score
final_score

priced_factors_json
unpriced_factors_json
```

---

## 6.16 expectation_gap_snapshot

```sql
id
instrument_id
snapshot_date

profit_revision_30d
stock_return_30d
valuation_change_30d

score
status
reason
```

---

## 6.17 trade_plan

```sql
id
instrument_id
current_version_id
status
created_at
```

---

## 6.18 trade_plan_version

```sql
id
trade_plan_id

version_no
parent_version_id

buy_zone_low
buy_zone_high

initial_position_pct

add_condition
stop_loss

invalidation_condition

base_target
bull_target

status
change_reason

created_at
frozen_at
```

---

## 6.19 catalyst

```sql
id
instrument_id

title
event_type
expected_at
actual_at

status

created_at
```

---

## 6.20 catalyst_check

```sql
id
catalyst_id

metric
operator
target_value

actual_value
result

weight
```

result：

```text
PASS
FAIL
PENDING
```

---

## 6.21 portfolio_position

```sql
id
instrument_id

quantity
avg_cost
position_pct

opened_at
closed_at

linked_trade_plan_version_id
```

---

## 6.22 discipline_event

```sql
id
instrument_id

event_type
severity

planned_value
actual_value

reason
occurred_at
```

---

# 7. Thesis Score Ledger

禁止黑盒评分。

例：

```text
THESIS-001

基础分                       78

Q3订单证据增强               +3
两家券商上调盈利预测          +2
收入增长继续加速             +2
经营现金流尚未改善           -1

────────────────────────────
当前                        84
```

计算由规则引擎完成。

LLM 只提供：

```text
Evidence Classification Proposal
```

---

# 8. 关键事件定义

V1 不引入 Kafka。

使用：

```text
Redis Streams
```

核心事件：

```text
instrument.added_to_watchlist

research.full_requested
research.completed
research.module_updated

evidence.created

thesis.created
thesis.updated
thesis.invalidated

broker_report.ingested
estimate.revised
consensus.updated

price_in.updated
expectation_gap.updated

valuation.updated

market.regime_changed

trade_plan.created
trade_plan.frozen
trade_plan.revised

catalyst.created
catalyst.completed

position.opened
position.updated
position.closed

discipline.violation_created
```

---

# 9. 关键事件链路

## 9.1 加入自选

```text
POST /watchlist
↓
instrument.added_to_watchlist
↓
Classification Service
↓
research.full_requested
↓
Research Worker
↓
Evidence Extraction
↓
Research Package
↓
Initial Thesis
↓
research.completed
```

---

## 9.2 新研报进入

```text
broker_report.ingested
↓
Estimate Extractor
↓
broker_estimate
↓
Consensus Calculator
↓
estimate.revised
↓
Expectation Gap
↓
Price-In
↓
Thesis Re-evaluation
↓
Notification
```

---

## 9.3 Q3 财报进入

```text
financial_report.ingested
↓
Fact Extraction
↓
Catalyst Validation
↓
4 / 5 checks
↓
catalyst.completed
↓
Thesis Score Ledger
↓
78 → 83
↓
Agent Notification
```

---

## 9.4 修改冻结止损

```text
User:
96 → 90

↓
Risk Service

risk_delta > 0

↓
BLOCK normal edit

↓
Require reason

↓
Create PLAN-v2

↓
trade_plan.revised
```

---

# 10. Agent Runtime

## 10.1 Agent 架构

```text
User
 ↓
Agent Orchestrator
 ↓
Context Builder
 ↓
Policy Layer
 ↓
Tool Registry
 ↓
LLM
 ↓
Structured Proposal
 ↓
Domain Service
```

---

## 10.2 Tool Registry

V1 工具：

```text
get_instrument

get_research_package

get_current_thesis
get_thesis_versions
get_thesis_evidence

get_broker_estimates
get_consensus_history

get_expectation_gap
get_price_in

get_valuation_scenarios

get_market_regime

get_portfolio
get_position

get_trade_plan
get_trade_plan_versions

get_catalyst_tasks

get_discipline_summary

calculate_valuation
calculate_position_size

propose_thesis_update
propose_trade_plan
```

---

## 10.3 禁止 Agent 直接调用

```text
UPDATE DATABASE

delete historical version

modify frozen plan

change market regime score

change portfolio limit

execute trade
```

---

# 11. Bull / Bear / Judge

V1 不需要复杂 Multi-Agent Runtime。

流程：

```text
Evidence Package
      │
      ├── Bull Prompt
      │
      ├── Bear Prompt
      │
      └── Judge Prompt
```

输出：

```text
确定事实
合理推断
证据不足
核心争议
```

三个角色必须读取相同 Evidence Snapshot。

---

# 12. Market Regime Engine

## 12.1 输入

```text
advancers
decliners

limit_up
limit_down

failed_limit_up_rate

max_limit_streak

turnover
turnover_20d_ratio

index_trend_daily
index_trend_60m

breadth

sentiment_slope
```

---

## 12.2 输出

```json
{
  "regime": "REPAIR",
  "score": 28,
  "position_budget": {
    "min": 0.30,
    "max": 0.45
  },
  "single_position_max": 0.12,
  "initial_position_max": 0.05
}
```

---

# 13. API 设计

统一：

```text
/api/v1
```

---

## 13.1 Instrument

```http
GET    /instruments/{id}
GET    /instruments/search
```

---

## 13.2 Watchlist

```http
GET    /watchlist
POST   /watchlist
DELETE /watchlist/{id}
```

---

## 13.3 Research

```http
GET  /instruments/{id}/research
POST /instruments/{id}/research/full
POST /instruments/{id}/research/refresh
```

---

## 13.4 Thesis

```http
GET  /instruments/{id}/theses

POST /instruments/{id}/theses

GET  /theses/{id}
GET  /theses/{id}/versions
GET  /theses/{id}/evidence

POST /theses/{id}/revalidate
```

---

## 13.5 Expectation

```http
GET /instruments/{id}/expectations
GET /instruments/{id}/expectations/history
GET /instruments/{id}/broker-estimates
```

---

## 13.6 Valuation

```http
GET  /instruments/{id}/valuation
POST /instruments/{id}/valuation/recalculate
```

---

## 13.7 Price-In

```http
GET /instruments/{id}/price-in
GET /instruments/{id}/expectation-gap
```

---

## 13.8 Trade Plan

```http
GET  /instruments/{id}/trade-plan

POST /trade-plans
POST /trade-plans/{id}/freeze
POST /trade-plans/{id}/revise

GET /trade-plans/{id}/versions
```

---

## 13.9 Catalyst

```http
GET  /instruments/{id}/catalysts
POST /catalysts
POST /catalysts/{id}/validate
```

---

## 13.10 Portfolio

```http
GET /portfolio
GET /portfolio/risk
GET /portfolio/correlation
POST /portfolio/replacement-pk
```

---

## 13.11 Market

```http
GET /market/regime
GET /market/sentiment
```

---

## 13.12 Agent

```http
POST /agent/chat
POST /agent/rebut
POST /agent/explain-thesis
POST /agent/pretrade-check
```

Agent 流式：

```text
SSE
```

---

# 14. 实时通信

## SSE

适合：

```text
Agent streaming
Research progress
Report extraction progress
```

---

## WebSocket

适合：

```text
price_tick
market_regime
breadth_update
alert
```

---

# 15. 项目目录结构

建议：

```text
thesisguard/
├── apps/
│   ├── web/
│   ├── api/
│   └── worker/
│
├── backend/
│   ├── common/
│   │   ├── db/
│   │   ├── events/
│   │   ├── security/
│   │   └── storage/
│   │
│   ├── instrument/
│   ├── watchlist/
│   ├── research/
│   ├── evidence/
│   ├── thesis/
│   ├── expectation/
│   ├── valuation/
│   ├── price_in/
│   ├── market/
│   ├── portfolio/
│   ├── trade_plan/
│   ├── catalyst/
│   ├── discipline/
│   ├── intelligence/
│   ├── notification/
│   └── agent/
│
├── migrations/
├── infra/
│   ├── docker/
│   └── nginx/
│
├── docs/
│   ├── PRD.md
│   ├── TAD.md
│   ├── DATA_MODEL.md
│   ├── EVENTS.md
│   └── API.md
│
├── docker-compose.yml
└── README.md
```

---

# 16. Docker Compose 拓扑

```text
web
api
worker

postgres
redis
minio

nginx
```

后期可增加：

```text
scheduler
```

V1 可让 worker 自己完成定时任务。

---

# 17. 数据接入策略

## 17.1 P0 必接

```text
A股基础证券信息
日线行情
财报
公告
投资者关系活动记录
新闻
用户手工交易记录
```

---

## 17.2 P1

```text
券商研报
一致预期
盈利预测历史
行业数据
政策数据
市场宽度
涨跌停
连板数据
```

---

## 17.3 P2

```text
同花顺 MCP
券商账户
实时成交
分钟行情
龙虎榜
北向 / 机构资金
```

---

# 18. 数据抓取层

统一抽象：

```python
class DataProvider:
    async def fetch(...)
    async def normalize(...)
```

Provider 示例：

```text
AkshareProvider
ExchangeProvider
CninfoProvider
NewsProvider
BrokerReportProvider
TonghuashunMcpProvider
```

所有 provider 的输出必须先 Normalize。

禁止业务层直接依赖某个供应商 schema。

---

# 19. Research Pipeline

```text
Source
↓
Fetch
↓
Raw Document
↓
Dedup
↓
Parse
↓
Fact Extraction
↓
Evidence
↓
Entity Link
↓
Research Module Update
↓
Thesis Revalidate
↓
Notify
```

---

# 20. 文档 RAG Pipeline

```text
PDF
↓
Parser
↓
Chunk
↓
Metadata
↓
Embedding
↓
pgvector
```

Metadata 至少包含：

```text
instrument_id
source_grade
source_type
source_date
document_id
page
section
```

---

# 21. 交易计划风险控制

修改冻结计划时计算：

```text
Original Risk

(entry - stop) × position
```

用户将：

```text
stop 96 → 90
```

必须输出：

```text
Risk increased by X%
```

如风险扩大：

```text
require reason
```

---

# 22. 个人交易模型

不要用大 Prompt 保存。

结构化为：

```text
trading_profile
```

以及：

```text
behavior_metric
```

推荐指标：

```text
win_rate_by_model

win_rate_by_regime

avg_holding_period

chase_rate

late_stop_rate

loss_averaging_rate

plan_violation_rate

risk_reward_distribution
```

50–100 笔后再生成个性化规则。

---

# 23. 通知系统

通知等级：

```text
P0
P1
P2
```

P0 示例：

```text
Thesis INVALIDATED
Frozen stop breached
Position limit exceeded
Major negative announcement
```

P1：

```text
Expectation revised
Price-In exceeds threshold
Catalyst failed
```

P2：

```text
news related
research module stale
```

---

# 24. Audit Log

必须记录：

```text
谁
什么时候
修改什么
旧值
新值
原因
```

尤其：

```text
Thesis
Trade Plan
Discipline
Prompt
```

---

# 25. P0 黄金链

第一阶段只做一条真正闭环。

```text
Add to Watchlist
↓
Classify
↓
Create Research Package
↓
Extract Evidence
↓
Create Thesis
↓
Show Thesis Validation
↓
Add New Evidence
↓
Revalidate Thesis
↓
Score Ledger
↓
Show Why Score Changed
```

---

# 26. P0 工作包

## WP-01 工程骨架

目标：

```text
Vue3
FastAPI
Postgres
Redis
MinIO
Docker Compose
```

验收：

```bash
docker compose up -d
```

全部启动。

---

## WP-02 Instrument + Watchlist

实现：

- 搜索证券
- 加入自选
- 分类
- Watchlist API

---

## WP-03 Research Package

实现：

- Research Package
- Research Module
- 首次建档任务
- 增量刷新

---

## WP-04 Evidence

实现：

- Evidence Model
- Source Grade
- Information Type
- Evidence API

---

## WP-05 Thesis

实现：

- Thesis
- Version
- Validation
- Evidence association
- Score Ledger

这是 P0 最核心工作包。

---

## WP-06 Research UI

实现：

- 自选池
- 自动建档
- 单股 Thesis Validation
- Evidence Drawer
- Thesis Health 变化原因

---

## WP-07 Agent Read-Only

Agent 只允许：

```text
查询
解释
反驳
```

禁止写操作。

---

## WP-08 Incremental Update

模拟：

```text
新公告
→ Evidence
→ Thesis
→ 78 → 84
```

---

# 27. P0 验收标准

必须可以完整演示：

## Case 1

加入：

```text
301128 强瑞技术
```

系统：

```text
分类
↓
建档
↓
Research ACTIVE
↓
生成 5 条 Thesis
```

---

## Case 2

查看 Thesis：

```text
AI服务器液冷订单持续增长
```

必须看到：

- 状态
- 建立日期
- 支持证据
- 反对证据
- 待验证
- 失效条件

---

## Case 3

模拟新证据：

```text
Q3订单增强
```

系统：

```text
78 → 81
```

并显示：

```text
+3 Q3订单证据增强
```

---

## Case 4

历史仍可查看：

```text
Thesis v1
Thesis v2
```

不得被覆盖。

---

# 28. P1 工作包

```text
Expectation Engine
Broker Reports
Consensus History

Bull / Base / Bear

Expectation Gap

Price-In

Trade Plan Freeze

Catalyst Validation
```

---

# 29. P2 工作包

```text
Market Regime
实时市场情绪

Portfolio

Discipline

Realtime Alerts

同花顺 MCP

券商账户同步
```

---

# 30. 非功能要求

## 性能

普通 API：

```text
P95 < 500ms
```

Research / Agent：

异步。

---

## 可追溯

任何：

```text
Thesis
Estimate
Trade Plan
```

必须能追到：

```text
source
version
timestamp
```

---

## 数据安全

API Key：

```text
encrypted
```

禁止明文入库。

---

## Agent 安全

Tool 白名单。

不允许 Agent：

```text
raw SQL
shell
arbitrary HTTP
```

---

# 31. V1 明确不做

```text
自动买入
自动卖出

券商直连下单

高频量化

全市场 tick

复杂多 Agent 协作网络

AutoML 预测涨跌

大规模组合优化
```

---

# 32. 产品架构核心

ThesisGuard 的技术护城河最终不是：

```text
LLM
```

而是：

```text
Structured Facts
      +
Evidence Graph
      +
Thesis Versioning
      +
Expectation History
      +
Trade Plan History
      +
Behavior History
```

LLM 只是这些结构化资产之上的 Reasoning Layer。

---

# 33. 最终架构原则

```text
事实 → DB

证据 → Evidence

逻辑 → Thesis

预期 → Expectation

赔率 → Valuation

市场风险 → Regime

动作 → Trade Plan

验证 → Catalyst

结果 → Trade

复盘 → Discipline

解释 → Agent
```

这应该成为 ThesisGuard V1 的工程边界。

---

# 34. 推荐下一步

下一步不建议继续扩产品功能。

建议直接进入：

```text
WP-01
ThesisGuard 工程基础骨架
```

然后按顺序执行：

```text
WP-01 工程骨架

WP-02 Instrument / Watchlist

WP-03 Research Package

WP-04 Evidence

WP-05 Thesis Engine

WP-06 Thesis Validation UI

WP-07 Read-only Agent

WP-08 Incremental Update
```

当 WP-08 验收通过时，ThesisGuard 才第一次真正形成产品闭环。

---

# 35. 一句话架构定义

> ThesisGuard 是一个以 Thesis 为核心对象、以结构化事实和可追溯证据为基础、以事件驱动持续验证投资逻辑、并通过不可变交易计划和纪律记录控制个人交易行为的研究与决策系统。

