# ThesisGuard Market Data / A 股行情技术预案审计

> Audit ID: `AUDIT-MARKET-DATA-2026-09-15`
>
> Date / timezone: 2026-09-15，Asia/Shanghai；主要取证窗口约 17:50—18:10。
>
> Status: `DESIGN_ONLY — PROPOSED / NOT_APPROVED_FOR_IMPLEMENTATION`
>
> Timing recommendation: **PARALLEL_DESIGN_ONLY**
>
> Scope: 当前仓库定向静态审计、官方资料核查、合同草案和拟议工作包；不构成业务验收、数据采购或策略启用授权。

## 1. AI State Capsule 与结论

- ThesisGuard 是个人 A 股现金账户的证据与风险操作系统；行情应成为可追溯输入，不能替代账户、订单、Evidence 或用户确认。
- [FACT] local `main@7d3734bc8346c16f9bbf7f7d9806309949c996de` 有 Instrument 主数据、Research 容器、Evidence persistence foundation；没有正式行情 Provider、Quote/Bar 存储、行情 API、行情推送或 K 线展示。[E01—E06]
- [FACT] 本地缓存的 `origin/main` 同为 `7d3734b`；远端当前 HEAD **UNKNOWN**，不能把 tracking ref 当作远程实时状态。[E01、E08]
- [FACT] WP04-02 candidate 为 `codex/wp04-02-evidence-domain-service@bdd70edc153b6ed5def65ed99c41f325df45f066`；有 service 实现，但本轮读取期间 services.py / service tests 正在并发修改，未验收该修改。[E07]
- [CLAIM] 当前治理材料将下一最小修复定位为 R1C-01 latest-first lifecycle eligibility；R1C/R1D 和原 WP04-02 复验仍未闭环。本轮没有重跑 Evidence 测试。[E07]
- [PROPOSAL] iFind 服务端 HTTP 优先作为主源候选；AKShare 用于历史补数、开发研究和受限 fallback，生产用途许可未核实前不能进入交易准入。
- [PROPOSAL] PostgreSQL 保存必要行情事实、修订和决策快照；Redis 仅缓存与分发。实时行情不逐条写 EvidenceVersion。
- [PROPOSAL] 普通盘中 30 秒批量刷新；持仓/待入场及尾盘关注标的 15 秒；准入前按需重取。阈值是待验证的数据政策，不是已批准交易规则。
- [PROPOSAL] 先完成 Evidence 修复和 WP-05 核心验收，再将最小双指数日线与价格输入作为 WP-RISK-01 的前置切片；完整分钟 UI / SSE 不阻塞风险内核。
- Strategy remains `UNPROVEN`；Whole Product remains `NOT_READY_FOR_FULL_AGENT_BUILD`。

## 2. 审计范围、Git 与验证边界

项目类型为 API_SERVICE / WEB_APP / DATA_PIPELINE（目标能力）；当前是模块化单体工程骨架。阅读 README、AGENTS、canonical PRD/TAD、PRODUCT_GOAL_REALIGNMENT、SECTOR_CROWDING_DECISION、ARCHITECTURE_REFERENCES，检查 backend/instrument、market、common、Research/Evidence 边界、apps/api、worker、web、requirements、Compose、nginx、模型注册与全部现有迁移。对 backend/apps/tests/infra/docs 做 Market、quote、bar、kline、provider、AKShare、iFind、freshness、Redis、WebSocket/SSE 等检索，区分金融 quote 与文档引文、Bar 与名称误命中。

| 对象 | 当前观察 | 不能据此证明 |
|---|---|---|
| local main | `7d3734b`；开始时 tracked diff 为空，有四份未跟踪的 Evidence 治理文档 | 生产、全部测试绿色、远端已同步 |
| local origin/main | `7d3734b`，缓存内容可审查 | 本轮远程 HEAD |
| candidate | `bdd70ed`；该分支相对 main 没有 instrument/market/common/API/worker/web/migrations 的 committed 差异；Evidence service 是独立候选切片 | WP04-02 已集成 main 或 candidate 当前修改通过 |
| 远端查询 | 默认代理端口 17891 不可达；无代理沙箱查询 DNS 失败；获准的只读无代理查询未返回结果后中断；Web 仓库查询亦失败 | 远端不存在、private、无新提交等猜测 |
| 当前 OpenAPI | 现有 Python 3.12 环境中调用 `create_app().openapi()`，未启动 lifespan / 服务；无行情路径 | 运行中的 API / DB / MinIO 正常 |
| OpenAPI 一致性 | paths 相同；components 三个 Research enum 的 description 漂移 | api:check、build、类型检查全部通过 |

系统 PATH 中另一 Python 缺少 pydantic_settings，第一次导出失败；随后使用已有 `/opt/homebrew/opt/python@3.12/bin/python3.12` 成功做内存 schema 比较。没有安装依赖、生成/改写 OpenAPI、启动服务、DB 查询、migration 或业务测试。本轮最高仓库证据为 L1 静态实现与当前命令观察，不声称 L3/L4/L5。

起始未跟踪文件均保留：`TASK-WP04-02-R1C-01-dispatch-prompt.md`、`TASK-WP04-02-R1C-01-task-contract.md`、`TASK-WP04-02-R1C-BASELINE-CONFIRM-R1-acceptance.md`、`TASK-WP04-02-R1C-BASELINE-CONFIRM-R1-INDEPENDENT-REVIEW-acceptance.md`（均位于 docs/acceptance）。本任务唯一拟新增文件是本文；不 commit / push，不改 candidate。

## 3. 当前能力矩阵

状态采用用户指定五级。`DESIGN_ONLY` 表示有设计论述；其附注 `DOCUMENTATION_ONLY / HISTORICAL` 不证明实现。`PLANNED` 表示需求或路线已提及，缺少具体实现；`NOT_STARTED` 表示本轮检查范围没有可信实现，也没有正式独立合同。本文的新方案不反向升级以下审计时点状态。

| 能力 | 状态 | 证据与缺口 |
|---|---|---|
| Instrument 主数据 | PARTIALLY_IMPLEMENTED | models/services/schemas/API、migration 0002；五项内置 catalog（四只股票和 FOMC 事件篮子），不是全量证券服务；symbol-only 查询存在跨交易所身份歧义。[E02] |
| MarketDataProvider 抽象 | NOT_STARTED | 无代码；历史 TAD 仅有通用 DataProvider.fetch/normalize，非专用行情合同。[E03、E09] |
| 实时 Quote | PLANNED | 产品需要价格/freshness；详情页 45.67 是 Mock。[E04、E09] |
| Snapshot（行情事实快照） | NOT_STARTED | 无 Quote Snapshot / Market Snapshot ORM、repository、服务或路由。[E03、E06] |
| Historical Bar（日/周） | PLANNED | 历史 TAD 提及日线接入；当前无采集或表。[E06、E09] |
| Intraday Bar / 分时 | PLANNED | 历史接入路线提及分钟行情；当前无实现。[E03、E09] |
| Kline API | NOT_STARTED | 注册路由和内存导出的当前 OpenAPI 均无行情端点。[E05] |
| 行情时间序列存储 | NOT_STARTED | migration 0001—0004 和 registry 没有行情表；不因 PostgreSQL/pgvector 存在而成立。[E06] |
| WebSocket/SSE 行情推送 | DESIGN_ONLY | 仅历史 TAD 对行情 WS 的用途说明；Agent SSE proposal 是不同流。[E03、E09] |
| Redis 行情缓存 | NOT_STARTED | 有同步通用 TTL client，没有行情 key、标准化写入或采集消费者。[E03] |
| Provider fallback | NOT_STARTED | Instrument catalog fallback 是种子搜索，不是行情切换。[E02、E03] |
| 行情 freshness | DESIGN_ONLY | canonical fail-closed 原则存在；OD-003 时效门尚待设计。Research freshness 不是行情算法。[E09] |
| 技术指标计算 | NOT_STARTED | 未发现行情 MA/ATR/量能 service；不得把 healthScore 原型当指标。[E03、E04] |
| 前端 K 线展示 | NOT_STARTED | StockDetailView 为 Mock/占位，没有数据驱动图表。[E04] |
| TradingView Lightweight Charts | DESIGN_ONLY | 历史 TAD 点名；package/lock/source 未接入。[E04、E09] |
| ECharts | NOT_STARTED | package/lock/source 无接入。[E04] |
| 交易日历/会话/证券停牌状态服务 | NOT_STARTED | 无专用合同实现；Instrument ACTIVE 不等于可交易。[E02、E03] |

通用设施单独评价：async PostgreSQL session 和已注册领域 ORM 属于静态 `IMPLEMENTED`；Redis TTL wrapper、Redis Streams publish helper、Dramatiq broker 与 health/echo actor 属于已实现的基础设施切片。没有行情 scheduler/actor、消费者、durable market event、行情 fan-out 或真实采集证据。Redis client / boto3 包装及 actor 当前存在同步 I/O；以后应在行情边界处理阻塞，不把它们直接放进 async 请求热路径。[E03、E06]

