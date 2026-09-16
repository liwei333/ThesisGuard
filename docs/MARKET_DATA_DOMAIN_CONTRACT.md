# Market Data / A 股行情领域合同草案 — MD-00

> Task: `TASK-MD00-CONTRACT-R1` · evidence cutoff: 2026-09-15 · local `main@7d3734b` / cached `origin/main@7d3734b` · live remote HEAD: `UNKNOWN`。
>
> Document state: **CONTRACT_DRAFT / PROPOSED**。静态文档收敛，不是已冻结的生产合同、APPROVED ADR、实现派发或行情能力。Market Data 当前 **DESIGN_ONLY / NOT_IMPLEMENTED**；Whole Product 仍 `NOT_READY_FOR_FULL_AGENT_BUILD`；策略 `UNPROVEN`。时序 **PARALLEL_DESIGN_ONLY**，不打断 Evidence 修复。

## 1. 范围、权威与本轮结论

本合同承接 [技术预案审计](MARKET_DATA_TECHNICAL_PLAN.md)，将身份、时间、报价与 K 线、复权、质量、可用性和冻结策略输入写成可验收语义。下文“必须”表示**草案内的设计约束**，须经 MD-00 后续正式决策采纳；已经冻结的交易规则则来自下列原文，不因本合同而变化。端口/记录名称均是文档概念，不代表已有 Python schema、表或路由。

项目权威按 [AGENTS](../AGENTS.md)、[产品目标](PRODUCT_GOAL_REALIGNMENT_2026-09-14.md)、[技术架构](ThesisGuard_V1_Technical_Architecture_Design.md) 与 [架构权威映射](ARCHITECTURE_REFERENCES.md)。WP-04 以 [Evidence 冻结合同](WP04_EVIDENCE_DOMAIN_CONTRACT.md) 为准。市场数据质量不得改写其生命周期或 Evidence freshness。

冻结规则核对使用只读重定位原文（原 skill 指向的旧路径已不存在，已搜索并核对下列文件）：

- [个人模型 v1.3](../../tradingModel/last/ThesisGuard_个人交易模型_v1.3_个人适配草案.md)：§4、§5、§6。
- [个人系统 v1.1](../../tradingModel/IterationRecord/个人交易系统_v1.1_基于ThesisGuard_v1.3.md)：§3–§5、§7–§10，尤其统一数据约定、Setup B 表、盈利保护、公司行动和精确持仓区间。
- skill 的 `references/personal-trading-policy-v1.3.md` 只作交叉索引；不能因为相邻目录存在新的系统候选而切换本项目冻结版本。

本轮收敛：Provider 与决策域分离；原始事实/修订可追溯；时间与区间语义明确；观察图与委托尺度可核实转换；新鲜度、可信度、区间覆盖和动作准入独立。**15 秒轮询不能证明过去没有触及保护价**，必须把监控覆盖作为单独资格条件。账号授权、因子历史、finality、冲突阈值、留存和知识发布机制仍待关闭，见 §12。

## 2. 当前基线与不应继承的 PASS

本轮 main 与缓存 origin 引用均为 `7d3734bc8346c16f9bbf7f7d9806309949c996de`。上一轮真实远程核验受 proxy / DNS / 网络阻断，本轮没有新远程成功证据。当前 `backend/market/__init__.py` 只有空模块占位；没有 Quote/Bar 持久化、Market API、Provider adapter、行情 worker、确定性 Market Gate 或 K 线组件。Instrument/Watchlist/Research/Evidence 的已有 bounded slices 不等于行情实现。完整代码证据保留在前一轮预案，不能把本文件写成实现证据。

本轮又读到其他任务的 [R1C-01 验收](acceptance/TASK-WP04-02-R1C-01-acceptance.md) 和 [R1C-02 合同](acceptance/TASK-WP04-02-R1C-02-task-contract.md)。前者的 PASS 仅限 latest-first eligibility 修复，后者仍是后续 Evidence 状态机修复。本轮未执行其中任何测试；WP-04 仍 `PARTIALLY_IMPLEMENTED`，candidate 保留未提交修复。本任务既不改写上一轮审计历史，也不改写上述材料。

## 3. 模块和 Provider 合同边界

未来建议在模块化单体的 `backend/market/data/` 内实现 Gateway。它负责采集、归一化、来源策略、时点查询与质量评价，**不**计算订单准入、修改保护价或直接提交交易状态。Market Gate、Trade Plan、Portfolio、Discipline 是确定性消费者；Agent/UI 只能读取或形成无副作用提案。

