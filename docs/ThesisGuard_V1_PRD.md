# 论衡 ThesisGuard V1 产品需求文档（PRD）

> Version: 2.0-draft
>
> Updated: 2026-09-14
>
> Status: **PRD_DRAFT**
>
> Product Direction: **APPROVED**
>
> Strategy Validation: **UNPROVEN**
>
> Whole Product: **NOT_READY_FOR_FULL_AGENT_BUILD**
>
> Canonical decision: [PRODUCT_GOAL_REALIGNMENT_2026-09-14.md](PRODUCT_GOAL_REALIGNMENT_2026-09-14.md)

## 1. 文档目的与权威边界

本文定义 ThesisGuard V1 的产品定位、目标用户、能力优先级、MVP、成功指标、假设和验收边界。它不代表功能已经实现，也不是个人交易模型的启用登记。

权威顺序：

1. 个人交易模型 v1.3 / 系统 v1.1 对已冻结策略参数和动作语义具有最高权威；
2. 产品目标调整决策定义目标、优先级、MVP 和工作包依赖；
3. 本 PRD 定义 V1 产品需求；
4. canonical TAD 定义技术边界；
5. 领域合同定义其工作包实现合同；
6. proposal、历史审计和验收报告不自动成为当前实现事实。

如本 PRD 与冻结策略在阈值、Setup、退出、暂停恢复或 `ActionDecision` 上冲突，必须标为 `CONFLICT` 并提交 Open Decision；不得静默覆盖。

## 2. 产品定位

### 2.1 North Star

> **ThesisGuard 是一套面向个人 A 股现金账户的、证据驱动的风险与决策操作系统。它通过不可覆盖的研究证据、投资逻辑、市场状态、账户风险、交易计划与纪律记录，帮助用户避免无法承受的错误，并以可审计的前瞻数据验证个人交易方法是否存在扣除成本后的优势。**

产品口号：

> **先活下来，再用可验证的数据判断自己是否具有优势；Agent 服务于纪律与证据，而不是替代纪律与证据。**

### 2.2 产品承诺

产品直接承诺提供的能力是：

- 将关键决策建立在带来源、时点、freshness 和版本的证据上；
- 在关键数据缺失、过期、冲突或无法核验时，对新增风险 fail-closed；
- 让账户、持仓、订单、计划、退出、纪律和规则历史可追溯；
- 让用户能区分模型问题、执行问题和客观限制；
- 用前瞻、扣成本记录评估交易方法，而不是用事后故事证明方法。

产品不承诺收益、胜率、回本、年度盈利、稳定跑赢指数、准确预测危机日期或任何单笔交易结果。

### 2.3 品牌表达

“论”代表 Thesis、事实、来源、产业逻辑与可证伪判断；“衡”代表账户承受力、市场环境、机会成本、仓位与纪律。`Guard` 守卫的是决策边界和投资逻辑，不是守住某只股票或拒绝止损。

## 3. 目标用户与非目标用户

### 3.1 Primary user

- 个人 A 股现金账户用户，使用自有资金、不使用杠杆；
- 主动股票持仓有限，研究和执行能力受个人时间约束；
- 愿意在交易前明确 Thesis、证据、失效条件、风险预算和计划亏损；
- 愿意每日维护或导入账户、持仓、订单与成交数据；
- 希望用真实费用和前瞻数据判断方法是否值得继续；
- 能接受系统拒绝交易、要求补数据或反驳自己的观点。

### 3.2 Non-target user

- 要求系统自动下单、控制券商、代替确认交易意愿或承诺收益的人；
- 追求高频、分钟级、杠杆、多市场多资产或社交跟单的人；
- 不愿提供账户/订单/证据，却要求确定性 `ALLOW` 的人；
- 希望 AI 根据自然语言临时改变风险阈值、保护价或暂停状态的人。

## 4. 产品方法论

### 4.1 Thesis First

每个新主动交易必须有版本化 Thesis、支持与反驳证据、下一验证日期和明确证伪条件。没有 Thesis 的标的只能观察，不能进入交易许可。

### 4.2 Fact > Narrative

系统必须区分：客观事实、来源、推断、市场预期、用户假设、Agent 提案。LLM 输出不能直接成为 Evidence 或系统事实。