## 4. 权威关系与漂移

| 来源 | 生效边界 / 本轮处理 |
|---|---|
| PRODUCT_GOAL_REALIGNMENT / canonical PRD/TAD | 风险 OS 优先、Evidence→Thesis→Risk 主线、不可变事实和 fail-closed 继续生效。其历史事实章节不作为 live status。 |
| README / AGENTS / ARCHITECTURE_REFERENCES | d8f38dd / c38c96f 的本地/远端描述已落后于当前本地 refs；只记录漂移，不改入口文件。 |
| PRODUCT_GOAL_REALIGNMENT §16 | bd4b1d7 时点 Evidence 仅占位的描述已被 main persistence 实现取代；产品目标的权威性不把过时事实变成当前事实。 |
| SECTOR_CROWDING_DECISION | `APPROVED — DEFERRED`；当前 candidate hash 已变化，时机约束仍生效。本预案不授权 Sector score、空表/API、成分工程。 |
| 历史 TAD `(1)` | DOCUMENTATION_ONLY / HISTORICAL：通用 Provider、Lightweight Charts、行情 WS、分钟数据 P2 都只能作参考。禁止让其优先级覆盖当前 canonical。 |
| Agent / Memory / structured output proposals | 可参考只读和追溯边界；其 SSE/Runtime 及内部 WP 编号不是现有能力或 canonical Market 工作包。 |
| 当前 PRD §8、§16 | 明确排除 60 分钟生产确认、分钟级策略。用户本轮提出 30m/60m 观察需求；可设计数据/展示，不能启用新确认门或改 Setup B。 |
| 本文 | PROPOSED；不冻结合同、不修改交易规则、不宣布新增 canonical WP。 |

## 5. 方案取舍与正式目标架构

| 方案 | 好处 | 代价 / 结论 |
|---|---|---|
| A：单一 AKShare + 前端直接拉数 | 早期研究成本低 | 缺许可、时效、版本与故障治理；无法作为唯一生产事实源，拒绝作为正式架构。 |
| B：模块化单体 Gateway + 一个获准主源 + 受限辅源 | 依赖可替换、审计边界清晰、运维可控 | 需要先核实授权和合同；**推荐**。 |
| C：全市场 Tick、多源投票、流平台/TSDB | 大规模吞吐与低延迟 | 当前无此规模或策略需求，延后。 |

```text
Instrument + provider symbol mapping + versioned calendar/session
                              |
                              v
                     Market Data Gateway
          (batching / quota / timeout / explicit source selection)
                              |
                              v
                     MarketDataProvider port
                  /             |             \
          IFindProvider    AkshareProvider    future adapter
          server HTTP      bounded research   only when justified
                  \             |             /
                   Provider Observation envelope
                              |
                   Normalize + Validate + Quality
                              |
                    Canonical Quote / Bar revisions
                              |
                     PostgreSQL durable facts
                              |
                       Redis cache / fan-out
                              |
                 Market query / Indicator / Market Gate
                              |
              Risk Gate + Trade Plan + Read-only Agent + UI
```

箭头是采集/读取流程，不要求每个组件单独部署。消费者经 Market 查询服务读 PostgreSQL 或带确切 observation_id 的 Redis projection；Redis 不能成为必须经过的唯一读取路径。同步交易判断必须可回到 durable facts，并提交不可变决策输入快照。

建议将行情技术边界置于 Market 内部子模块，例如未来 `backend/market/data/`，Market Gate 属于 Market 业务领域；不放进 common，不先建微服务或通用 Provider Runtime。图中的 FutureProvider 仅代表可实现同一 port，V1 不创建空类、表、Router 或运行时注册框架。MarketDataProvider 与延后的 LLM Capability Runtime 是两类能力；本文不改变 ADR-CAP-01。

Gateway 负责批量、去重请求、账户级预算、超时/有限重试、明确切换记录；adapter 只封装供应商访问与字段映射。Normalization/Quality 负责单位、身份、时间、复权、质量。Market service 负责事实查询/快照/业务规则。Risk 与业务层禁止直接调用 ifind.xxx / akshare.xxx。

## 6. Provider port 草案

以下是文档中的接口草案，没有业务代码或 API 路径变更。

```text
capabilities() -> ProviderCapabilities
get_quotes(instruments, requested_fields, deadline) -> BatchQuoteResult
get_bars(instrument, interval, start, end, limit, adjustment_spec,
         as_known_at=None, cursor=None) -> BarPage
get_intraday(instrument, trading_date, cursor=None) -> IntradayPage
get_session_status(exchange, trading_date) -> SessionObservation
get_instrument_status(instruments) -> InstrumentStatusBatch
get_trading_calendar(exchange, start_date, end_date) -> CalendarObservation
get_adjustment_metadata(instrument, start_date, end_date) -> AdjustmentObservation
```

- 公共查询使用稳定 instrument_id / exchange / instrument_type；adapter 内转换为供应商代码。`get_quote` 可作为 Gateway 对单元素 batch 的 convenience，避免重复协议。指数 000300 与股票代码不能靠裸 symbol 判别。
- capabilities 明确交易所/标的类别、interval、复权方法、历史深度、批量上限、source timestamp 语义、延迟声明、授权字段；不支持返回 UNSUPPORTED，不伪造空成功。
- batch 按 instrument 返回成功/错误/缺失，附 request_id、provider、endpoint、underlying_source、adapter/normalization revision、quota observation；半成功不视为全组成功。
- start/end 使用带时区的范围。拟议规范选取谓词为 `start <= bar_start < end`，不是按 bar_end 或覆盖相交选取；limit 有上限、确定排序和 cursor。adapter 转换供应商 inclusive 参数并取得必要边界数据，再按同一谓词裁剪。查询09:30—10:30包含09:30开始、10:30结束的60m Bar；查询09:31—10:30不包含它。按交易日期查询先转换本地日期的半开时点范围。分页按已选数据集/知识时点与bar_start确定排序，cursor、UI去重和裁剪不得各用不同时间字段；覆盖区间/最终性另行校验。
- intraday 是单交易日分钟点/均价等展示查询，不能返回并冒充完整 Tick，也不能从每 30 秒抽样 Quote 重建真实 OHLC。
- 原 `get_market_status()` 拆为交易所 session 与单证券 trading status；是否开市与是否停牌不能混为一谈。日历由确定性本地版本统一解释，Provider 只给来源观察。
- adjustment metadata 是复权可重现性所需；不假定所有复权都能用一个乘法 factor 表达。as_known_at 是本地版本查询语义，不能假定供应商支持历史知识时点。
- 错误类别建议 AUTH_EXPIRED、NOT_ENTITLED、RATE_LIMITED、TIMEOUT、UNAVAILABLE、INVALID_PAYLOAD、UNSUPPORTED、PARTIAL；附可重试性与 Retry-After，禁止日志暴露 token。

## 7. 数据源核查与选型

### 7.1 iFind：有条件的主源候选