| 边界 | 允许责任 | 不得承担 |
|---|---|---|
| Provider adapter | 账号能力声明；来源标识映射；异步 I/O；字段、时间、单位和错误归一化；提供原始响应引用 | Setup B、ALLOW、账户阈值、自动回退掩盖异常 |
| Gateway | 批量读取；完整性/质量；版本化来源选择；缓存；事实修订；knowledge 时点查询 | 改 Evidence lifecycle；把最后一次成功价当当前可买价 |
| 纯指标函数 / domain evaluator | 基于明确 dataset 的确定性计算与输入版本引用 | 在指标内部调用 Provider、隐式补数据、用 LLM 填缺失 |
| Market / Risk / Trade Plan | 按冻结政策判断并保存 decision inputs 和原因 | 从 UI 图形颜色、Provider 名或 FRESH 自动取得交易权限 |
| PostgreSQL / MinIO / Redis | PG 耐久事实与引用；MinIO 原始响应且受授权限制；Redis 可丢失缓存/通知 | Redis/RAG/通知成为唯一财务事实；每个 Quote 强制产生 EvidenceVersion |

端口建议：`capabilities()`、批量 `get_quotes(instrument_ids)`、`get_bars(instrument_id, interval, start, end, adjustment, as_known_at)`、`get_intraday(...)`、`get_calendar(...)`、`get_exchange_session(...)`、`get_instrument_status(...)`、`get_adjustment_metadata(...)`。分页、超时、请求预算和部分成功必须显式。目标间隔为1m（分时）、5m / 15m / 30m / 60m / 1d / 1w，逐账号逐间隔声明覆盖，不因日线可用就宣称分钟/周线可用。capabilities 是**该账号当前实测或待核验声明**，含支持证券/市场、间隔、历史覆盖、延迟、字段、数据授权用途、批量与限额、采样/事件覆盖、时间及公司行动语义；函数存在不能当能力核验。

iFind 服务端 HTTP 是有条件的首选候选；Linux SDK、账号权限、储存/展示/衍生/重演权和资源预算必须实测。iFind MCP 交互查询不能据此认定适合后台持续采集。AKShare 是研究/历史及有条件备用候选，软件 MIT 不等于数据授权；东财直连与 AKShare 东财接口不能算独立来源。两者都不是本项目已获准/已接入的生产源。官方资料与上轮核验局限见 §14。

## 4. 身份、日历、单位和稳定性

证券主键使用 Instrument 的稳定 `instrument_id`；每次归一化附 canonical identity `{symbol, exchange, instrument_type}` 与 `provider_symbol` / mapping version / 有效期。三个身份字段不能只靠字符串或 symbol 推断。现有唯一约束 `(symbol, exchange)` 与 symbol-only lookup 不是完整跨品种主数据合同，后续 MD-01 必须审查迁移和碰撞；本轮不修表。不假设上证指数、深证证券、ETF 与板块指数共用代码命名。

身份、交易日历、交易所 session 与单证券状态分开：交易所正常交易不代表证券未停牌；休市不等于 Provider 故障。日历有版本、来源、发布日期、取得与知识可见时点。日索引按登记交易所交易日，不能用自然日、Provider 返回行号或浏览器本地时区替代。停牌、无成交、缺失保留状态；不以人工补零、前值填充或跳过缺失缩短窗口来满足指标。

存储时间统一 UTC，展示和交易日映射指定 `Asia/Shanghai`，包含明确 offset；日期字段是日历交易日而非 UTC date 截断。午休、集合竞价、临时停市、节假日与各类证券 session 以已核验、版本化日历为准；不在本文替项目账号断言交易权限。30/60 分钟不得跨午休拼接；竞价是否进入第一根/最后一根、时间标签等须通过 MD-00-OD-04 fixture 对账才可派发该覆盖。

价格使用十进制定点 / Decimal，并按 instrument_type 声明单位：股票/ETF等证券报价为 `CNY/share`（每股/每份），指数level为 `points`（点），不能将指数点位当作元/股或套用股票金额/委托公式。股票/ETF成交量标准 `shares`（股/份），成交额标准 `CNY`，保留原始单位、换算及供应商对量的调整方式；指数的量额/换手字段仅在来源有明确、已核验的统计定义时提供，不支持时为null及原因，不借个股定义填充。不能全市场按 100 股/0.01 元报价处理；最小申报量、增量、tick、涨跌幅/可卖限制是证券级、有效日级参考事实，核验另有职责。金额不能从 `close×volume` 伪造供应商成交额。真实零、不可用 null、无成交与 Provider 哨兵值分开。

## 5. Quote、Bar 与错误记录的最小语义

### 5.1 QuoteObservation（不可默改的观测事实）