### 4.3 Risk Before Opportunity

决策顺序是：账户硬限制与退出事件 → 未结订单与持仓真相 → 市场过滤 → 研究与 Evidence → Setup → 价格数量与空间 → 用户确认。不能从“公司不错”跳到“可以买”。

### 4.4 Immutable History

Research、Evidence、Thesis、Trade Plan、订单、成交、退出、告警、纪律、暂停恢复和规则版本不得原地覆盖。修正通过新版本、关联和审计记录完成。

### 4.5 Deterministic core, LLM only proposes

账户状态、回撤、风险预算、订单预占、Evidence freshness、市场过滤、交易准入、退出状态、纪律事件和暂停恢复由确定性领域服务计算和提交。Agent 读取结果、解释缺口并生成提案。

## 5. Product Outcome Hierarchy

| Outcome | Meaning | Ownership |
|---|---|---|
| Survival | 避免无法承受的错误继续扩大 | Product-owned |
| Decision integrity | 输入有效、动作可复现、结果可追溯 | Product-owned |
| Discipline | 计划、执行、违规和暂停不被盈亏改写 | Product-owned |
| Method validation | 前瞻判断是否存在扣成本优势 | Product observes and supports |
| Financial result | 盈亏、回撤、超额收益 | Observed; never promised |

## 6. V1 Capability Priorities

### 6.1 P0 — Personal Risk OS

P0 是 V1 生存内核，必须在 Agent 之前形成可靠、可读取、可测试的边界。

#### 账户与净值

- 账户单位净值；
- 外部出入金中性化；
- 当前回撤与历史高点回撤；
- `AccountState`；
- `PauseStatus`；
- `RecoveryEligibility`；
- `NewRiskPermission`。

#### 持仓、订单与券商事实

- 当前持仓、可卖数量；
- `NEW_ACTIVE / LEGACY_PRE_MODEL / LONG_TERM_ETF` 分类；
- 未结订单、部分成交、拒单、撤单待确认和迟到成交；
- 订单对现金、市值、主动风险和产业风险的预占；
- T+1、停牌、跌停、跳空、流动性和券商能力限制。

#### 风险与组合

- 单笔风险预算；
- 主动持仓风险 H；
- 单股市值、权益总市值；
- 同产业与共同风险因子；
- 个人股票最多 4 只；第五只执行 Position Replacement PK。

#### 退出与纪律

- 价格退出、逻辑退出、时间复核；
- 退出触发后锁定 `EXIT_PENDING`；
- 计划外新增、超数量、摊低成本、扩大止损/预算和拖延退出等违规；
- 账户暂停、有限恢复与恢复周期耗尽；
- 盈利不抹掉违规，亏损不自动证明模型错误。

#### 市场与数据门

- 拟入场日前一完整交易日的沪深300和中证1000过滤；
- 行情、账户、Research、Evidence、券商能力和事件 freshness；
- 数据 `MISSING / STALE / CONFLICTING` 或不可核验时禁止新增风险；
- 每日盘前、盘中、盘后核对。

### 6.2 P1 — Research, Evidence and Thesis

P1 负责决策的可引用事实基础：

- `SourceDocument / SourceDocumentVersion`；
- `EvidenceSeries / EvidenceVersion`；
- `SourceLocator / SourceGrade / VerificationStatus`；
- Evidence freshness；
- `ResearchPackage / ResearchModule`；
- `ThesisVersion / ThesisValidation`；
- Bull/Base/Bear、预期差、证伪条件、Catalyst；
- 增量更新与不可覆盖历史。

### 6.3 P2 — Read-only Agent

Agent 是推理、解释和提案层，不是风险或金融事实的 System of Record。

Agent 可以：

- 读取结构化事实，解释研究、市场、账户、持仓和纪律状态；
- 找出缺失、过期、冲突资料并要求核验；
- 提出支持或反驳 Thesis 的证据；
- 生成研究、交易计划、复盘和长期记忆提案；
- 比较候选股票和当前持仓；
- 提醒风险、纪律、下一验证日期和必要用户确认。

Agent 不可以：