[EXTERNAL DOCUMENT] 官方产品手册列出历史行情、THS_HF 分钟序列、THS_RQ 最新行情、THS_SS 快照、交易日期及 HTTP/SDK；THS_HF 覆盖 1/5/15/30/60 分钟等周期，THS_RQ 支持多代码和多字段。它们证明产品接口类别，**不证明本项目账户已开通**。[同花顺官方产品手册](https://quantapi.51ifind.com/gwstatic/static/ds_web/quantapi-web/help-center/manual.html)

| 要求 | 候选路径 / 判定 | 上线前需取得的证据 |
|---|---|---|
| 个股实时价、OHLC、前收 | RQ / HTTP real_time_quotation 候选 | 字段代码、价格基准、有效 source timestamp、实测延迟 |
| 分时、分钟 K、日/周 K | HF / history / snapshot 类候选 | 窗口、周期、auction/fill 口径、未完成 Bar、日线最终性 |
| 量、额、换手、bid/ask | 字段目录待逐字段核实 | 股/手/元/比例、累计或区间、流通股口径；盘口为可选 Level-1 |
| 复权 | 手册参数提供候选 | 方法、anchor、因子或公司行动、修订、当时可知能力 |
| 指数 | 两个冻结指数需单独验收 | exact 指数身份/类型、价格指数而非全收益替换、日线/日历口径 |
| 板块 | 可作为以后数据能力调查 | 分类/成员时点/许可未验证；Sector 仍延后 |
| 日历、批量 | 正式 port 候选 | 交易所覆盖、批量上限、逐项缺失、临时休市与修订 |
| SDK | 产品支持候选 | Linux/容器/Python 3.12 实测、native library、会话和并发 |
| HTTP | **优先评估**：现有 httpx、容器环境易隔离 | HTTPS、token/IP、合法 unattended server 调用及断线恢复 |
| 延迟、频率、授权、配额、费用、SLA | 不能用“实时”二字推断 | 当前账户合同/entitlement/报价、服务端用途、保存与派生展示/Agent 转发范围 |

[EXTERNAL DOCUMENT] 权限页区分免费/试用/正式账号：正式行情总量标为 1.5 亿单元格/周；免费实时为 300 万/月、分钟为 150 万/月；正式分钟历史标为 2010 年至今，免费/试用最近一年。此为官方页面政策快照，不是本账户额度承诺。[官方权限说明](https://quantapi.51ifind.com/gwstatic/static/ds_web/quantapi-web/help-center/permission.html)

[EXTERNAL DOCUMENT] FAQ 给出函数 QPS 10、账号总 QPS 20（EDB 例外），并提示分钟线受快照采样影响；日线入库时效有概括描述与专门时刻描述的差异。因此最终性要靠目标函数/字段的实际可用数据核验，不硬编码“15:07 必然 final”。[官方 FAQ](https://quantapi.51ifind.com/gwstatic/static/ds_web/quantapi-web/help-center/faq.html)

本轮 manual/FAQ 的直接 open 多次超时，以上来自官方页面搜索索引返回；权限页取得直接页面内容。未登录、未调数据接口、未检查账户 token；时效/收费站点/许可/SLA 全部为未验证外部依赖。最终判定：**适合作为优先尽调的生产主 Provider 候选，不是已批准主源。**

### 7.2 MCP 与服务端 Provider 分离

[EXTERNAL DOCUMENT] iFind 发布资料将 MCP 定位于 Agent 自然语言交互式金融数据获取。[官方新品发布资料](https://m.10jqka.com.cn/sr/20260312/56649265.shtml)

| MCP for Agent / interactive | Server-side Market Data Provider |
|---|---|
| 交互探索、查字段、研究解释候选 | 固定字段/范围、批量、频率预算、可控错误、版本化 normalizer |
| 自然语言与工具输出可能增加语义不确定性 | 无需 LLM，确定性写入 observation 和 snapshot |
| MCP access 不证明 HTTP/SDK entitlement | 服务端授权、持久化/展示用途和可测质量必须另验 |
| Agent 读取已有领域事实为主；外部查数结果是未摄取材料 | 只有确定性摄取流水线可提交 canonical 行情事实 |

不让 Agent/MCP 自主轮询并写行情真相，也不因 MCP 已上线便省略 Linux/HTTP、配额、许可和故障验收。若未来仅能通过 MCP 访问，必须先取得固定 schema、无需语义猜测的调用、服务端许可和端到端证据，再独立重审；不是 V1 默认实现路径。

### 7.3 AKShare：历史/研究候选，fallback 有限制

[EXTERNAL DOCUMENT] 官方股票文档列出日/周历史及不复权、前/后复权；分钟东财接口支持 1/5/15/30/60，1m 仅近五交易日且不复权，并提示某些历史 1m open 为 0；各接口成交量单位并不一致。不能拿该窗口补出多年完整分钟史或把零开盘视为真实价格。[AKShare 股票接口](https://akshare.akfamily.xyz/data/stock/stock.html)

[EXTERNAL DOCUMENT] 官方概览明确公开数据源、学术研究定位及网页变化导致接口异常；库采用 MIT 不等于源数据获得无限使用权。[AKShare 概览](https://akshare.akfamily.xyz/introduction.html)、[官方仓库](https://github.com/akfamily/akshare)

[INFERENCE / PROPOSAL] 从依赖公开站点和缺少本项目实测/授权的事实推导：不推荐唯一生产实时源。限流/封禁/接口漂移应由 adapter 的版本固定、真实字段样本、质量校验、明确超时和低频预算处理；版本更新需要回归，不能自动拉最新版。没有统一可承诺的限流或延迟数值。历史质量必须核验样本、停牌、复权、缺段和修订，成功返回 DataFrame 不算验收。

Fallback 必须按用途降级：可以显示带来源/质量标记的研究历史；交易价格只有在目标接口的 source_time、合法用途、单位与时效均通过同一合同后才可作为关键输入。若许可未澄清，AKShare 仅作研究候选，不进入生产持久化/准入。源数据许可与服务器保存、UI/Agent 展示范围需正式确认，本轮不作法律结论。

### 7.4 第三 Provider 与独立性

V1 只保留 port/capabilities，不实现第三 adapter。若 iFind 服务端授权、预算或可靠性无法达标，再比较有许可的替代来源：Tushare 可优先调查日线/日历/复权资料；其 daily 官方接口是日频数据，不能推导实时权限。[Tushare daily 官方文档](https://tushare.pro/document/2?doc_id=27)

EastmoneyProvider 必须区分官方授权产品与网页非正式接口；AKShare 东财与直接东财抓取共享上游，不能算两个独立源。ExchangeProvider 不等于免费取得交易所行情，BrokerProvider 只考虑获授权的只读行情，不创建交易权限。OtherProvider 只有在现有源存在已证实缺口时再尽调；不预建空适配器。

```text
Primary candidate:   iFind server HTTP（必要时经验证的 Linux SDK）
Secondary candidate: AKShare historical / development research（许可核验门）
Fallback:            按能力/用途获准的辅源；关键价格无合格辅源时 NO TRADE
Third:               条件触发尽调，V1 无默认第三实现
```

## 8. Canonical Quote / Observation 合同草案

Quote 是一个来源在明确行情时点的观察，不是无条件可交易价格。采用 Decimal / NUMERIC；JSON decimal 建议字符串，UI 才转图表数值。股价单位元，股数统一股，金额元，换手率统一比例（0.05=5%）；指数价格单位点，指数 volume/amount/turnover 不支持时为 null，不造零。

| 字段组 | 草案 |
|---|---|
| 身份 | quote_observation_id、schema_version、instrument_id、symbol、exchange、instrument_type、currency、provider_symbol |
| 原始价格事实 | last_price、open、high、low、prev_close；raw / NONE；prev_close 定义供应商实际比较基准，另保留 previous_session_close / reference_price 及其语义，不能默认同一个值 |
| 基础量额 | volume（日累计股）、amount（日累计元）、turnover_rate（比例）、turnover_basis / denominator_as_of；缺失为 null |
| 可选盘口 | bid_price/ask_price、bid_size/ask_size、book_time；单一 bid/ask 改成结构化 Level-1，缺失不伪造 |
| 时点 | trading_date、source_time、source_time_kind、last_trade_at（可选）、feed_as_of / heartbeat_at（可选）、observed_at、received_at、committed_at、knowledge_valid_from |
| 来源 | provider、underlying_source、endpoint、provider_revision（无则 null）、adapter_revision、normalization_revision、payload_hash、request_id |
| 会话/状态 | session_phase、market_status、instrument_trading_status、status_source_time、calendar_revision、session_rule_revision；涨跌停/风险警示事实单列且带有效期 |
| 时效评估 | freshness_status、quality_status、evaluated_at、use_case、freshness_policy_version、reason_codes、required_fields、field_quality |
| 延迟 | is_delayed（true/false/null）、delay_ms（声明或实测估计）、delay_basis；age_ms 和 acquisition_latency_ms 独立，不把延迟数值与来源年龄混淆 |

三个必需时点的区别：

- **source_time**：供应商声明的市场观察有效时点，可能是交易所快照时间、供应商采样时间或最后成交时间，必须由 source_time_kind 说明；不是本机请求时间。
- **observed_at**：adapter 完整取得该响应并首次观察其内容的本机 UTC 时间；同一旧来源数据重复响应只新增观察，不刷新 source_time。
- **received_at**：Gateway / 摄取边界收到 adapter envelope 的本机 UTC 时间；异步队列积压也被计入。它不是持久化时间，committed_at 另记。

正常本机边界 observed_at ≤ received_at ≤ committed_at；跨时钟异常记录质量原因，不能改写时间来满足排序。source_time 缺失、只有本机取得时间时，实时决策时效为 UNKNOWN。last_trade_at 旧可能只是无成交；只有经验证的行情快照时间/心跳与证券状态才能证明 feed 活着，单纯“价格没变”或 HTTP 200 均不足。

**拟议统一知识可见性时间轴：** `as_known_at=T` 仅选择本系统 durable 可查询发布时点 `knowledge_valid_from <= T` 的事实及当时已发布的canonical选择政策版本。knowledge_valid_from不得早于数据库提交完成确认；可用可靠的committed_at表达，但不能拿事务开始时间/写入前的now()冒充提交完成时间。具体时间记录与原子可见性机制在MD-00冻结、MD-04验证。observed_at/received_at是获取/传输证据，source_time是市场有效时点，都不使未发布数据提前可见。例如10:00取得、10:02收到、10:03确认提交并发布的事实，10:02的回放不可见，10:03之后才可见；事后补回旧source_time仍只能从本次发布时点可见。更正revision和canonical选择政策采用同一时间轴，不使用今天的选择政策重写历史选择。

Quote 数值检查：raw 价格须正且 OHLC 范围合理、量额非负；累计量额回退必须有重置/修订原因；非法数字、单位未知、错证券、日期不符隔离。盘口 stale 不必让纯研究图不可用，但可执行性所需字段失效必须阻止该用途。统一 DTO 不把不同日期/来源的字段偷偷拼成完整行情；若有明确复合视图，每字段保存 exact observation reference。

## 9. Freshness / Conflict 与 fail-closed

时效是 **输入 × 用途 × 会话 × evaluated_at × policy version** 的计算结果，不是永久写死的标签，也不复用 WP04 VerificationStatus。FRESH 不表示获准交易：研究、市场规则、计划、账户、费用、可卖数量和用户确认仍需独立通过。

| 状态 | 含义 / 处理 |
|---|---|
| FRESH | 当前用途必需字段、身份/来源、预期日期/版本和时效可判定且通过 |
| STALE | 已有有效观察，超过该用途允许时效或预期 Bar/日期未到位 |
| MISSING | 必需观察/字段/Bar 缺失；null、停牌、未上市要有具体原因 |
| CONFLICTING | 可比的关键观察存在未解决实质差异，或版本/单位/口径冲突 |
| UNKNOWN | 无法确定时间、许可/来源可用性、会话、单位、延迟或数据完整性 |

用 field_quality / reasons 保存多个问题；单标签建议按未解决关键冲突→必需缺失→可判定过期→不可判定→FRESH 归并，最终顺序在 MD-00 冻结。不要让枚举选择隐藏另一个阻断原因。validation/entitlement 轴与 freshness 分开，未知授权使使用资格不可核验。

**拟议候选阈值，非生产规则：** 普通 UI source age ≤60 秒；新增风险价格 source age ≤30 秒，准入前 on-demand refresh；数据获取/队列延迟也计入 end-to-end age。主源固定延迟若超过用途预算，快轮询也不能变 FRESH。价格快照时间不可靠时拒绝准入。暂不把这些数值写进冻结模型；实施前须获批数据政策、模拟和故障验收。

双指数门使用拟入场日 **前一完整交易日** 的最终日 Bar 及冻结规则要求的完整窗口，不用 intraday 替代。盘后/周末 freshness 按目标交易日和最终性判断，不能让正确周五日线在周末因“超过 60 秒”失效。若窗口长度/基准口径未在有效策略合同明确，则 UNKNOWN，不猜 MA 参数。

午休/闭市允许展示最后有效观察，UI 明示“午休/收盘截至”；不能改 source_time 或当成盘中新价。午休不把本已 stale 的观察救活；下午恢复必须获得当前会话确认。前收数据仅服务盘前用途，开市后对新增风险重新核验。

冲突仅比较同一 instrument、会话时间范围、字段单位、复权/最终性；异步成交导致两价格不同不直接判冲突。时间可比范围、tick-size tolerance、量额差容忍度待合同/实测冻结，不采用平均价或多数投票。保留双方与 underlying_source，不同采样分钟 Bar 要独立序列及原因；未解决关键冲突只能阻止新增风险，不能自动切源抹去冲突。

```text
required market input MISSING / STALE / CONFLICTING / UNKNOWN
  -> AssessmentStatus = UNKNOWN（确有已知失败时按冻结 evaluator 表达失败）
  -> user requests new risk: ActionDecision = NO TRADE
  -> expose missing inputs / reasons / exact references
```

不新增 ActionDecision 枚举；已有 EXIT_PENDING 不因行情失败解除，已存在的退出义务继续记录客观限制，行情失败本身不自动卖出。准入快照绑定 valid_until / exact input versions，用户确认前重新校验；过期结果不得靠页面停留继续 ALLOW。

## 10. Bar / Kline 合同与复权

| 字段组 | 合同草案 |
|---|---|
| 身份与边界 | bar_revision_id、instrument_id、exchange、interval（1m/5m/15m/30m/60m/1d/1w）、trading_date、bar_time（兼容显示字段，定义为 bar_end）、bar_start、bar_end、timezone=Asia/Shanghai |
| 数值 | open/high/low/close、volume（区间股）、amount（区间元）、turnover_rate（可选，带口径），price_unit/volume_unit |
| 最终性/完整性 | is_final、coverage_status、expected_count/actual_count（可判定时）、gap_reasons、auction_inclusion、session_phase/segments |
| 复权 | adjustment_type=NONE/QFQ/HFQ、adjustment_method、adjustment_anchor、adjustment_revision、adjustment_as_known_at、raw_input_refs |
| 来源与知识时点 | provider、underlying_source、provider_revision、adapter/normalization_revision、source_time/source_time_kind、observed_at、received_at、committed_at、payload_hash |
| 版本 | revision、supersedes_revision_id、correction_reason、aggregation_rule_version、calendar_revision、knowledge_valid_from；as_known_at采用§8统一发布可见性时间轴 |

**默认分用途：** canonical 持久化基础与 API 默认 NONE（raw）；图表观察默认明确选择 QFQ，并展示复权 anchor/revision。交易入场价格、Pmax、S0、保护价、限价与成交必须真实 raw 坐标。不能把 QFQ 支撑线直接用作 raw 订单价格。HFQ 不作默认看盘/执行价；是否用于研究收益必须另定义公司行动、现金和费用口径。

raw Bar 永久保留所用范围与修订。adjusted Bar 可作为可重建派生序列缓存，不必永久保存全市场多套；凡进入决策/指标的版本，永久保存 exact adjusted values/input refs 与复权元数据，保证重现。供应商只给 QFQ、不给可重现公司行动时，可保存当次完整窗口及其知识时点，不伪造通用 factor。当前 QFQ 历史不能直接作为多年以前“当时可知”的行情。

除权除息生成新的复权 revision/anchor 和受影响派生结果，不覆盖旧 snapshot。保留 raw 与公司行动观察，费用/持仓/计划调整由对应领域服务按冻结规则处理，行情 Provider 不自动下移止损。指数不假设具备股票复权，价格/全收益指数不可互换。QFQ 某些方法可能出现非正历史价格，不能套用 raw 正价格校验后偷偷删除；明确方法及适用性，必要指标不可判定则 UNKNOWN。

供应商 Bar 以 provider/source/method 区分并追加版本；canonical 选择 policy 固定且可追溯。相同逻辑 Bar 收到更正，新增 revision，旧引用不变。“最终 Bar”可被供应商更正，final 与不可修改混为一谈会毁掉审计。

### 10.1 时间边界与交易异常

[EXTERNAL DOCUMENT] 沪市股票竞价会话包含开盘集合竞价、上午/下午连续竞价和收盘集合竞价；不同标的另有特殊交易安排，不能从统一时间表推断所有证券规则。[上交所官方交易时间表](https://english.sse.com.cn/start/trading/schedule/)

以下为 canonical 规范化建议，须对目标交易所、标的和实际 provider 样本冻结，不声称供应商天然一致：

- UTC timestamptz 存时点，Asia/Shanghai 解释会话与 trading_date。分钟 Bar 推荐 end-label，覆盖约定为 `(bar_start,bar_end]`，首个交易点/拍卖成交分配有单独规则；查询使用§6的`start <= bar_start < end`，与Bar覆盖约定是两件事。
- 30m 按 09:30 与 13:00 分别锚定；60m 结束为 10:30、11:30、14:00、15:00，不能从午休跨接。1d 是实际交易日全部获准竞价会话，1w 按本地交易周实际交易日聚合，周未结束时非 final。bar_start/end 不表示午休也有交易；必要时保留 session segments。
- 开盘竞价虚拟参考价不是 last_trade；拍卖成交是实际市场事实。开盘成交如何纳入首分钟必须标明，收盘竞价成交纳入日线及末段分钟并注明；若 provider 口径不明或重复计量，不硬合成。盘后固定价格交易单独会话/规则，不默认并入常规 Bar。
- 停牌/无成交/未上市/假日/源缺段分别标原因；不为停牌伪造完整零量 K，也不前向填充伪装真实成交。UI 可用 whitespace 或明确缺口；所有零值须区分真零与 placeholder。
- 一字涨跌停可为 O=H=L=C 且 volume≥0，不能因此断言成交保证。是否限价、真实盘口、停牌和交易制度用有效期事实表达，T+1/可卖数量由账户/执行域读取。
- 1m 有完整 OHLC 与独立区间量额时才可聚合更长周期；5m 不能还原 1m，抽样 Quote 不能还原 OHLC。缺任一必需子段则 higher Bar coverage 不完整；不补零、不从累积量倒推已丢失的分钟分布。
- 未完成 30m/60m/日/周 Bar 只供标明 provisional 的观察；冻结生产门不能使用尚未 final 的输入。实时修订观察追加或短期暂存，决策引用及最终版本不可覆盖。

## 11. V1 实时等级与采集范围

用户本轮描述持仓 2 周—3 个月，主要日线/30m/60m 观察、偶尔尾盘执行；冻结策略不是高频。**推荐 30 秒基线 + 15 秒小范围关注 + 准入前按需刷新**，不推荐 Tick 或全市场秒级。

| 刷新等级 | V1 判定 |
|---|---|
| Tick / 毫秒 / 1秒 | 排除；不满足当前成本收益需求，也不能保证成交 |
| 5秒 | 非默认；后续真实用例和获准服务质量能证明必要时独立重审 |
| 15秒 | 持仓/待入场/用户当前关注与尾盘小集合；准实时观察 |
| 30秒 | 普通盘中 watchlist 的服务端批量缓存更新 |
| 60秒 | 非关注研究视图可降级；若关键输入超用途预算不能交易 |
| 盘后 | 日线/双指数完整窗口、公司行动与次日状态；核验最终性/缺段后发布 |

15 秒是采样周期，不是供应商时延 SLA，也不是连续穿越保护价必被捕获的保证。两次采样间价格可能触及又恢复；Bar high/low 有助事后识别但不能实时补造触发顺序。退出规则若要求更细时效，WP-RISK-01 必须评估真实样本与人工券商核对边界，不能因此直接给系统自动执行权。

先覆盖四只持仓、有限 watchlist 和沪深300/中证1000；四只上限是持仓规则，不是行情观察数量上限。20 个标的只是容量估算假设：240 分钟、30 秒、12 字段约 115,200 cells/日、576,000/五交易日；全部 15 秒翻倍，22 日约 5,068,800 cells，已可能超过官方免费 RQ 月度候选额度。此估算未包含历史、状态、重复、auction 与账户共享用量；以真实计费为准，不承诺免费可用。

调度是显式的单逻辑 scheduler 按交易日历发起 bounded batch，worker 执行；Dramatiq actor 自身不是定时器。使用现有 Redis/Dramatiq 但不引入新编排平台；采集租约/去重失败不得形成请求风暴。分钟段完结按需拉取并核验，日线收盘后有限重试；没有 final 不标完成。

## 12. 存储、修订与容量

| 对象 | PostgreSQL / 持久策略 | Redis / 可重建策略 |
|---|---|---|
| 日线 raw / 公司行动 / 日历 | 跟踪标的与双指数所需历史及修订永久保留 | 查询缓存，按版本 key |
| 分钟 raw | V1 优先 30m/60m 所需范围；1m 基础及1/5/15m按需。进入计划/复盘的窗口永久保留；非引用1m建议滚动180交易日，最终保留政策需合同批准 | 当前交易日/热窗口 TTL |
| Quote Observation | 成功采集观察在 DB 追加，建议非引用细粒度保存30交易日；决策/退出/告警引用、日终快照及其 inputs 永久；许可不足则不得启用该保存模式 | 最新 quote 只引用已提交 observation，TTL 到期不代表源数据突然缺失 |
| Market Snapshot / ActionDecision inputs | exact Quote/Bar/日历/质量/指标/规则版本、evaluated_at 永久；同一 as_of 多来源的时差明确 | UI 最新快照 projection |
| Provider Observation | 规范化数据、request/endpoint/来源/单位/时点/状态/错误预算；被决策引用永久。非引用 payload/log 可短期清理，凭据不保存 | 短期 health/quota 状态 |
| 指标结果 | 关键决策结果/输入 refs/参数版本永久；其他按需重算 | 以 dataset+indicator version 为 key |
| 原始大对象 | 必要且许可允许时 MinIO，PostgreSQL 保存 hash/identity；无须每个 JSON response 建对象 | 无唯一原始事实职责 |

这些是设计政策候选，不是迁移 schema。清理必须检查决策、退出、告警、复盘的exact引用及其**传递依赖**（指标原始窗口、聚合子Bar、复权与日历/选择政策版本等），以及授权保留义务；不能清理快照重现仍需的数据。所有仍保留的历史不得原地改写，只追加更正；被上述用途直接或间接引用的历史永久保留，其他非引用观察可按获批retention清理。latest projection可更新，不影响历史引用。历史回放按§8统一knowledge_valid_from选择当时可见revision/政策；observed/received/committed保留传输和提交证据，不能混用来提前可见。payload_hash独自不足重现，关键normalized values必须保存。

普通 PostgreSQL NUMERIC + B-tree，逻辑索引围绕 instrument/interval/adjustment/source/bar_end/knowledge_time；先以测量决定是否按月分区。不预建 Timescale/ClickHouse/pgvector 索引。假设20标的×240分钟×250日≈120万1m行/年，20标的30秒Quote约240万行/年；若每行含索引粗估0.5—1.5KB，仅这两类约1.8—5.4GB/年，payload/revision/备份另计。以有限范围和分级保留控制体量，不能凭“个人应用”宣称无成本。

发布顺序为 DB transaction 提交→Redis projection/fan-out；Redis 写失败不得伪造事实失败/成功。新逻辑较旧乱序观察不能覆盖 latest；source_time/版本单调规则需显式实现。丢失 fan-out 可通过 DB read 修复；V1 不为非关键 UI 每条 update 建复杂事件平台。

## 13. 技术指标层

建议 Market 内独立 `MarketIndicatorService`：纯确定性计算，输入为 exact Bar window + adjustment/calendar/算法版本，输出 Derived Market Signal；adapter 即使可给指标，也不直接决定交易状态。

| 阶段 | 指标 / 边界 |
|---|---|
| 最小 | 冻结双指数门所要求的精确日线计算；个股观察 MA5/10/20/60、Volume MA5/20、过去20完整交易日 high/low、raw 涨跌幅/振幅 |
| 按确有用途追加 | ATR14（明确 Wilder 等平滑/预热）、一个获准 EMA 周期；无需求不实现所有周期 |
| 延后 | 量比（须同交易时点历史基线与有效样本）、复杂支撑/压力算法、底部确认评分、多因子 engine |

MA_N 是 N 个有效完整交易日 close 的算术均值；Volume MA 不把停牌/缺失补成普通零交易日。前高比较窗口排除当前触发 Bar，标明 N、极值口径与 tie 处理；真实低成交零量与缺失不混淆。EMA/ATR 初始化和预热必须版本化。指标输入不足、mixed provider/adjustment 或 conflict 输出 UNKNOWN，不补零、不悄悄缩短窗口。

趋势/支撑/压力/突破/回踩/量能/底部确认不是天然客观单一标签。V1 可显示数值与人工计划标记；除冻结规则已有确定条件外，只作为观察。用户计划线绑定 plan_version 和 raw 坐标，derived 观察线绑定算法与复权版本。禁止因为新增 ATR/MA 或 60m 数据便修改 Setup B、RR、退出路径或启用“底部确认自动买入”。

## 14. API、K 线与 UI

[EXTERNAL DOCUMENT] Lightweight Charts 是金融图表库；官方教程提供 price/volume、price lines、series markers、MA、实时更新和 Vue 集成示例；官方仓库列出 Apache-2.0 及 NOTICE/TradingView 链接要求。[官方教程](https://tradingview.github.io/lightweight-charts/tutorials)、[官方仓库与署名说明](https://github.com/tradingview/lightweight-charts)

[EXTERNAL DOCUMENT] ECharts 官方提供多类型图表与 Handbook，candlestick 示例及组件目录包括 K 线、markLine、dataZoom 等组合能力；项目许可证为 Apache-2.0。[ECharts 官方 K 线示例](https://echarts.apache.org/examples/en/editor.html?c=candlestick-sh)、[官方组件目录](https://echarts.apache.org/en/builder.html)、[官方许可证](https://github.com/apache/echarts/blob/master/LICENSE)

| 需求 | Lightweight Charts | ECharts |
|---|---|---|
| 日/30m/60m K、分时、缩放/十字线 | 专用金融展示，数据周期由后端提供 | candlestick/line 配置可实现，金融交互需组合 |
| 成交量、MA、多窗格 | 对应 series / pane，后端提供指标 | 组合多个 series/grid/axis |
| 支撑、压力、止损、止盈、Pmax | price line / line series，坐标须一致 | markLine/series 类组合需针对最终版本验证 |
| 买点、Thesis、Catalyst | markers + 应用 tooltip/详情，绑定 exact 业务版本 | 标记/graphic/tooltip 组合，绑定版本要求相同 |
| 广度/组合/宏观多类型图 | 不是主要用途 | 更适合以后通用统计图 |
| 数据与指标 | 不提供 A 股数据许可、自动 MA、风险逻辑或完整交易终端 | 同样不能替代数据合同或领域服务 |

**推荐 V1 K 线用 Lightweight Charts**，理由是需求集中于价格/量/计划线/事件标记，当前前端未接入任一库，无 ECharts 既有投资需要兼容。复杂拖拽画线/持久化绘图工具不默认存在，另行按需评估。不得把开源库与 TradingView Advanced Charts/完整终端混为一谈。实施时锁定实际版本，5.x markers/API 与旧示例有差异，遵守 NOTICE；本轮不安装。[官方 v4→v5 迁移说明](https://tradingview.github.io/lightweight-charts/docs/migrations/from-v4-to-v5)

Market API 未来提供 bounded quotes/bars/intraday/quality/snapshot 查询，参数以 instrument_id、interval、adjustment、范围、分页定义；领域成功返回也包含质量与来源，MISSING 不是无说明空数组。前端继续使用 OpenAPI-generated client；thin facade 不手写业务 endpoint。SSE event schema 若未来采用，要有独立 typed contract 与运行校验，不能假设现有 generator 原生处理 EventSource。

V1 **先 REST 批量轮询**；Provider 请求数量与客户端页面数解耦。若证明多页面/延迟体验需要，再启用单向 SSE，带 event_id / observation_id、来源时点、freshness、重连后 REST snapshot 补齐、去重、丢事件/背压处理，鉴权与 nginx buffering/timeout 单独验收。行情推送与 Agent token stream 分离；WebSocket 暂无双向需求，延后。

UI 始终显示 source、截至时间、实时/延迟/休市、缺口、provisional、raw/QFQ/anchor；失效不能留绿色“实时”。research 模式可看 stale 图，交易请求必须重验当前有效快照。chart data 的加载顺序、重复/乱序修订、午休/停牌 whitespace、复权切换和计划 raw overlay 应覆盖实际浏览器验收。减少截图依赖是未来完整采集/展示链的目标，当前并未实现。

## 15. Market / Evidence / Thesis / Risk 边界

| 层 / 对象 | 负责 | 禁止混入 |
|---|---|---|
| Provider | 市场数据访问、字段原始语义和来源错误 | Pmax/RR/ALLOW、策略阈值、可卖账户事实 |
| Market Observation | 一次来源观察，如当前188.30、来源/时点/质量 | EvidenceVersion、Agent 观点或无依据实时声明 |
| Canonical Market Data | Quote/Bar/日历/状态及修订 | Research source quote、公司公告事实 |
| Market Snapshot | 某用途 exact inputs、derived indicators、质量和知识时点的不可变组合 | 缓存最新值替代历史引用 |
| Market Domain / Gate | 冻结双指数过滤、数据可用性、确定性市场计算 | 订单/账户限制、自动清仓、七阶段历史状态覆盖策略 |
| Evidence | 可定位来源文档的声明/事实及不可变生命周期，例如公司公告订单增长 | 每一价格采样、所有技术指标自动变 Evidence |
| Thesis | “订单增长可能推动未来两季度盈利”等可证伪命题，支持/反驳 exact Evidence refs | 行情裸数值、Provider/MCP 直接写 Thesis |
| Trade Plan | 版本化 Pmax、S0、T、保护价和退出路径；确切市场输入、费用/数量及用户接受 | Provider 内计算和动态随行情改写旧计划 |
| Risk Gate | 结合市场、计划、扣成本 RR、账户、持仓、订单、数量/产业风险、退出/纪律/确认决定动作 | 最新价单独视为许可、LLM自行 ALLOW |
| Execution / Account | T+1、真实可卖数量、未结/迟到/部分成交、broker 能力 | 仅凭 Bar 或 bid/ask 推断必成交 |
| Read-only Agent | 读取 exact snapshot、解释缺口、挑战和无副作用提案 | 直接 SQL/ORM/行情事实提交、订单、解除暂停/退出 |

“最近20日放量突破”属于 Derived Market Signal（算法与输入版本可追溯），不天然是 Evidence。“188.30 当前价”属于 Market Fact；公司公告订单增长属于 Evidence；盈利改善逻辑属于 Thesis。若以后某篇研究文档对行情提出声明，其原文经 Evidence 流程单独管理，声明再引用 Market Snapshot；不能倒过来把所有 Quote 塞进 WP04。

Market Snapshot typed reference 的未来消费合同需在 WP-05 / WP-RISK-01 重审，不改 WP04 当前 exact Evidence schema，不制造伪 Evidence ID。Market Data 自身不依赖 WP04 才能定义合同，但依照当前治理不得以技术独立性为理由打断主线。

freshness 与指数基础数据在 Market Data；指数过滤在 Market Gate；Pmax/S0/T 和保护价在 Trade Plan；RR/数量/账户承受力与最终动作在 Risk/Plan 的冻结计算边界。可执行性联合 Market 状态与 Execution 的可卖/券商约束；EXIT_PENDING 由退出/风险领域锁定，行情仅提供输入与客观市场限制。

## 16. 故障策略与未来必需验收

| 事件 | 行情层行为 | 新增风险 / 既有持仓 |
|---|---|---|
| iFind unavailable / timeout | bounded timeout/retry+jitter、熔断、失败 observation、保留旧 source_time | 合格辅源无则 NO TRADE；展示旧价并标失效，既有计划保留 |
| iFind rate limited / quota exhausted | 尊重 Retry-After、预算共享、降频非关键视图、不重试风暴 | 降频不能豁免 freshness，关键输入不合格则 NO TRADE |
| iFind auth expired / no entitlement | 明确鉴权/权限失败，安全刷新须符合供应商政策；无绕过 | 不拿 MCP token 猜测 HTTP 权限 |
| AKShare unavailable / upstream changed | adapter 隔离 payload、禁止误单位/缺字段上线；主源健康时继续 | 主辅都失败则 NO TRADE；不得自动装新版 |
| values conflict | 先校验可比性与来源家族，保留两方/版本和冲突原因 | 未解决关键冲突 NO TRADE；不平均、不偷偷换源洗冲突 |
| stale / source time missing / clock skew | 各用途重算质量，明确 STALE/UNKNOWN，旧快照不改时间 | NO TRADE；不得恢复旧 ALLOW |
| Bar missing / invalid OHLC / provisional | 保留 coverage 与原因；有限补数，禁止 fill previous 冒充成交 | 依赖窗口的 gate/indicator 不可判定 |
| trading halt / no liquidity / price limit | 保存有效期状态、raw行情、缺口；缺状态不猜 | 已知不可交易按冻结 gate 禁止新增；退出仍 EXIT_PENDING，记录约束不自动解除 |
| Redis unavailable | durable read，按负载降级 UI；缓存重建 | DB 可读且事实有效时风险门不依赖 Redis；否则 NO TRADE |
| PostgreSQL unavailable | 不发布未提交事实；写/读失败明确阻断、待恢复核验 | 关键事实不可核验 NO TRADE；通知/Agent 不成为替代真相 |
| queue backlog / out-of-order | source_time/received_at 检查、丢弃 latest 投影的落后更新，历史可保留 | 新 received_at 不救活旧 source；引用快照仍不可改 |

未来各任务至少按其触及边界验证：固定源样本单位/身份/缺字段（L1/L3）；真实 PostgreSQL 追加、更正、exact引用、并发/幂等（L4_DB）；获授权真实小集合盘中与收盘/除权/停牌观察（L4_RUNTIME）；时钟 skew、429、quota、timeout、partial batch、源冲突、缓存/DB/队列故障的 fail-closed；指标同输入同版本重算与当时可知 replay；UI provisional/freshness/raw-adjusted overlay（L4_BROWSER）。

没有 credentials / 许可 / 数据样本不能报生产 Provider PASS。Mock 接口测试不证明盘中 SLA；漂亮 chart 不证明风险闭环；业务正确性测试不证明策略盈利。本报告是预案，不作为这些验收的执行结果。

## 17. 拟议工作包与依赖顺序

当前 canonical 没有独立 Market Data WP：Market Gate 属于 WP-RISK-01，Instrument 主数据属于 WP-02。建议未来将数据技术切片登记为 **`WP-MARKET-DATA-01`（PROPOSED / NOT_DISPATCHED）**，作为 WP-RISK-01 的数据前置，不改 WP-01—08 或 Risk WP 编号。只有经正式批准并同步权威索引后才成为 canonical；本文只给候选，不生成正式派单或改任务板。

下表每项均为拟议验收要求；实现任务随后再按 SMALL contract 派单，不一次交付全模块。

| 顺序 / Task | 最小产物 | 依赖 | 关键验收证据 |
|---|---|---|---|
| MD-00 Contract / ADR review | 身份、时间、knowledge可见性轴、bar_start查询谓词、单位、复权、quality、scope、授权/预算、引用传递依赖retention、策略边界冻结 | 本预案；当前有效策略/OD-003、供应商尽调 | docs-only traceability；所有未知项有核验路径，无代码 |
| MD-01 Provider port / identity / calendar | 最小 typed capabilities、batch/error、exchange-aware mapping、版本日历/会话合同落地 | MD-00获批、WP-02边界；实施总体时机门 | 接口/身份冲突/假日/会话测试；不建第三空 adapter |
| MD-02 Quality / normalization core | 字段单位、source_time、freshness per use-case、conflict及provisional校验 | MD-01 | 纯计算失效/边界案例；引用现有冻结动作，不改阈值 |
| MD-03 iFind minimum server adapter | 获授权指数/股票日线、Quote、日历/状态与必要复权样本 | MD-01/02、当前账号/HTTP用途/预算/环境 | 真实小范围调用、timestamp/单位、429/auth/timeout；分钟支持可拆后续扩展 |
| MD-04 Historical raw daily persistence | 双指数及有限个股日线、修订/复权/knowledge-time窗口 | MD-02/03 | real PG约束、exact version/append-only、除权/缺段/重取幂等 |
| MD-05 Minimal indicator / Market Gate integration | 冻结双指数必需计算、exact Market Snapshot query | MD-04、WP-RISK-01获批领域合同；WP04/WP05核心完成 | 规则版本、窗口不足NO TRADE、日历用途、确定性重现；观察MA分开 |
| MD-06 Quote ingestion / durable snapshots / cache | 30s/15s bounded scheduler、成功观察存储、准入按需更新、DB→Redis | MD-02/03/04、freshness/retention政策获批 | 真实enqueue/consume、source age、旧缓存/乱序/队列积压、失效门 |
| MD-07 AKShare historical / bounded fallback | 经许可的有限历史补数，按能力用途显式切换 | MD-02/04/06、独立许可/质量证据 | 同语义验收、上游家族/冲突不消失、fallback失败NO TRADE |
| MD-08 Intraday Bars / aggregation | 30m/60m优先，必要1m基础及5m/15m、分时/周线 | MD-03/04、完整分钟样本与session/auction规则 | 午休/竞价/停牌/缺段/复权/final聚合；Quote抽样不得生成OHLC |
| MD-09 Market API / OpenAPI client | bounded typed quote/bar/snapshot/quality查询 | MD-04/05/06，分钟查询依赖MD-08 | OpenAPI drift、generated client、typed错误、范围/身份校验 |
| MD-10 Kline UI | Lightweight Charts日线/量/MA/raw计划线；分钟按需追加 | MD-09、WP-06读模型；分钟依赖MD-08 | L4浏览器真实数据、来源/freshness、复权/计划坐标、版本标记 |
| MD-11 Optional SSE | 单向更新、鉴权、reconnect REST恢复、去重/背压 | MD-06/09/10，实测证明轮询不足 | 多页面不重复回源、nginx/断线/丢事件，不依赖Agent流 |

MD-05 是本 WP 对冻结 Market Gate 的数据/查询集成切片；冻结 gate 实现与 final ActionDecision 仍归 WP-RISK-01，不能派两个 WP 各自维护一份策略。MD-07/08 不阻塞已有合格主源的日线/价格最小闭环；MD-09 可先做 daily/quote 的窄 API，分钟能力通过后另追加。通用 MA/量能观察随 MD-05/10 按需扩展，不为了 MD-11 新建 factor platform。

```text
Existing critical path (unchanged):
WP04 repair -> original WP04-02 reverify -> WP04-03/04 integration
            -> WP05 core -> WP-RISK-01 minimum deterministic loop

Proposed Market Data dependency branch (implementation only after review):
MD00 -> MD01 -> MD02 -> MD03 -> MD04 -> MD05 -------+
                           \-> MD06 --------------+-> Risk minimal market inputs
                                  \-> MD07 (conditional)
MD03 + MD04 -> MD08 -> MD09 -> MD10 -> MD11 (optional)
MD05 + MD06 --------> MD09
```

日线/Quote/状态作为 Risk 最小闭环必要输入，不等待完整 K 线 UI、第三源、Agent、Sector 或 Macro。完整 Market Data 全包不能变成 WP-RISK-01 的无限前置。MD-00 当前仅草案，正式合同审查需另派 docs-only 最小任务。

## 18. 时机：PARALLEL_DESIGN_ONLY

独立判断依据：行情是 Risk 的真实依赖，但当前仍有 Evidence fail 修复未关闭，Thesis 核心未实现，OD-003、数据授权/时效与复权未冻结。现在实现会同时引入供应商、时间序列、调度、时效和 UI 多个未验收边界，且不能解除当前 Evidence blocker。设计成本有限，能提前发现双指数/报价/计划坐标和外部数据门，因此选 **PARALLEL_DESIGN_ONLY**。

不选 NOW：尚未到获批实现条件；不选 NEXT：下一业务任务是 Evidence 最小修复，而非行情；不选纯 DEFER：身份/时效/复权/typed snapshot 设计现在可提前降低后续返工。若今后 Risk 开发排程已临近且数据许可长周期，先批准小范围供应商尽调可并行，仍不授权生产实现/采购。

重审门：WP04 原任务修复复验与 API/exact Evidence references 核心集成完成；WP05 核心验收；WP-RISK-01 Market/计划输入边界冻结；本数据合同/授权/预算/保留用途明确。重审后单独授权实施 MD-01 起的小任务。Sector 和 Capability Runtime 保持既有延后约束。

明确排除 V1：全市场毫秒 Tick、Level-2 全量盘口、高频撮合、Kafka集群、微服务拆分、ClickHouse仓库、分布式TSDB、CEP、超低延迟优化，以及自动交易/券商控制。不存在证据证明这些为当前必要需求。

## 19. TOP5 风险与未验证项

| 优先级 / 风险 | 影响 | 最小缓解 / 核验 |
|---|---|---|
| R01 P1：授权与额度不匹配 | 能查数但不能获准服务端保存/展示；免费额度超出、MCP与HTTP权限不同 | 获得具体账号/用途/字段/费用/保留和Agent转发确认；不作无限许可假设 |
| R02 P1：伪实时与会话状态不可靠 | 新收到旧价、无心跳、午休/停牌误判，错误放行 | source_time_kind、field quality、calendar/status有效期、端到端时效与故障样本 |
| R03 P1：复权/auction/Bar修订污染历史 | raw计划与QFQ图混坐标、历史重写、look-ahead | raw与派生分开，anchor/method/revision、exact snapshot与as_known_at重放 |
| R04 P1：fallback相关失效/质量漂移 | 东财双包装假独立、多源差异被平均、0开盘误采 | underlying_source、逐字段校验、有限补数与未解决冲突NO TRADE |
| R05 P1：范围/策略漂移 | 打断Evidence，把60m/新指标变生产门，把价格当Evidence | docs-only门、非canonical WP标记、冻结策略映射、独立验收及Repair First |

| Unknown / 假设 | 现状 / 核验路径 |
|---|---|
| U01 远程实时HEAD及新文件 | 当前访问失败；后续获可用网络只读ls-remote，再比较所需commits。不能在本文声称远程完整审查。 |
| U02 iFind实际账号、字段/时延/最终性/SDK环境 | 未提供账号证据；后续获授权小集合真实观察与供应商书面确认。 |
| U03 AKShare在本个人系统中的合法用途与质量 | 官方学术定位与MIT库许可不解决源数据用途；核实后才选择production fallback。 |
| U04 冻结市场门具体窗口/复权/计划价格规则 | canonical PRD/TAD明确边界但不复制阈值；MD00必须查当前有效个人模型合同，不猜公式。 |
| U05 15/30s与20标的/容量估算 | 基于用户持有期的设计假设，没有真实行为/延迟/容量证据；盘中/尾盘影子采样与使用试验。 |
| U06 candidate并发变化/剩余修复验证 | 有活动修改，无本轮复验；后续按其现有精确baseline contract独立验证，不能由行情任务替代。 |

## 20. 最小下一步、治理与交接

现在最小下一步是 **审阅本文中的 MD-00 决策清单**：确定Quote时间语义/用途、raw与QFQ、日历会话、关键字段/freshness候选、许可/预算和Scope；标明待供应商确认项，形成 docs-only Contract/ADR review。若仍无外部证据，保留 UNKNOWN，不能冻结未经证实的能力承诺。业务执行主线继续现有 `TASK-WP04-02-R1C-01`，不能据本文开始 MD01。

没有新增 `MARKET_DATA_DECISION_2026-09-15.md`：本轮用户授权预案而不是批准特定技术政策/正式WP，将未批准结论写成canonical ADR会混淆权威。必要时后续以实际批准结果另立决策。

治理摘要：Role=ARCHITECT/AUDITOR；Task Type=DOCUMENTATION/QUESTION_DIRECTED AUDIT；业务实施未派发；本轮Required Acceptance=L1_STATIC_REVIEWED，仅审计与文档覆盖，不能自批生产PASS。未来交易关键数据任务要求L3及真实DB/Provider/Browser证据，执行者只能报IMPLEMENTATION_COMPLETE，Verifier独立验收。No Evidence No PASS；FAIL→Repair First；不得改变WP04 candidate/verifier/阈值绕过主线。

后续AI执行简报：Current State=main无行情链、candidate修复进行中；Milestone=WP04有序修复；Critical Blockers=Evidence未闭环及数据许可/合同未确认（行情实施门）；Critical Path=WP04→WP05→Risk最小闭环及其行情分支；Safe Next Action=MD00 docs review；Acceptance=每个关键合同有来源/用途/失败语义和未验证项，零业务变更；Evidence Required=精确Git/source、官方政策、之后真实账号/采样；Do Not Assume=下面规则。

1. 不得把 unsupported claim 当成事实。
2. 必须尊重 Evidence Level（L0-L5），禁止跨级推断。
3. 必须尊重 Audit Scope（Included / Excluded / Partially Covered）。
4. `UNKNOWN` 不得自行推断填补。
5. `NOT_AUDITED` 不得解释为"不存在"。
6. `NOT_APPLICABLE` 不得解释为"未完成"。
7. `PROPOSED` / `DERIVED` / `INFERRED` 任务不得当作 `CANONICAL` 任务。
8. 同等级证据冲突时优先采用更新证据。
9. 遇到 Blocker，优先解除 Critical Path 上的关键依赖。
10. 不得绕过 `ACTIVE` Decision，除非有新的 Evidence / Decision。
11. Next Action 是基于证据的建议，不是未经验证的事实。
12. 如果报告与源码发生冲突，应重新验证源码，而不是盲信报告。

本轮NOT_AUDITED：远程实时内容、运行中的DB/Redis/worker/UI、真实账号/SLA、全产品业务验收、个人模型收益。NOT_APPLICABLE：在本轮文档任务中执行业务红绿测试/迁移/Provider安装。NOT_STARTED仅限本轮已覆盖代码的行情能力，不用于替代上述未知/未覆盖状态。

## 21. Portable Project State

```yaml
audit: AUDIT-MARKET-DATA-2026-09-15
mode: QUESTION_DIRECTED
project: ThesisGuard personal A-share cash-account risk OS
snapshot:
  local_main: 7d3734bc8346c16f9bbf7f7d9806309949c996de
  cached_origin_main: 7d3734bc8346c16f9bbf7f7d9806309949c996de
  remote_live_head: UNKNOWN
  candidate_head: bdd70edc153b6ed5def65ed99c41f325df45f066
  candidate_worktree: concurrent Evidence service/test edits observed
scope: documentation only; no business/provider/API/migration/frontend changes
market_data: NOT_STARTED implementation; partial infrastructure and design references
verification:
  repository: L1 static and fresh command observations
  live_openapi_in_memory: no market paths; three Research enum descriptions drift
  business_tests_runtime_production: NOT_AUDITED
decisions:
  timing_recommendation: PARALLEL_DESIGN_ONLY
  architecture: PROPOSED modular-monolith Market Data Gateway
  provider_primary: conditional iFind server HTTP
  secondary: AKShare research/history; entitlement and quality gates
  realtime: proposed 30s baseline, 15s focus, on-demand admission
  wp: WP-MARKET-DATA-01 PROPOSED; MD00-MD11 NOT_DISPATCHED
active_constraints: [Evidence repair first, frozen strategy unchanged, Sector deferred, Capability Runtime deferred]
risks: [R01, R02, R03, R04, R05]
unknowns: [U01, U02, U03, U04, U05, U06]
readiness:
  plan_review: READY_WITH_EXPLICIT_UNKNOWNS
  provider_production: NOT_READY
  market_risk_trading_loop: NOT_READY
next_action: MD00 documentation review; continue current Evidence repair priority
```

## 22. 证据索引与命令

取证日期统一2026-09-15；L0文档声明、L1源码/配置、L2构建、L3测试、L4真实运行、L5生产验证。本轮没有L2—L5业务验证。外部官方资料仅证明供应商/库公开说明，不能提升本项目证据级别。

| ID / type / level | Source | Supports | Does not prove |
|---|---|---|---|
| E01 GIT_STATE L1 | `git status --short`、`branch -vv`、`rev-parse HEAD origin/main`、`log -8`、`worktree list` | 本地refs、四份起始未跟踪文件、分支边界 | 远端实时/业务通过 |
| E02 SOURCE L1 | backend/instrument/models.py:21；services.py:19/141/169/188；api.py:17；migration 0002 | 主数据/catalog/查询持久化、symbol-only缺口 | 正式证券源或行情fallback |
| E03 SOURCE L1 | backend/market/__init__.py（1字节）；backend/common/redis_client.py:13/events.py:59/config.py:13/storage.py:16；apps/worker/main.py:19/23/43 | Market未实现、通用Redis/Streams/worker包装存在 | 行情actor/scheduler、消费者/推送/生产可用 |
| E04 SOURCE L1 | apps/web/package.json；package-lock.json；StockDetailView.vue:15；router/index.ts:25；src/api/client.ts | Mock价格、无图表依赖、generated client展示边界 | 真实行情/Kline/风险UI |
| E05 COMMAND/SOURCE L1 | apps/api/main.py:54；apps/web/openapi.json；现有Python环境`create_app().openapi()`内存比较 | 无行情路由、三个enum描述漂移 | 已启动API、api:check/build/test绿色 |
| E06 SOURCE L1 | backend/common/db/session.py/models_registry.py；migrations/versions/0001—0004；docker-compose.yml；requirements-api/worker；infra/nginx/nginx.conf | 存储/部署骨架、无行情table、非行情proxy设置 | DB迁移已运行、行情fan-out或async I/O全满足 |
| E07 GIT/SOURCE/DOCUMENT L1/L0 | candidate status/HEAD、main..candidate scoped diff；docs/acceptance/TASK-WP04-02-R1C-01-task-contract.md 与 baseline-independent-review | 候选service存在/并发修改、现有最小修复声明 | 该修复执行完成、本轮Evidence测试通过 |
| E08 COMMAND/EXTERNAL observation | 三种只读ls-remote尝试及GitHub Web失败 | 当前远端访问未成功，U01 | 远端HEAD、仓库权限或远端不存在 |
| E09 DOCUMENT L0 | README/AGENTS、canonical PRD/TAD、PRODUCT_GOAL_REALIGNMENT、ARCHITECTURE_REFERENCES、SECTOR decision、历史TAD §14/17/18、Agent proposals、HTML原型 | 策略/工作包/设计要求、文档漂移与历史参考 | 目录/原型对应业务实现 |
| E10 EXTERNAL DOCUMENT | §7/10/14每项旁的官方HTTP/SDK/AKShare/chart/交易会话链接 | 公开产品与库说明，规划的外部依据 | 本账号许可/SLA/真实性、项目接线或收益 |

关键当前命令：Git status/branch/log/worktree/ls-tree/scoped diff；`rg --files`与`rg -n -i`跨代码/文档检索；`wc -c backend/market/__init__.py`；在已有Python3.12中内存读取committed schema并比较create_app().openapi()（paths相同，三个enum仅description变化）。长/空白检索输出作线索，能力结论追到实际源码与注册/迁移，不拿无输出直接证明全仓不存在。

基线业务目录指纹（SHA256，按文件路径与内容、排除node_modules/__pycache__/.pytest_cache/dist；仅主仓）：backend=853fb6261ba60f232cef11b6a870227cc0edc416c3e9b20e25517b32d8e25e1a；apps=6a870191d01d3bdd59257aae0ec11ceb08cb7f59e66c2ef0214cfd34dd34f28d；migrations=a7eaf8c8fcf52bbcd9ba48d96d35ceb8487d4c6ef1f77f6bfa2b056553834faa；infra=70d41e92f2def571b9811e56f5b225f841b3b1b37da994487194946405f9bdbc。

首次交付检查已实际执行：上述四组指纹完全一致；git status仅多出本文，四份起始治理文件仍在；tracked `git diff --check` exit 0。另对未跟踪的本文做 `git diff --no-index --check /dev/null docs/MARKET_DATA_TECHNICAL_PLAN.md`，无空白diagnostic，exit 1是存在新增diff的状态，不能写成exit 0；Python逐行检查尾随空白为空，12个代码围栏成对。AST检查迁移create_table清单仅Instrument/Watchlist/Research/Evidence，无行情表。candidate活动文件不作本轮未变更承诺。

## 23. Fresh AI Handoff Validation

按定向审计压缩报告结构，模拟仅依赖本文的交接可答性（文档完整性检查，不是业务PASS）：

| 问题 | 仅凭本文答案位置 |
|---|---|
| 1项目是什么 / 2为什么存在 | §1风险与证据OS/可追溯纪律 |
| 3scope / 4milestone | §1/2/18/20，docs-only与Evidence修复 |
| 5Git snapshot | §2/21，远程UNKNOWN与candidate活动修改 |
| 6capabilities / 7已实现 | §3逐项及通用设施范围 |
| 8已验证 / 9低级证据 | §2/22，仅静态及当前schema观察，无新业务测试 |
| 10未审计 | §20末段明确列出 |
| 11blockers / 12risk / 13unknowns | §18/19，主线修复、R01—05、U01—06 |
| 14decision drift | §4，历史事实滞后但有效边界不变 |
| 15next action / 16不能假设 | §20，MD00草案review与十二条规则 |

交接可答性：`HANDOFF_READY`，表示上述16问题可从报告回答；远端、供应商账号、实际时效/许可及业务运行仍未知。本文未作独立业务验收，不输出Market Data生产PASS。

独立文档复核记录：review_market_data_plan仅阅读本文，首次提出保留/不可删除、knowledge可见性轴、Bar查询谓词三处一致性问题；修订§6/8/10/12/17后复核为`Approved — documentation completeness review`。该复核未读取其他仓库/网络、改文件或运行业务测试；只证明上述合同矛盾已澄清，不证明实际Provider、存储/风险链或候选政策已通过验收。