必须含 observation/revision 身份、instrument identity、provider/底层来源、source revision（如有）、原始响应引用/内容 hash、采样/事件类型、四类时间（§6）、知识可见时点、交易日/session 及原始字段映射版本。每项价格/量可为 null，但附缺失/不可用原因，不能省略后由前端推断零。

价格字段至少区分 `last_trade_price` / `last_trade_time`、`previous_session_close_raw` 与 `session_reference_price`。供应商“昨收”可能是除权后的涨跌幅参考，不得自动等同上一日真实成交收盘；字段含义未核实时标 UNKNOWN。bid/ask、日高低、累计量额、换手率、涨跌停边界仅在该账号有可信字段且语义明确时提供，不因 UI 需要编造。换手率标准为ratio（0.01=1%），保留源百分比换算、分母流通股口径与有效时点；分母不可核实时不能自己用过期股本补算。采样 Quote 的字段不等于连续逐笔成交序列。

附 quality evaluation 与 source conflict group 引用；质量评价可以另行修订，不修改观测本身。正常停牌价、昨日最后成交价可用于带状态的观察，不能直接用来认定实时执行资格。异常 observation 保留用于审计，与“查询完全未返回”区别记录。Provider feed snapshot 是来源采样类型；耐久 decision snapshot 是固定exact inputs/版本引用的决策记录，两者不得混名或互相替代。

### 5.2 BarRevision（带 finality 与 lineage 的修订事实）

必须含 instrument、来源、interval、`bar_start`、`bar_end`、交易日/session、OHLC、volume/amount（及单位）、adjustment mode/方法/anchor/factor dataset、source revision、原始引用、知识可见时间、归一化版本、状态与 revision lineage。唯一身份要包含来源、间隔、调整尺度和版本，不能只 `(symbol, date)` 覆盖旧行。精确表/索引和幂等键由后续持久化合同冻结。

分别表达 `PROVISIONAL / FINAL / UNKNOWN` finality、`VALID / INVALID / UNKNOWN` 结构质量及缺失原因；这些是新行情概念，**不是** WP-04 enum。闭市不自动 FINAL；时钟走到 15:00 或抓到一行不算完成日线。需 Provider final marker 或已核验发布策略/对账机制，之后仍允许 correction 新 revision。FINAL 不是永不修订。周线覆盖依登记日历与Provider周标签核验，不把每周五固定当最后交易日；由日线聚合时保存所有成员revision、聚合版本和同尺度量额规则，未完成成员或未完周不能宣称完成周线，也不能替代冻结日线窗口。

结构检查在同一尺度中进行：`high≥max(open,close,low)`、`low≤min(open,close,high)`，合法非负量额、身份与交易日/session 可解、重复/逆序/缺口显式；没有 open 的分钟行不能填 last/0 伪装完整 OHLC。不静默删除错误行后把图/窗口宣称完整。

### 5.3 返回错误与部分成功

每个证券/时间范围给独立成功或结构化错误：权限、限额、超时、断线、schema 变化、身份不明、覆盖不足、源时间不明、复权不可核实、冲突或系统故障。批量部分成功不能把失败项复用上一份成功数据而不披露。重试遵从账号预算与幂等；切源必须产生新的 dataset / 选择版本，记录原因并重新评估消费者。

## 6. 时间、知识可见性和区间查询

| 时间轴 | 精确定义 | 禁止的替代 |
|---|---|---|
| `source_time` + `source_time_kind` | 来源声明的 market event / feed snapshot 时间，时区与精度明确 | 网关 now 替代；把最近成交时间当 feed 更新时间 |
| `observed_at` | adapter 收到完整响应的时点 | 请求开始；行情发生时点 |
| `received_at` | Gateway 收到归一化 observation 的时点 | 能证明报价仍有效；历史当时已知 |
| `committed_at` | 耐久写入完成的提交确认时点 | 事务开始 / INSERT 默认 now；收包时点 |
| `knowledge_valid_from` | 耐久、可查询的首次发布可见时点，**不早于提交完成** | source/observed/received/source 发布时间作为自动可见时点 |

同一系统可验证的 observed→received→commit→publish 顺序以及 source 的时区/未来偏移必须有校验；跨进程时钟偏差不能只靠时间戳证明发生顺序，偏差不可解释为 UNKNOWN。source 无时间/种类时不能生成“新鲜”结果。feed heartbeat 更新且 last_trade_time 很老要分开判断：无新成交不等于断流，feed 更新时间也不证明 last price 对拟交易可用。