- 直接提交订单、控制券商或自主调仓；
- 自行修改风险阈值、Trade Plan 或策略版本；
- 自行解除暂停或把恢复资格映射成 `ALLOW`；
- 将自然语言或 LLM 输出直接写成 Evidence、账户状态、成交事实；
- 在关键输入未知时给出无条件 `ALLOW`；
- 自动形成长期风险偏好；
- 通过聊天覆盖冻结保护价或历史。

### 6.4 P3 — Macro Risk Sentinel

#### Stage 1: Basic Policy & Market Alert

- 监控权威官方政策来源；
- 识别融资保证金、担保物折算、融资融券、流动性、准备金、资本约束、跨境融资、房地产、地方债和程序化交易变化；
- 保存原文、来源、发布日期、生效日期、适用对象和影响路径；
- 结合市场价格、市场宽度和流动性确认；
- 只映射是否允许新增风险、是否需要账户风险复核；
- 不输出未经校准的危机概率。

#### Stage 2: Systemic Risk Sentinel

- 信贷/GDP 缺口、债务偿付率；
- 企业、居民和政府杠杆；
- 房地产信用周期；
- 银行与非银金融风险；
- 跨境债权、外币债务和美元流动性；
- 信用利差、估值、波动率、融资和流动性；
- 多资产相关性与去杠杆压力；
- 历史回放、误报、漏报和提前量评估。

宏观输出表达脆弱性、风险累积和压力升级，不把单一指标解释为确定性股灾。初期优先限制新增风险，不凭一个宏观分数自动清空已有持仓。

## 7. V1 MVP Core Scenarios

V1 MVP 只以以下三个核心场景形成闭环。Research/Evidence/Thesis 是场景依赖，不再把“与 Agent 讨论一只股票”单独当作 MVP 完成。

### SC-001 — 盘前风险检查

#### User goal

每天盘前知道账户是否安全、风险门是否可进入、有哪些必须先处理的事实。

#### Required output

- 当前 `AccountState / PauseStatus / RecoveryEligibility / NewRiskPermission`；
- 是否允许进入新交易全量检查，而非直接 `ALLOW`；
- 未处理的 `EXIT_PENDING`；
- 未结订单、撤单待确认、迟到成交和部分成交；
- 每只持仓可卖数量和当日有效保护价；
- Research、Evidence、行情、账户、订单或券商能力的 freshness；
- 今日 Must Do / Must Not Do。

#### Acceptance boundary

关键账户、持仓或订单输入无法核验时，必须为 `AccountState=UNKNOWN` 或有效暂停态，且 `NewRiskPermission=PROHIBITED`。Agent 不得补造缺失事实。

### SC-002 — 新交易准入

#### User goal

在新增主动股票风险前获得可复现、扣成本、考虑账户全局状态的检查。

#### Required gates

1. Research 与 Evidence 对当前决策可用；
2. 前一完整交易日沪深300和中证1000市场过滤通过；
3. Setup B 为 `TRIGGERED`；
4. `Pmax / S0 / T / q_plan`、费用和申报约束齐全；
5. 当前计划数量的扣成本 RR 通过；
6. 当前账户风险、现金、权益市值和订单预占允许；
7. 股票数量上限允许，或第五只已完成 Position Replacement PK 且名额真实释放；
8. 用户明确接受计划亏损并最终确认。

#### Decision contract

```text
AssessmentStatus = COMPLETE / UNKNOWN
ActionDecision = ALLOW / NO TRADE / MANAGE_ONLY / EXIT_PENDING / NOT_APPLICABLE
```

不得增加新枚举。准入失败、判断未知或用户不接受计划亏损时，新增风险必须 `NO TRADE`。

### SC-003 — 持仓退出与复盘

#### User goal

退出发生或交易结束时，知道什么触发、什么受客观限制、模型与执行分别如何表现。

#### Required output

- `EXIT_PENDING` 与剩余可卖数量；
- T+1、停牌、跌停、跳空、拒单、迟到成交、部分成交和流动性限制；
- `EntryClass = MODEL_IN / MODEL_OUT / UNCLEAR`；
- `Execution = COMPLIANT / EXECUTION_ERROR / UNKNOWN`；
- 实际净盈亏；R0 完整可核验时才有 `R_net`；
- MFE/MAE 及其数据口径；
- 纪律违规、Pause Event 或整改项；
- 模型问题、执行问题和客观限制分列。