`as_known_at=K` 只选择 `knowledge_valid_from≤K` 的事实、revision、因子、映射、日历、来源选择与政策版本，再在该可见集合中依照当时可见的 selection policy 选 canonical revision。不存在可见记录就 UNKNOWN/MISSING；不以后来补录数据伪装当时可知。有效日期（例如除权日）与知识可见日期独立；source 发布时间早并不能把今日本地补录变为昨日已知。本项目实际摄取前的历史数据只能属于事后 historical replay，不能冒称本项目 operational as-known 数据。

语义已收敛；**发布机制尚未选型**（OD-05）：须能证明 commit completion 后的 durable publish，消除崩溃窗口、排序/并发与历史 backdating。若机制不能证明该轴，时点查询保持 UNKNOWN；不得先以 INSERT 时间代用。decision snapshot 同时固定查询 K、实际 exact dataset / revision refs、输入发布日期及 policy / evaluator 版本；重演不得“重新查询今天最新结果”替换输入。

Bar 查询统一请求半开区间 `[start,end)`，**选取谓词 `start≤bar_start<end`**；条自身的标准覆盖表示 `(bar_start,bar_end]`，展示 `bar_time=bar_end`。返回完整选中的条，不能默截 OHLC 到 end，也不能声称返回条覆盖恰好等于请求区间。若调用者需要严格覆盖，必须提供 interval-aligned 边界或单独校验/拒绝不齐边界。

例：60m 条 start=09:30、end=10:30，查询09:30–10:30包含它；查询09:31–10:30排除它；查询09:30–10:00仍按谓词包含完整60m条并披露其结束时间，不能假装只到10:00的数据。历史决策可见性与 finality 另行过滤，未来/尚未完成条不因 start 在范围内而进入生产信号。分页 cursor 使用稳定排序键（bar_start + 唯一 revision identity + 固定 dataset/查询 K），不得用展示 end 混选导致重复/遗漏；图形 clipping 不改变服务谓词。

## 7. 原始价、复权与公司行动合同

DB/API canonical 原始事实用 `adjustment=NONE`；观察 K 线可默认**显式 QFQ**，显示模式、anchor、方法、版本和 as-known。HFQ 可选观察；没有已核验因子不开放对应模式。QFQ 不是当前 raw order price，股票 OHLC、MA、极值和比较阈值必须处在同一来源、同一 adjustment dataset 与同一经济价值尺度，不能拼接未说明的来源/公司行动处理。

复权元数据保存公告/权益事实引用、有效日、每原股权益、source/knowledge 时间、factor dataset / revision、provider 公式及 anchor。QFQ 历史会随 anchor 和公司行动改变；不能拿今日 QFQ 曲线重演过去已知因子。供应商只提供今日调整序列而没有历史可见因子时，标 `PIT_UNSUPPORTED`，可事后观察但不能作精确 as-known 验证。

从信号 L / Close(t) 或保护/目标阈值转换到执行日 raw 必须具备可核实的 exact 输入、有效日、方法和因子/权益 dataset，保存原值、转换结果、报价取整与引用。不能假设 QFQ 只有一个通用比例或用最新 raw/QFQ 比值替代现金分红/送转的处理。公司行动跨信号/订单/持仓时，S0、Pmax、T、有关数量与 RR 的协调由确定性域负责，Provider 只提供事实与核实转换；旧原始 q0、Entry0、S0、r0、R0 和历史不覆写。

固定 tick 的 S0 输入契约沿用冻结规则 `tick×[ceil(L_raw/tick)−1]`；L_raw=50.00、tick=.01 得49.99；L_raw=50.004得50.00。不能只 floor 把恰为合法价格的 L 原样当严格下方。实际 tick 和合法价格域须证券级核实。新保护价比较双方先换到同一经济尺度，“数值下降”不自动等于人为放宽；公司行动转换不能被 Agent 自行批准。

## 8. 新鲜度、可信度、覆盖与用途资格

`MarketDataQualityEvaluation` 是独立结果，建议字段：`temporal_status={FRESH,STALE,MISSING,CONFLICTING,UNKNOWN}`、`verification_status`（有依据/未核验/无效的独立概念）、source age、feed/成交时间、finality、结构异常、conflict、coverage、policy version 和 reason codes。此处 UNKNOWN 是**行情计算结果**，不是向 WP-04 Evidence freshness 加 enum；Evidence 仍为 `VERIFIED / UNVERIFIED / STALE / CONFLICTING / MISSING`，其 verification lifecycle 也保持原冻结状态。