#### Acceptance boundary

盈利不能抹掉违规；亏损不能自动修改模型；事后资料不能补造成事前证据；历史 Trade Plan 和成交记录不能覆盖。

## 8. Personal Trading Model Frozen Boundary

当前个人交易模型 v1.3 / 系统 v1.1 保持冻结且 **UNPROVEN**：

- 新主动交易只验证 Setup B；Setup A、Setup C、60 分钟确认、做 T 和其他分支不进入生产准入；
- 市场过滤使用拟入场日前一完整交易日的沪深300与中证1000；
- 研究、市场、价格数量、空间、退出事件、账户执行意愿六项全部通过；
- 关键输入不可判定时 `AssessmentStatus=UNKNOWN`；用户请求新增风险时 `ActionDecision=NO TRADE`；
- 股票持仓最多 4 只，第 5 只必须 Position Replacement PK；
- 不用杠杆、不摊低成本、不下移保护价；第一轮不主动加仓、不做 T；
- 订单预占现金、市值和风险；撤单未终结、迟到成交未核清前不释放；
- 退出触发后使用 `EXIT_PENDING`；
- D 对应 `WARNING / CONTRACTED / PAUSED_DD / RECOVERY` 的阈值和恢复规则不变；
- 旧仓与长期 ETF 单列；历史不可覆盖。

本 PRD 不复制或重定义冻结数值。任何参数、买点、退出路径、恢复或账户额度变化必须另立策略版本、回放、前瞻验证并获得用户批准。

## 9. Domain and State Boundaries

### 9.1 Sources and Evidence

来源文档与 Evidence 分开。一个来源可以有多个不可变版本；同一事实系列可以有多个 Evidence 版本；locator 必须能定位到原文。Source grade 不等于真实性，verification state 不等于 freshness。

WP-04 的详细合同以 [WP04_EVIDENCE_DOMAIN_CONTRACT.md](WP04_EVIDENCE_DOMAIN_CONTRACT.md) 为准。该合同是 `CONTRACT_ONLY`，不得被解读为 Evidence 实现已存在。

### 9.2 Research and Thesis

Research Package 聚合可复用 Research Modules。Thesis 必须引用 Evidence 版本并保存自身版本、验证记录、支持/反驳关系、下一验证日期和证伪条件。Bull/Base/Bear 是情景表达，不是目标必达或自动交易信号。

### 9.3 Account and Portfolio

账户单位净值用于表现和回撤，账户金额用于当下预算。外部出入金只改变份额，不重置策略启用点、高点、暂停或恢复周期。旧仓与长期 ETF 进入全账户风险，但不被伪装成新模型交易。

### 9.4 Orders and Trades

信号、计划、订单、成交、持仓和退出状态分开。未结订单持续预占；撤单请求不等于撤单完成；迟到成交必须回到账户与持仓真相。一个完整交易生命周期使用一个 TradeID，不能通过拆 ID 绕过限制。

### 9.5 Market

V1 新主动交易的生产过滤遵守冻结的双指数规则。旧的七阶段情绪状态机和示例仓位区间是历史设计素材，除非产生独立策略版本并获批，不得覆盖冻结账户/市场门。

### 9.6 Discipline and Notification

纪律事件、暂停、恢复、整改、告警投递、确认和失败重试均可审计。通知只是传递机制，不是金融事实或风险状态的唯一真相；通知失败不能改变领域状态。

## 10. Daily Operating Loop

```text
盘前：账户/持仓/订单/退出/保护价/freshness → Must Do / Must Not Do
盘中：按冻结计划执行 → 记录委托、成交、拒单、客观限制与退出
盘后：对账 → 更新单位净值、回撤、风险、保护价、Evidence 与次日计划
周期复盘：纪律、模型、成本、资金占用、市场状态与规则版本
```

盘前/盘中/盘后任何时点发现账户、未结订单、主动风险或退出状态未知，都必须阻止新增风险，直到事实核清。

## 11. Product-Owned Success Metrics

| Metric | Target direction | Baseline / current measurability |
|---|---:|---|
| 交易前计划覆盖率 | 100% | PLANNED；UNKNOWN baseline |
| 账户日终对账完整率 | 100% | PLANNED；UNKNOWN baseline |
| 关键 `MISSING / STALE / CONFLICTING` 错误放行次数 | 0 | PLANNED；UNKNOWN baseline |
| 计划外超数量次数 | 0 | PLANNED；UNKNOWN baseline |
| 人为扩大止损次数 | 0 | PLANNED；UNKNOWN baseline |
| 人为扩大风险预算次数 | 0 | PLANNED；UNKNOWN baseline |
| 人为拖延退出次数 | 0 | PLANNED；UNKNOWN baseline |
| 未知持仓或未结订单时新增风险次数 | 0 | PLANNED；UNKNOWN baseline |
| 历史交易计划覆盖或删除次数 | 0 | PLANNED；UNKNOWN baseline |
| 规则变更版本覆盖率 | 100% | PLANNED；UNKNOWN baseline |
| ActionDecision 到规则版本和输入快照可追溯率 | 100% | PLANNED；UNKNOWN baseline |
| 决策关键 Evidence 来源与时间戳完整率 | 100% | CONTRACT_ONLY；UNKNOWN baseline |
| 告警去重、送达、确认和失败重试 | 每事件可审计 | PLANNED |
| 数据源中断时 fail-closed 正确率 | 100% for new-risk gates | PLANNED |

## 12. Trading Outcome Metrics

以下仅用于观察和决定策略是否值得继续：

- 扣费 Expectancy、Profit Factor、胜率、平均盈利 R、平均亏损 R；
- 最大回撤、当前回撤、回撤恢复时间；
- 相对沪深300全收益表现与匹配账户权益比例的现金/权益基准；
- 分 Market Regime、产业、持有期、退出类型表现；
- 资金占用、滑点、真实费用；
- 信号频率、未成交和失效信号；
- 宏观告警命中率、误报率、漏报率和提前量；
- 对用户时间、情绪和主业的影响。

10 笔只做行为检查，30 笔做阶段评价，50 笔以上才开始更系统的参数研究。样本节点不证明盈利，不自动提高风险预算。单笔盈亏不能触发策略修改。

## 13. Assumption Register

| ID | Content | Type | Impact | Uncertainty | Current evidence | Validation | Success | Failure / stop | Status |
|---|---|---|---|---|---|---|---|---|---|
| A-001 | 严格风险门改善真实交易行为 | Value | P0 核心价值 | High | 无前瞻行为数据 | 比较计划覆盖、违规和错误放行 | 计划覆盖 100%，关键违规趋近 0 | 持续绕过或维护成本过高 | UNVALIDATED |
| A-002 | 用户愿意每日维护/导入账户、持仓、订单、成交 | Usability | 账户可信度 | High | 无连续使用证据 | 30 个交易日试用 | 日终对账 100% | 持续缺失导致错误或大量 UNKNOWN | UNKNOWN |
| A-003 | 数据源及时、合法、稳定且可负担 | Feasibility | 所有事实门 | High | 无正式 provider/SLA/许可 | 数据源选型和故障演练 | 满足时效、许可、成本并能 fail-closed | 长期不可得或成本/法律不可接受 | UNKNOWN |
| A-004 | 只读 Agent 足以形成长期价值 | Value | P2 投资 | Medium | 仅 proposal | P0/P1 后做任务完成率和留存试验 | 提高缺口发现与复盘完成率 | 增加负担或诱发绕过 | UNVALIDATED |
| A-005 | Setup B 在费用、滑点和不同市场状态下正期望 | Value / Feasibility | 策略继续与否 | High | 定义冻结，无足够前瞻样本 | 回放→模拟→小预算登记 | 净 Expectancy/风险支持继续 | 成本后为负或风险不可接受 | UNPROVEN |
| A-006 | 宏观预警比简单市场过滤有额外保护 | Value | Stage 2 必要性 | High | 无对照数据 | 影子告警对照 | 降低错误新增风险且误报可接受 | 无增量价值 | UNPROVEN |
| A-007 | 宏观误报不会导致长期错误空仓或频繁改计划 | Value / Usability | 机会成本和纪律 | High | 无行为证据 | 回放+影子告警 | 干扰与误报在阈值内 | 高频误报或用户失去信任 | UNKNOWN |
| A-008 | 用户在亏损、踏空或连损时不会绕过系统 | Usability | 纪律闭环 | High | 无前瞻证据 | 违规与暂停日志 | 重复违规下降且可整改 | 持续绕过关键规则 | UNKNOWN |
| A-009 | 手工、文件或只读同步足以保证券商对账 | Feasibility | 风险状态准确性 | High | 无路径验收 | 多渠道对账和迟到成交演练 | 日终 100% 对账 | 差异无法及时解释 | UNKNOWN |