FRESH 只表示对**指定用途与政策**的时间条件合格，不表示 Evidence VERIFIED、不保证结构/复权/覆盖、不等于 ActionDecision ALLOW。MISSING=所需事实不存在；UNKNOWN=事实/时间/语义/机制不足以判断；CONFLICTING=不可消解的决定性来源/修订冲突；STALE=有可解释时间且超过用途时效。结果保留各轴原因，不因其中一个“正常”掩盖其他轴失败。临界 inclusive/exclusive、时钟偏差和 conflict 规则由 OD-03 冻结。

| 用途 | 最低可用输入 | 不满足时 |
|---|---|---|
| UI / Agent 观察 | 来源/时间/模式可披露，last-good 可带状态；无交易许可 | 显示延迟/停牌/不可用，禁止装作当前实时 |
| 双指数 / Setup B | 完成日线、足够登记交易日、同源同尺度、可见版本、无决定性缺失/冲突 | evaluator UNKNOWN；不准新增风险 |
| 拟入场价格核验 | raw有效行情、当天证券/session、时间和限价/尺度可信、信号未失效与区间覆盖足够 | NO TRADE / UNKNOWN；不得靠 last-good 放行 |
| 退出触发观测 | 可信有效价/已核验范围证明触及当日有效保护价，事实与时点保留 | 已知触及仍交域处理；缺失/断流列异常，不推断“未触及”或清除已触发退出 |
| 精确 MFE/MAE / TIME_DECAY | 首次入场后至最终退出的真实覆盖和公司行动尺度 | 近似/范围/UNKNOWN，不能用入场前当天高点或退出后低点伪装精确 |

**区间覆盖独立于最新价时效。** 每个覆盖 claim 给起止时间、粒度、event/snapshot/range 类型、完整性、序列/缺口、交易时段、价格尺度、knowledge 与授权依据。15秒/30秒轮询只有采样点；最新价高于 S0 不能证明期间从未触及。可靠 range low≤S0 可证明发生触及；要以 range low>S0 证明未触及，须核实它完整包含所需区间且尺度一致。供应商从开盘累计最低价不天然等于“首次入场后最低价”；当日高低也不能推断同条内先后序。

结构失效监控窗口从 t 收盘确认到初始建仓结束；事件采集覆盖不足、断线或延迟回补时，未失效资格不能直接恢复为肯定结果。迟到的真实触及 observation 保留事件/知识时间，由冻结域处理失效和在途成交；不 retroactively 改写已存在决策输入。本合同不授权自动撤单或卖出，不控制券商；“覆盖可证明”的技术/运营方案与用户退出能力登记由 OD-02 关闭。

前一轮建议刷新30s、重点15s、拟单on-demand，UI源年龄60s / 准入30s，以及 Quote30交易日/1m180交易日留存，均仍 **PROPOSED，未成为批准政策**。不能写死进生产规则，也不能把 nominal refresh 当 SLA / 最坏延迟 / 监控覆盖承诺。

## 9. 冻结策略输入映射与最小历史窗口

以下是已有 v1.3 / v1.1 规则的输入合同，不在 Provider 内实现，不提高风险、不恢复排除的60分钟确认，也不证明策略优势。

| 冻结消费者 | 必须提供并保存的输入 | 边界 / UNKNOWN 情况 |
|---|---|---|
| 双指数 gate | 沪深300、中证1000身份；拟入场日前一完整交易日各 Close 与60个完整日收盘、SMA60、dataset/calendar/evaluator版本 | 两者均严格 Close>MA60；一项不足/未完成/冲突为 UNKNOWN；市场过滤失败本身不自动卖旧仓 |
| Setup B 趋势 | t 的 Close、SMA20、SMA60与 SMA20(t−5)，同源同尺度完成日线 | `Close(t)>MA20(t)>MA60(t)` 且严格斜率；不拿盘中值确认 |
| p / L / d 与缩量 | t−20…t−1 High，同高最近 p且p≤t−2；p+1…t−1 Low同低最近 d；MA20(d)；回踩均量与p−19…p均量 | 幅度3%–12%含边界，位置±3%含边界，回踩均量≤参照均量；缺失不能择早极值凑 PASS |
| 收盘确认 / 窗口 | Close(t)>High(t−1)，完成/知识时点、登记日历 t+1 | 仅t+1入场；盘中突破 READY；不能补旧信号到t+2 |
| S0 / Pmax / T | L与Close(t)转换到执行日raw的 exact输入；tick；T独立证据；同尺度报价 | S0严格下方合法价；Pmax≤converted Close(t)×1.01；S0<价≤Pmax；费用后RR由风险域计算，不能从2R反推T |
| 永久信号失效 / 盘中退出 | t收盘确认至建仓结束的可信触及事实与覆盖；当前持仓当日有效保护价；事件/知识时间 | 曾触及或跌破即进入冻结失效/退出处理；反弹不恢复；缺行情不造未触及；挂单不等于成交 |
| 流动性金额上限 | 此前20个完整交易日日成交额CNY、质量和dataset | `q×P≤mean_amount20×0.005`，不拿手数作金额；计划数量、成本由风险域核算 |
| 盈利保护 | 启动日j的completed Close(j)、已换算至j的 Trigger2=Entry0+2r0；生效日k开盘前的k−5…k−1完整Low、tick、同尺度旧有效保护价 | j收盘首次≥启动后永久记录；首次生效k=j+1，窗口为j−4…j（含启动日），以后每生效日k仍用k−5…k−1，在开盘前换算至k并保存；五日低点严格下方合法价、max只上移；不足保留仍有效已核实旧安排，暂停新价计算，不伪造 |
| TIME_DECAY / MFE / MAE | 第1持有交易日、10日历交易索引、入场后精确区间覆盖、当日已换算0.5r0阈值、实际成交时段 | TIME_DECAY标签不自动卖；窗口不足UNKNOWN；入场前/退出后当日极值排除，bar内先后无法确定不能宣称精确 |