## 14. Current vs Target State

Evidence cutoff：2026-09-14，`main@bd4b1d7`；开始修改前 worktree clean。

| Capability | Current | Target |
|---|---|---|
| Engineering skeleton | IMPLEMENTED locally | maintainable foundation |
| Instrument/Watchlist | PARTIALLY_IMPLEMENTED | validated data/user boundary |
| Research Package | Capability `IMPLEMENTED`; verification evidence: targeted backend L3 `VERIFIED`; overall quality-gate result `UNKNOWN` | reliable P1 container；修复既有 OpenAPI artifact drift |
| Evidence | CONTRACT_ONLY on main | versioned source/evidence implementation |
| Thesis | DESIGN_ONLY / NOT_STARTED | evidence-linked immutable Thesis |
| Personal Risk OS | DESIGN_ONLY / NEEDS_DOMAIN_DESIGN | deterministic P0 MVP kernel |
| Research UI | PLANNED | three-scenario decision workspace |
| Agent | DESIGN_ONLY / PLANNED | read-only explanation/proposal layer |
| Incremental Update | PLANNED | source-to-revalidation flow |
| Macro Alert/Sentinel | PLANNED | staged, calibrated risk signal |
| Forward Validation | PLANNED | versioned production governance |

`codex/wp04-evidence-persistence` 分支存在未合并的 WP-04 persistence foundation；它不改变 `main` 的 CONTRACT_ONLY 状态，也不能在合并与重新验证前写成 canonical 当前能力。

## 15. Work Packages and Dependencies

既有 WP-01 至 WP-08 不重命名、不覆盖、不重新编号：

| WP | Historical identity | Current observed state |
|---|---|---|
| WP-01 | Engineering Skeleton | IMPLEMENTED local skeleton |
| WP-02 | Instrument + Watchlist | PARTIALLY_IMPLEMENTED |
| WP-03 | Research Package | Capability `IMPLEMENTED`；verification evidence：targeted backend L3 `VERIFIED`；overall quality-gate result `UNKNOWN` |
| WP-04 | Evidence | CONTRACT_ONLY on main; implementation next |
| WP-05 | Thesis Engine | DESIGN_ONLY / NOT_STARTED |
| WP-06 | Research UI | PLANNED |
| WP-07 | Read-only Agent | DESIGN_ONLY / PLANNED |
| WP-08 | Incremental Update | PLANNED |

新增：

| WP | Purpose | Dependency |
|---|---|---|
| WP-RISK-01 | Personal Risk OS | WP-05；产品/领域设计可提前并行 |
| WP-ALERT-01 | Basic Policy & Market Alert | WP-08 + WP-RISK-01 |
| WP-MACRO-01 | Systemic Risk Sentinel | WP-ALERT-01 + validation data |
| WP-VALIDATION-01 | Forward Validation & Model Governance | cross-cutting; full evaluation follows prior WPs |

```text
WP-01 → WP-02 → WP-03 → WP-04 → WP-05 → WP-RISK-01
      → WP-06 → WP-07 → WP-08 → WP-ALERT-01
      → WP-MACRO-01 → WP-VALIDATION-01
```

Agent UI 可提前原型化，但不得当作风险闭环完成。Macro 不阻塞最小交易风险闭环。前瞻验证口径必须随生产规则设计，而非最后补写。

## 16. V1 Out of Scope