信号 t 有**至少60个连续登记交易日且均满足所需有效性的完成日线**时，才能覆盖 MA60(t)，同时覆盖 MA20(t−5)所需25日、最早p=t−20时参照均量最早t−39以及MA20(d)。不因为斜率5日就误要求 MA60(t−5)，也不把60条跳过停牌/缺口的返回行等同60个登记交易日。上市不足、停牌或任一所需窗口缺有效日线为 UNKNOWN；不得用占位填充或让“最后60有效行”改变冻结日索引。指数同样需完成60日窗口；盈利保护独立需此前完整5日，成交后区间分析另需精确时段。

指标输出均带 evaluator version、完整 input dataset/revisions、calendar、adjustment、finality、as-known、状态/原因；UI 可画均线/保护/目标标记，但不重新计算或改写生产事实。30/60m K线和指标仅观察，不能把预案展示需求变为被冻结规则排除的60m入场确认。

## 10. 耐久事实、缓存、引用与留存

建议 PG 存 raw日线/公司行动/日历与引用、指标结果及决策数据集，分钟数据按需求和成本分层；MinIO 存获授权的原始响应/文件；Redis 缓存 Quote / query与fan-out，TTL 不能作为金融可见性、freshness、版本或留存依据。缓存键至少含 instrument、source/dataset、interval/range、adjustment anchor/revision、as-known与quality policy；丢缓存不得丢 decision snapshot。缓存回源不得自动跨源/跨尺度替换。

对仍保留的 observation/bar/指标，correction 追加 revision 和原因，不覆写旧数据。不是要求所有无引用行情永久保存：非引用Quote/分钟候选30/180交易日只供后续留存政策评审，删除必须按获准策略、可证明无引用且留下清理批次记录。任何被决策、订单/退出事件、告警、争议、复盘**直接或传递依赖**的精确 inputs、因子、来源选择/规则版本、归一化方法与必要原始材料须保留到足以重演和审计；不能只留一个结果hash却删掉其依赖。授权不允许必要持久化时该数据用途不得启用，不能一边宣称永久可重演一边依赖会消失的第三方链接。

future schema 须明确 revision、唯一键、幂等、知识发布、snapshot 引用和 retention pinning 并通过真实 PostgreSQL/并发/故障验收；本合同不创建空表。Evidence 模块与 Market input refs 在决策链中按明确 exact identities 连接，不把每个报价机械摄取为研究 EvidenceVersion，也不允许 Market writes 绕过 Evidence Domain Service。

## 11. 必须转入实施验收的反例清单

这些是**未来测试/实测要求，本轮没有执行 Provider、DB、API或UI测试**。实施任务需按 scope 选 L1–L4并独立验收，不能继承本轮静态 PASS。

| ID | 可构造情形 | 预期可观察结果 |
|---|---|---|
| MD-T01 | 返回昨日quote，今天received/committed | 原source_time保留，不能借现在收包成为FRESH；last-good观察带状态 |
| MD-T02 | feed更新时间新但last_trade_time老；source_time缺失/未来偏移 | 两种时间分别披露；无可信源时间或时钟偏差不可解释为UNKNOWN |
| MD-T03 | 同symbol跨exchange/type；批量一项无权限 | 身份碰撞/失败独立；不能错配或拿上一证券结果替代 |
| MD-T04 | 60m09:30–10:30，start/end不齐与分页 | 按§6三例和bar_start谓词一致；完整条不冒称截断；固定dataset分页不漏重 |
| MD-T05 | 午休/竞价标签、1m缺open或哨兵0、停牌缺口 | session fixture对账；不可造OHLC/补零/跳日凑均线 |
| MD-T06 | 15:00闭市但源仍provisional；隔日correction | 不能用于完成日线确认；新增revision，旧引用不被改写 |
| MD-T07 | t后公司行动/因子今日补录；过去as_known_at查询 | 未来knowledge数据/选择policy排除；不可用则UNKNOWN；事后重演明确标识 |
| MD-T08 | durable写入后发布前crash，跨进程乱序或backdated INSERT | 不早于commit的发布轴仍可证明或不可见/UNKNOWN；不泄漏未发布事实 |
| MD-T09 | QFQ L恰50.00与非格50.004、现金分红跨执行 | raw换算可核实，S0取49.99/50.00；S0/Pmax/T数量协调；缺因子禁止新增 |
| MD-T10 | 轮询间低穿S0后反弹；迟到低点、日低含入场前时段 | 采样无连续证明为UNKNOWN；可信触及保留并交域永久失效；MFE/MAE不伪称精确 |
| MD-T11 | 两来源price冲突；切源恢复；AK东财与直连同底源 | 无silent fallback；保留原冲突与新dataset/selection；不虚称独立佐证 |
| MD-T12 | 新鲜但无权限/尺度不明；Evidence UNVERIFIED；Market FRESH | 三类状态独立；FRESH不映射VERIFIED/ALLOW |
| MD-T13 | 重复high/low择最近日、3/12%和±3%/≤量边界，少一天MA | 与冻结表一致；缺窗口UNKNOWN，不择日/改边界凑PASS |
| MD-T14 | j日2r0收盘启动后回落；首次j+1窗有更早/启动日不同低点；5日low缺失；市场gate失败旧仓 | 启动不取消；首次窗j−4…j、以后k−5…k−1，在生效日开盘前保存；不伪造新保护价/下移；市场失败不自动卖出；已触发退出不消失 |
| MD-T15 | Redis flush、并发correction与dataset查询、候选过留存期 | 事实与exact快照可重建；固定查询可重复；被传递引用的数据不能清理 |
| MD-T16 | 超时/429/配额耗尽/权限撤销/源schema变化 | 有界重试；部分失败、freshness与coverage降级；阻断新增，原异常可审计 |

## 12. 待关闭项与关闭证据（不能用文档存在关闭）

| ID | 待确认决策 / 负责人角色 | 所需关闭证据 | 未关闭的影响 |
|---|---|---|---|
| MD-00-OD-01 | 数据账号授权、服务模式与成本 / 用户账号持有人+架构师 | 项目账号权限与限额、后台Linux/HTTP实测、展示/缓存/耐久/衍生/历史重演用途的明确授权材料；脱敏留证 | 不可接生产；不能认为购买某产品即自动包括所有用途 |
| MD-00-OD-02 | “曾触及”与退出监控覆盖 / 领域负责人+用户 | 采样/逐笔/range覆盖语义与边界、断线/回补fixture、从t确认到建仓结束及持仓时段的可信覆盖方案、延迟预算、用户监控/退出能力登记 | 最新quote只能观察；无法证明未触及为UNKNOWN，最小风险闭环不能宣称已满足 |
| MD-00-OD-03 | 质量策略与冲突规则 / 领域负责人 | 用途级source/feed/last-trade age、session差异、clock skew容差、冲突阈值与价格尺度、临界包含关系、告警/阻断政策版本及用户批准 | 60s/30s只是建议；不批准生产自动准入 |
| MD-00-OD-04 | 证券映射、session、bar finality与单位 / 数据工程+领域负责人 | 两指数/代表股票ETF账号样本；竞价/午休/停牌/除权/收盘修订对账；NONE/QFQ/HFQ和量额单位的golden fixtures | 未核验身份/间隔/finality不得给生产信号 |
| MD-00-OD-05 | durable knowledge发布机制 / 架构师 | 机制ADR草案评审、commit→publish可证明顺序、crash/并发/backdating/factor补录验收；统一facts/policy选择 | 不得承诺精确operational as-known；不可用时UNKNOWN |
| MD-00-OD-06 | PIT公司行动与执行日换算 / 数据工程+领域负责人 | 当时可见factor/公告覆盖、provider方法和anchor，跨现金分红/送转样例与真实raw对账，exact转换可重复 | 图形只观察；尺度不可核实时NO TRADE；不据今日QFQ证明历史策略 |
| MD-00-OD-07 | retention、引用依赖与容量 / 用户+架构师 | 30/180候选成本测算、授权约束、传递pin规则、删除批次/恢复与审计要求、明确批准的版本化留存策略 | 不启用自动删除；不许删已引用依赖；未授权耐久用途不启用 |
| MD-00-OD-08 | 合同正式冻结与实施拆包 / 架构师+独立Reviewer+用户 | 上述critical项按拟实施用途关闭；写入明确批准的ADR与authority map；独立合同验收；每包allowed scope/DoD与主线排序批准 | `WP-MARKET-DATA-01` / MD-01…仍PROPOSED，不是当前派发 |