- 自动下单、自主调仓、券商客户端控制；
- 高频、分钟级、做 T、第一轮主动加仓；
- Setup A、Setup C、60 分钟确认和未经验证的多买点；
- 杠杆、借款、亏损摊低成本；
- 多市场、多资产全面覆盖；
- 复杂多 Agent、社交投资、收益排行榜；
- 自动在线学习和自动修改生产策略；
- 精确预测股灾概率或危机日期；
- 为所有 A 股同时生成完整深度研究；
- 任何稳定盈利、回本、胜率或超额收益承诺。

## 17. Validation Plan

### 17.1 Product validation

- 用真实日常流程验证 SC-001/002/003 是否减少遗漏和绕过；
- 记录完成时间、缺口、用户手工负担和错误恢复路径；
- 失败场景必须比成功演示优先，包括缺数据、在途订单和不可卖退出。

### 17.2 Deterministic validation

- 同一输入/规则版本产生相同账户状态和动作；
- `MISSING / STALE / CONFLICTING` 的关键输入不能错误放行；
- 订单、成交、撤单和迟到回报不双计、不漏计；
- 历史版本不可覆盖。

### 17.3 Strategy validation

1. 用当时可知数据重演；
2. 前瞻模拟并保存未成交/失效信号；
3. 在用户批准的启用登记和预算内做小预算记录；
4. 按 10/30/50 节点检查行为、阶段表现和参数研究资格；
5. 任何参数变化建立新版本，不污染旧样本。

### 17.4 Macro validation

Stage 1/2 先影子运行，记录来源延迟、去重、误报、漏报、提前量和对用户行为的影响。只有独立策略版本、历史重演、前瞻模拟和用户批准后，宏观信号才可能改变已有持仓动作。

## 18. Product Readiness

| Scope | State | Meaning |
|---|---|---|
| Product direction | APPROVED | 北极星、P0-P3 与非承诺边界已确定 |
| PRD | PRD_DRAFT | 可继续细化；未达到 `PRD_VALIDATED` |
| WP-04 foundation | READY_TO_CONTINUE_IMPLEMENTATION | 合同已冻结；WP04-01 persistence 仅存在于未合并分支，main 尚未集成，后续 service/API/typed links 未实现 |
| WP-05 foundation | NEEDS_DOMAIN_DESIGN | 依赖 WP-04 落地 |
| WP-RISK-01 | READY_FOR_PRODUCT_AND_DOMAIN_DESIGN | 不等于 ready for coding |
| Whole product | NOT_READY_FOR_FULL_AGENT_BUILD | Agent 事实与风险依赖不完整 |
| Strategy profitability | UNPROVEN | 没有足够扣成本前瞻证据 |

## 19. MVP Acceptance Summary

V1 MVP 只有在以下条件均有 L3+ 证据、关键真实对账链有 L4 证据时才可声明闭环：

1. SC-001 在账户/订单未知时稳定禁止新增风险；
2. SC-002 六项准入、双指数、Setup B、数量/费用/RR/预占/PK/确认全部可复现；
3. SC-003 能锁定退出、处理客观限制、完成净结果与纪律复盘；
4. 所有 ActionDecision 可追溯到规则版本和输入快照；
5. 历史 Evidence、Thesis、计划、订单、成交、纪律和规则不可覆盖；
6. Agent 离线时确定性风险门仍工作；
7. 任何收益或宏观观察不被写成产品保证。

## 20. Open Decisions

- WP-RISK-01 的领域合同、子任务和验收分解；
- 账户/持仓/订单的数据接入路径和对账 SLA；
- 各类决策数据的 freshness 阈值；
- 长期 ETF 与 4 只个股容量规则的精确交互；
- 政策数据源清单、许可、去重和告警 SLA；
- 宏观告警可接受误报/漏报阈值；
- 真实前瞻验证的启用条件和小预算上限。

## 21. 一句话产品定义

> **ThesisGuard 是一个以确定性风险内核为底座、以 Evidence 与 Thesis 为事实基础、以只读 Agent 为解释与提案层的个人 A 股现金账户决策操作系统；它帮助用户少犯不可承受的错误并验证方法，而不承诺盈利或预测危机日期。**