具体实现可按用途裁剪关闭集，例如先验证日线不必已完成SSE/30mUI，但必须明确禁用尚无资格的拟单/监控用途。所有生产用途共同需要账号授权、身份/单位、质量策略、耐久事实/知识发布与必要尺度语义。不得用“先做最小闭环”省掉冻结规则需要的触及覆盖或退出能力。

## 13. 时序和可派发条件

已批准的主线仍是 WP-04修复/服务/API和WP-05核心后接最小WP-RISK-01；WP-RISK-01产品/领域设计可并行。MD-00此时仅静态合同准备，与 Sector / Capability Runtime 当前延后决定一致：不实现Sector评分、空表、Provider Runtime或Agent调用层。

后续建议顺序：MD-00正式合同/ADR → MD-01身份/端口/日历 → MD-02质量归一化 → MD-03获准iFind最小采集 → MD-04完成日线耐久 → MD-05最小指标/Market输入；MD-06 Quote/cache与**区间覆盖验证**满足拟实施用途后，才可能接风险域。AKShare备用、分钟/30m60m、API/K线UI以及SSE按条件拆包。完整图表不是最小风险闭环前置；新鲜Quote和完成日线也不足以单独证明完整闭环。

Lightweight Charts维持前一轮观察K线优先候选，ECharts为一般多图可选。库版本、归因/NOTICE、Vue生命周期、时间映射、raw/QFQ标识与数据缺口必须在真正UI任务前核验。客户端绘图、标记与均线不提供正式决策事实，不允许直接改Trade Plan。

本轮 MD-00**文档交付**可通过独立 L1 静态验收；MD-00**生产合同冻结**仍未完成。下一步可继续关闭OD（授权/覆盖/样本实测等需要实际账号和独立合同任务），但不得仅凭本轮PASS启动adapter、表、API或修改冻结规则。实现前须再建立bounded task-contract及独立验收，代码/DB/Provider/API验证按具体任务选择，不沿用文档PASS。

## 14. 官方资料与证据限制

以下沿用2026-09-15前一轮技术预案核验，**本轮未重新连源/调用账号**。外部文档不证明项目权限、可持久化权、实际覆盖、延迟、finality或PIT因子可用。

- iFind [开发手册](https://quantapi.51ifind.com/gwstatic/static/ds_web/quantapi-web/help-center/manual.html)、[FAQ](https://quantapi.51ifind.com/gwstatic/static/ds_web/quantapi-web/help-center/faq.html)、[权限说明](https://quantapi.51ifind.com/gwstatic/static/ds_web/quantapi-web/help-center/permission.html)：前两项上轮官方搜索索引可见、direct open timeout；不据索引/通用权限表替代账号实测。公开接口能力/额度只是候选核验线索。
- AKShare [股票数据文档](https://akshare.akfamily.xyz/data/stock/stock.html)、[介绍与数据使用说明](https://akshare.akfamily.xyz/introduction.html)、[官方仓库](https://github.com/akfamily/akshare)：上轮核到分钟范围、复权/单位/字段差异与公开网站变动风险；仍需逐接口与项目用途核验。
- Lightweight Charts [官方仓库与NOTICE](https://github.com/tradingview/lightweight-charts)、[官方教程](https://tradingview.github.io/lightweight-charts/tutorials)、[v4→v5迁移](https://tradingview.github.io/lightweight-charts/docs/migrations/from-v4-to-v5)；ECharts [官方candlestick示例](https://echarts.apache.org/examples/en/editor.html?c=candlestick-sh)与[LICENSE](https://github.com/apache/echarts/blob/master/LICENSE)。只作为前一轮库候选证据，不是项目已集成证明。

## 15. 交付与验收归属

[不可变任务合同](acceptance/TASK-MD00-CONTRACT-R1-task-contract.md)约定本轮范围和五项blocking AC；[独立验收记录](acceptance/TASK-MD00-CONTRACT-R1-acceptance.md)由Reviewer在审查最终内容后写入。结论范围只能是 `L1_STATIC_REVIEWED`。本文件不是WP-04实现记录、策略盈利证据、生产数据政策批准或账号采购建议执行记录。
