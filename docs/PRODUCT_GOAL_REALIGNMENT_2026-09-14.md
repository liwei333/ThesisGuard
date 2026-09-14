# ThesisGuard 产品目标调整决策

> Decision ID: `PDR-2026-09-14-01`
>
> Date: 2026-09-14
>
> Product Direction: **APPROVED**
>
> PRD State: **PRD_DRAFT**
>
> Whole Product: **NOT_READY_FOR_FULL_AGENT_BUILD**
>
> Strategy Validation: **UNPROVEN**
>
> Authority: 本文是 2026-09-14 起产品目标、优先级、MVP、成功定义和工作包依赖的 canonical decision。若既有 README、PRD、TAD、Agent proposal 或历史审计与本文冲突，以本文及随后同步后的 canonical README、PRD、TAD 为准；冻结的个人交易模型 v1.3 / 系统 v1.1 参数除外。

## 1. Document Status

本文记录一次产品方向收敛，不是实现验收、交易策略启用登记或收益承诺。

- Included Scope：产品北极星、目标用户、非目标、P0-P3 能力层级、MVP 场景、成功指标、假设、宏观预警边界、工作包依赖、当前实现现实和文档迁移。
- Excluded Scope：业务代码、数据库迁移、API、OpenAPI、前端页面、生成客户端、Agent Runtime、数据接入、宏观算法、自动下单和任何冻结交易参数修改。
- Evidence Cutoff：2026-09-14，仓库 `main`，HEAD `bd4b1d7`；开始修改前 worktree clean。
- Evidence Method：文档为 L0 CLAIM；源码/迁移为 L1；构建为 L2；实际自动化测试结果为 L3；历史运行或验收记录只描述其记录时点，不自动证明当前 L4/L5。

状态词统一为：`IMPLEMENTED`、`PARTIALLY_IMPLEMENTED`、`CONTRACT_ONLY`、`DESIGN_ONLY`、`PLANNED`、`UNPROVEN`、`UNKNOWN`。目录、文档或提交存在本身不能证明能力已经实现。

## 2. Decision Summary

ThesisGuard 的第一产品目标调整为：

> **ThesisGuard 是一套面向个人 A 股现金账户的、证据驱动的风险与决策操作系统。它通过不可覆盖的研究证据、投资逻辑、市场状态、账户风险、交易计划与纪律记录，帮助用户避免无法承受的错误，并以可审计的前瞻数据验证个人交易方法是否存在扣除成本后的优势。**

浓缩表达：

> **先活下来，再用可验证的数据判断自己是否具有优势；Agent 服务于纪律与证据，而不是替代纪律与证据。**

本次决策带来六个直接变化：

1. 第一优先级由“研究闭环或 Agent 体验”上移为 `P0 Personal Risk OS` 生存内核。
2. 研究、Evidence、Thesis 仍是关键事实基础，排在 Agent 之前。
3. Agent 明确为只读推理、解释与提案层；它不是金融事实、风险状态或准入结果的 System of Record。
4. V1 MVP 收敛为盘前风险检查、新交易准入、持仓退出与复盘三个场景。
5. 产品负责的决策质量/纪律指标与产品只能观察的交易结果指标严格分开。
6. 宏观能力分为基础政策与市场告警、系统性风险哨兵两阶段；不承诺预测金融危机发生日期。

## 3. Why the Goal Is Being Adjusted

当前产品材料同时描述研究知识库、Thesis 验证、账户与交易纪律、Agent、个人模型迭代、宏观危机预警和稳定盈利，造成三个问题：

- 价值层级混合：基础生存控制、研究能力、交互能力和长期实验被写成并列目标。
- 依赖倒置：Agent UI 容易在 Evidence、Thesis、账户和风险服务之前被理解为核心交付物。
- 验收不可证：稳定盈利和危机预测受策略、市场、数据和用户行为共同影响，不能作为开发阶段可直接承诺的产品结果。

真正需要优先验证的是：系统能否在关键数据缺失时拒绝新增风险，能否把事前计划、实际成交、退出和纪律完整留痕，以及这些规则是否改善用户真实行为。

## 4. Previous Goal and Its Problems

既有目标中的研究沉淀、Thesis 持续验证、市场先于个股、不可覆盖历史和 Agent 反迎合仍然有效；以下表达被本决策取代或降级：

| Previous emphasis | Problem | New treatment |
|---|---|---|
| 以单标的研究到 Agent 对话作为首个 MVP | 无法覆盖账户未知、在途订单、退出与暂停等不可承受风险 | MVP 改为三个风险闭环场景；研究是准入依赖 |
| Agent 被呈现为“个人交易操作系统”的中心 | 容易让自然语言成为风险规则或系统事实 | Agent 降为只读解释与提案层 |
| 多模型、多买点和个性化学习并行 | 当前 Setup B 尚无扣成本前瞻优势证据 | 只验证冻结的 Setup B；其余进入独立实验 |
| 市场情绪七阶段直接映射仓位 | 与冻结的双指数过滤和账户风险阈值可能冲突 | 标记为历史设计；未经策略版本批准不得用于生产准入 |
| 稳定盈利或跑赢作为愿景式成功 | 无法由产品保证，且会诱发事后调参 | 仅作为观察结果；状态保持 UNPROVEN |
| 金融危机预测 | 时点不可校准且误报代价高 | 改为脆弱性、压力、价格确认和新增风险限制 |

## 5. New North Star

北极星不是“给出更多买卖观点”，而是形成一个可审计、可复现、在信息不足时会停下来的决策闭环：

```text
来源与时点
  → Evidence freshness
  → Thesis / 市场 / 账户的确定性状态
  → 交易准入或退出动作
  → 订单、成交与客观限制
  → 纪律与净结果复盘
  → 规则版本的前瞻验证
```

优先级判断准则：能减少不可承受错误、解除风险闭环关键依赖或提高决策可追溯性的能力，优先于提升对话表现、覆盖更多标的或增加预测复杂度的能力。

## 6. Target User

### Primary user

- 使用个人自有资金、无杠杆的 A 股现金账户；
- 愿意在交易前记录 Thesis、证据、失效条件、预算和计划亏损；
- 持仓集中、需要控制研究与管理负担；
- 希望用前瞻、扣成本记录判断个人方法是否存在优势；
- 接受“数据不全时不新增风险”和 Agent 反驳。

### Not the target user

- 需要自动下单、代客交易、券商客户端控制或无确认跟单的用户；
- 追求高频、分钟级、多市场多资产或杠杆交易的用户；
- 希望系统承诺回本、胜率、年度盈利、稳定盈利或准确预测危机日期的用户；
- 不愿维护账户、持仓、订单、成交和事前计划，却要求系统给出确定性交易许可的用户。

## 7. Explicit Non-Targets

- 不自动下单、不自主调仓、不控制券商客户端。
- 不保证收益、胜率、回本、年度盈利或稳定跑赢指数。
- 不预测每日涨跌，也不承诺金融危机发生时间。
- 不做高频、分钟级策略、做 T、第一轮主动加仓或亏损摊低成本。
- 不做多市场、多资产全面覆盖、复杂多 Agent、社交投资或收益排行榜。
- 不为全部 A 股同时生成完整深度研究。
- 不允许在线学习自动修改生产策略或自然语言覆盖冻结 Trade Plan。

## 8. Product Outcome Hierarchy

| Level | Outcome | Product responsibility |
|---|---|---|
| Survival | 避免未知账户、未结订单、失控退出、超预算和不可承受回撤继续扩大 | Directly owned |
| Decision integrity | 决策使用可核验、未过期、无未解决冲突的输入；结果可追溯 | Directly owned |
| Behavioral discipline | 计划、执行、违规、暂停和恢复不能被盈亏改写 | Directly owned |
| Method validation | 用前瞻、扣成本、分市场状态的数据判断方法是否值得继续 | Shared/observed |
| Financial outcome | 盈亏、回撤、超额收益和资金效率 | Observed, not promised |

## 9. P0/P1/P2/P3 Capability Priorities

### P0 — Personal Risk OS / 生存内核

P0 是确定性领域服务集合，不依赖 LLM 可用性。产品定义至少覆盖：

- Account ledger：账户单位净值、外部出入金中性化、当前回撤、历史高点回撤；
- Account state：`AccountState`、`PauseStatus`、`RecoveryEligibility`、`NewRiskPermission`；
- Position truth：当前持仓、`LEGACY_PRE_MODEL`、`LONG_TERM_ETF`、可卖数量；
- Order truth：未结订单、撤单待确认、部分成交、拒单、迟到成交，及现金/市值/风险预占；
- Risk budget：单笔风险预算、主动持仓风险 H、单股市值、权益总市值、同产业和共同风险因子；
- Exit control：价格退出、逻辑退出、时间复核与 `EXIT_PENDING`；
- Market gate：拟入场日前一完整交易日的沪深300与中证1000过滤；
- Operational constraints：T+1、停牌、跌停、跳空、流动性、券商能力；
- Discipline：违规、账户暂停、有限恢复、恢复周期耗尽，盈利不抹掉违规；
- Data gate：Evidence/行情/账户/券商数据 freshness；关键输入未知时禁止新增风险；
- Daily operations：盘前、盘中、盘后核对。

P0 的目标是让风险门在 Agent、Redis、向量检索或通知不可用时仍能给出可复现的保守结论。

### P1 — Research, Evidence and Thesis

P1 提供可引用的研究事实基础：

- `SourceDocument`、`SourceDocumentVersion`；
- `EvidenceSeries`、`EvidenceVersion`；
- `SourceLocator`、`SourceGrade`、`VerificationStatus`、Evidence freshness；
- `ResearchPackage`、`ResearchModule`；
- `ThesisVersion`、`ThesisValidation`、证伪条件；
- Bull/Base/Bear、预期差、Catalyst、增量更新；
- 所有历史追加保存，不覆盖旧版本。

### P2 — Read-only Agent

Agent 可以：

- 读取结构化事实，解释研究、市场和账户状态；
- 识别缺失、过期和冲突资料；
- 反驳用户 Thesis；
- 生成研究、交易计划、复盘和记忆写入提案；
- 比较候选股票与已有持仓；
- 提醒风险、纪律、下一验证日期和必要确认。

Agent 不可以：

- 直接提交订单或控制券商；
- 自行修改风险阈值或解除账户暂停；
- 将 LLM 输出直接写成 Evidence、账户事实或交易事实；
- 在关键输入缺失时给出无条件 `ALLOW`；
- 自动形成长期风险偏好；
- 通过自然语言覆盖冻结 Trade Plan 或策略版本。

### P3 — Macro Risk Sentinel

P3 分阶段交付，并且不能阻塞 P0 最小闭环。

#### Stage 1 — Basic Policy & Market Alert

- 监控权威政策来源；
- 覆盖融资保证金、担保物折算、融资融券、流动性、准备金、资本约束、跨境融资、房地产、地方债和程序化交易等变化；
- 保存政策原文、来源、发布日期、生效日期、适用对象与影响路径；
- 用价格、市场宽度和流动性做确认；
- 只映射“是否允许新增风险、是否需要账户风险复核”，不输出未经校准的危机概率。

#### Stage 2 — Systemic Risk Sentinel

覆盖信贷/GDP 缺口、债务偿付率、部门杠杆、房地产信用周期、银行与非银、跨境债权、外币债务、美元流动性、信用利差、估值、波动、融资与流动性、多资产相关性和去杠杆压力，并建立历史回放、误报、漏报和提前量评估。

## 10. MVP Core Scenarios

### SC-001 — 盘前风险检查

每天盘前，用户能够得到：

- 当前账户状态与是否有资格进入新交易检查；
- 未处理的 `EXIT_PENDING`；
- 未结订单、撤单待确认、迟到成交与可卖数量；
- 当日有效保护价；
- Evidence、行情、账户或券商能力的 `MISSING / STALE / CONFLICTING`；
- 今天必须做什么、不能做什么。

关键输入无法核验时，`NewRiskPermission=PROHIBITED`。

### SC-002 — 新交易准入

新增主动股票风险前，系统必须依次检查：

1. Research 和 Evidence 是否可用于当前决策；
2. 沪深300与中证1000过滤；
3. Setup B 是否 `TRIGGERED`；
4. `Pmax / S0 / T / q_plan` 与费用；
5. 扣成本后的 RR；
6. 账户风险、现金与订单预占；
7. 股票数量上限，以及第五只的 Position Replacement PK；
8. 用户是否接受计划亏损。

最终动作只能使用既有 `ActionDecision = ALLOW / NO TRADE / MANAGE_ONLY / EXIT_PENDING / NOT_APPLICABLE`。任一关键准入失败或未知且用户请求新增风险时，必须为 `NO TRADE`。

### SC-003 — 持仓退出与复盘

在价格退出、逻辑证伪、账户暂停或交易结束时，系统必须：

- 锁定 `EXIT_PENDING` 并记录可卖数量；
- 记录 T+1、停牌、跌停、拒单、流动性和部分成交等客观限制；
- 区分 `EntryClass` 与 `Execution`；
- 计算实际净盈亏，仅在 R0 可核验时计算 `R_net`；
- 记录 MFE/MAE、纪律违规、暂停事件或整改事项；
- 区分模型问题与执行问题；
- 不因盈利抹掉违规，不因亏损自动修改模型。

## 11. Product-Owned Success Metrics

以下指标由产品直接负责。当前没有可审计生产基线的指标均标 `PLANNED` 或 `UNKNOWN`，不得伪造。

| Metric | Direction / target | Current status |
|---|---:|---|
| 交易前计划覆盖率 | 100% | PLANNED；baseline UNKNOWN |
| 账户日终对账完整率 | 100% | PLANNED；baseline UNKNOWN |
| 关键 `MISSING / STALE / CONFLICTING` 数据错误放行次数 | 0 | PLANNED；baseline UNKNOWN |
| 计划外超数量次数 | 0 | PLANNED；baseline UNKNOWN |
| 人为扩大止损次数 | 0 | PLANNED；baseline UNKNOWN |
| 人为扩大风险预算次数 | 0 | PLANNED；baseline UNKNOWN |
| 人为拖延退出次数 | 0 | PLANNED；baseline UNKNOWN |
| 未知持仓或未结订单时新增风险次数 | 0 | PLANNED；baseline UNKNOWN |
| 历史交易计划覆盖或删除次数 | 0 | PLANNED；baseline UNKNOWN |
| 规则变更版本覆盖率 | 100% | PLANNED；baseline UNKNOWN |
| ActionDecision 可追溯率 | 100% | PLANNED；baseline UNKNOWN |
| Evidence 来源与时间戳完整率 | 100% for decision-critical evidence | CONTRACT_ONLY；baseline UNKNOWN |
| 告警去重、送达、确认和失败重试 | 逐事件可审计 | PLANNED |
| 数据源中断时 fail-closed 正确率 | 100% for new-risk gates | PLANNED |

## 12. Trading Outcome Metrics

以下指标用于观察策略是否值得继续，不是产品完成、收益或风险承诺：

- 扣费后的 Expectancy、Profit Factor、胜率、平均盈利 R、平均亏损 R；
- 最大回撤、当前回撤、回撤恢复时间；
- 相对沪深300全收益表现，以及与账户权益比例匹配的现金/权益基准；
- 不同 Market Regime、产业、持有期、退出类型下的表现；
- 资金占用、滑点、真实费用、信号频率、未成交和失效信号；
- 宏观告警命中率、误报率、漏报率和提前量；
- 对用户时间、情绪和主业的影响。

样本节点：10 笔做行为检查，30 笔做阶段评价，50 笔以上才开始更系统的参数研究。任何节点都不自动证明盈利或允许提高风险预算。不得因单笔盈亏改策略；参数和路径变化必须产生独立版本。

## 13. Assumption Register

| ID | Assumption | Type | Impact | Uncertainty | Current evidence | Validation method | Success criteria | Failure / stop criteria | Status |
|---|---|---|---|---|---|---|---|---|---|
| A-001 | 严格风险门会改善真实交易行为 | Value | 决定 P0 是否产生核心价值 | High | 只有规则设计，无前瞻行为数据 | 对比启用前后计划覆盖、违规与错误放行 | 计划覆盖 100%，关键违规趋近 0，且用户可持续执行 | 用户持续绕过或维护成本超过保护价值 | UNVALIDATED |
| A-002 | 用户愿意每日维护或导入账户、持仓、订单和成交 | Usability | 决定账户状态可信度 | High | 无真实连续使用证据 | 30 个交易日可用性试验 | 日终对账 100%，重大缺口能在次日盘前闭环 | 连续缺失导致频繁 UNKNOWN 或错误决策 | UNKNOWN |
| A-003 | 能取得及时、合法、稳定且可负担的数据源 | Feasibility | 影响 Evidence、行情和宏观能力 | High | 当前无正式 provider/许可证据 | 数据源选型、SLA、许可和故障演练 | 时效/合法性/成本满足决策需求，故障可 fail-closed | 关键数据长期不可得或法律/成本不可接受 | UNKNOWN |
| A-004 | 只读 Agent 足以形成长期使用价值 | Value | 决定 P2 投资回报 | Medium | 仅有架构提案，无用户验证 | 在 P0/P1 可用后做任务完成率与留存试验 | 提高缺口识别、复盘质量和任务完成率 | 只增加对话负担或诱发绕过规则 | UNVALIDATED |
| A-005 | Setup B 在真实费用、滑点和不同市场状态下有正期望 | Value / Feasibility | 决定策略是否值得继续 | High | 冻结定义存在；无足够扣成本前瞻样本 | 历史重演后做前瞻模拟和小预算登记 | 足够样本下净 Expectancy/风险指标支持继续 | 净优势不稳定、成本后为负或风险不可接受 | UNPROVEN |
| A-006 | 宏观预警比简单市场过滤带来额外可观测保护 | Value | 决定 Stage 2 必要性 | High | 无校准比较 | 与双指数过滤做影子对照 | 降低错误新增风险且误报代价可接受 | 无增量价值或导致长期错误空仓 | UNPROVEN |
| A-007 | 宏观告警误报不会造成长期错误空仓或频繁改计划 | Value / Usability | 影响行为和机会成本 | High | 无用户行为数据 | 影子告警、回放和确认制试验 | 误报率与行为干扰在预设容忍度内 | 高频误报、用户失去信任或频繁改计划 | UNKNOWN |
| A-008 | 用户在亏损、踏空或连续止损时不会绕过系统 | Usability | 直接影响纪律闭环 | High | 无前瞻行为证据 | 违规事件和暂停恢复日志 | 违规被完整记录并按规则处理，重复率下降 | 关键场景持续绕过且无法通过流程纠正 | UNKNOWN |
| A-009 | 手工录入、文件导入或只读同步足以保证券商对账 | Feasibility | 决定账户风险准确性 | High | 尚无数据路径验收 | 多渠道对账与迟到成交演练 | 日终 100% 对账，未结/迟到成交可追踪 | 差异无法及时解释或错误放行新增风险 | UNKNOWN |

## 14. Macro Risk Sentinel Boundary

宏观预警优先表达“脆弱性增加、压力升级、价格是否确认”，不把单一指标解释为确定性股灾。Stage 1 初期只限制新增风险或触发账户风险复核，不凭一个宏观分数自动清空已有持仓。

如果未来增加宏观强制降仓规则，必须：

1. 建立独立策略版本；
2. 明确来源、as_of、freshness、适用范围和影响链；
3. 经过历史重演、前瞻模拟和误报/漏报评估；
4. 获得用户显式批准；
5. 不覆盖既有 Trade Plan 与历史记录。

## 15. Revised Work Package Dependency Map

历史 WP-01 至 WP-08 的 ID 和验收引用保持不变。新增非冲突 ID：

- `WP-RISK-01`：Personal Risk OS；
- `WP-ALERT-01`：Basic Policy & Market Alert；
- `WP-MACRO-01`：Systemic Risk Sentinel；
- `WP-VALIDATION-01`：Forward Validation & Model Governance。

Canonical critical path：

```text
WP-01 Engineering Skeleton
  → WP-02 Instrument + Watchlist
  → WP-03 Research Package
  → WP-04 Evidence
  → WP-05 Thesis Engine
  → WP-RISK-01 Personal Risk OS
  → WP-06 Research UI（集成风险视图，但不重命名历史 WP）
  → WP-07 Read-only Agent
  → WP-08 Incremental Update
  → WP-ALERT-01 Basic Policy & Market Alert
  → WP-MACRO-01 Systemic Risk Sentinel
  → WP-VALIDATION-01 Forward Validation & Model Governance
```

允许并行：WP-RISK-01 的产品/领域设计可与 WP-04/WP-05 基础工作并行；UI 原型可提前，但不得被当作完整风险闭环；WP-VALIDATION-01 的记录口径必须在生产规则启用前进入各工作包验收，而不是最后补报告。

## 16. Current Implementation Reality

### AI State Capsule

- [FACT] 仓库有 FastAPI/Vue/PostgreSQL/Redis/MinIO/Dramatiq 工程骨架，以及 Instrument/Watchlist 和 Research Package 代码。
- [FACT] `backend/research/` 有 models/schemas/services/API，migration `000000000003` 建立 Research Package/Module 表，API 路由已注册。
- [FACT] 2026-09-14 新运行 `pytest -q tests/test_research_api.py tests/test_research_persistence.py`：16 passed，4 warnings；首次沙箱内运行的数据库连接因 `PermissionError` 失败，不能解释为业务失败。
- [FACT] `backend/evidence/`、`thesis/`、`market/`、`portfolio/`、`trade_plan/`、`discipline/`、`agent/` 只有占位 `__init__.py`，没有相应 migration、service 或 API 注册。
- [FACT] WP-04 有冻结的 Evidence Domain Contract 和历史验收/修复记录；`main@bd4b1d7` 没有 Evidence 业务实现。未合并分支 `codex/wp04-evidence-persistence@4201ae7` 含 WP04-01 persistence foundation，但不代表 main 或整个 WP-04 完成。
- [FACT] 两份 TAD 在修改前 SHA-256 相同；无 `(1)` 文件将继续作为 canonical，带 `(1)` 文件保留为非 canonical 历史副本。
- [CLAIM] 历史提交和验收文档声称 WP-03 完成、WP-04 合同通过；它们是任务/时点声明，当前实现结论仍以代码和新验证为准。
- [INFERENCE] 基于 `main` 的静态实现、定向回归结果和工作包依赖，当前关键路径仍是先把 Evidence 的最小持久化切片纳入 `main` 并重新验证，再进入其 service/API 后续切片；这不是对尚未集成能力的完成声明。
- [CONFLICT] AGENTS/README/PRD/TAD 的旧里程碑、MVP 和 Agent 优先级落后于当前代码及本决策。
- [CONFLICT] 2026-09-13 WP-03 integration acceptance 记录全量门禁通过；当前 `bd4b1d7` 的 schema docstring 变更造成 committed OpenAPI artifact 漂移。该既有缺陷只记录，不在本次文档任务中修复。
- [UNKNOWN] 尚无生产、真实用户、正式数据源、券商对账或策略盈利证据。

| Area | Observed state | Highest current evidence | What it does not prove |
|---|---|---|---|
| WP-01 Engineering Skeleton | IMPLEMENTED for local skeleton | L1 current code; historical L2-L4 records | production readiness |
| WP-02 Instrument + Watchlist | PARTIALLY_IMPLEMENTED | L1 code/migration/tests present | formal live data source or full user scope |
| WP-03 Research Package | Capability `IMPLEMENTED`; verification evidence: targeted backend L3 `VERIFIED`; overall quality-gate result `UNKNOWN` | L1 implementation + 16 current backend tests; OpenAPI drift recorded | production usage, complete research content generation, or all quality gates green |
| WP-04 Evidence | CONTRACT_ONLY on main; persistence PARTIALLY_IMPLEMENTED on unmerged branch | L0 frozen contract/acceptance history + L1 branch implementation | main integration, service, API, worker, MinIO, embedding or RAG implementation |
| WP-05 Thesis | DESIGN_ONLY / NOT_STARTED | L0 PRD/TAD; placeholder package | domain implementation |
| WP-RISK-01 | DESIGN_ONLY / NEEDS_DOMAIN_DESIGN | frozen v1.3/v1.1 policy + this decision | account/risk/portfolio/trade implementation |
| WP-06 Research UI | PLANNED | L0 | usable risk/research UI |
| WP-07 Read-only Agent | DESIGN_ONLY / PLANNED | proposal docs + placeholder | runtime capability |
| WP-08 Incremental Update | PLANNED | L0 | end-to-end update flow |
| WP-ALERT-01 / WP-MACRO-01 / WP-VALIDATION-01 | PLANNED | this decision | implementation or value |

## 17. Migration Impact on Existing Documentation

- `README.md`：改为产品入口和真实状态摘要。
- `docs/ThesisGuard_V1_PRD.md`：以本决策重写 V1 范围、MVP、指标、假设和 readiness；旧 P0 研究链不再是当前 MVP。
- `docs/ThesisGuard_V1_Technical_Architecture_Design.md`：作为 canonical TAD，调整确定性风险内核、Agent 依赖和宏观分期；不新增未批准的 API/表设计。
- `AGENTS.md`：更新北极星、关键规则、工作包和当前里程碑，防止后续 Agent 从 WP-01 重新开始。
- `docs/ARCHITECTURE_REFERENCES.md`：建立 canonical / historical / proposal / implementation contract 的 authority map。
- `docs/PROJECT_STATUS_AUDIT_2026-09-12.md`：保持 2026-09-12 历史审计，不改写为当前状态。
- WP-03/WP-04 acceptance 和 repair 文档：保持历史记录，不为新路线改写。

## 18. Non-Goals

本次决策不授权实现或修改 Evidence、Thesis、Market、Portfolio、Trade Plan、Discipline、Notification、Agent、Macro、数据库迁移、API、OpenAPI、生成客户端、行情/政策/券商接入。也不授权修改 Setup B、风险阈值、账户恢复规则或 ActionDecision 枚举。

## 19. Open Decisions

| ID | Decision needed | Why it remains open |
|---|---|---|
| OD-001 | WP-RISK-01 的 canonical domain contract、子任务和验收分解 | 本次只确定产品范围，不设计表/API |
| OD-002 | 账户/持仓/订单数据采用手工、文件导入还是只读券商同步 | 数据合法性、时效、成本和对账可靠性未知 |
| OD-003 | Evidence/行情/账户/券商各数据类型的 freshness 阈值 | 必须按来源和决策用途设计，不能由 Agent 猜测 |
| OD-004 | `LONG_TERM_ETF` 与“最多 4 只个股”的精确容量交互 | 冻结政策要求单列，不能静默推导 |
| OD-005 | Stage 1 政策源清单、去重和确认规则 | 尚无数据源 ADR 和可用性证据 |
| OD-006 | 宏观强制降仓是否永远排除，或未来允许独立策略实验 | 若改变已有持仓动作，必须另版并显式批准 |
| OD-007 | 产品指标的观察窗口、告警 SLA 和可接受误报阈值 | 当前无生产基线 |
| OD-008 | 何时及以何种小预算条件进入真实前瞻验证 | 需要风险承受度、启用登记和用户批准 |

## 20. Validation Plan

1. Domain replay：同一冻结输入必须产生相同状态和 `ActionDecision`。
2. Fail-closed tests：关键 `MISSING / STALE / CONFLICTING` 输入不得错误放行新增风险。
3. Golden scenarios：SC-001、SC-002、SC-003 分别建立领域、集成和真实对账验收。
4. Historical replay：验证定义、费用、公司行动、迟到成交和客观限制处理，不用结果反向调参。
5. Forward simulation：保存每个未成交、失效和执行动作，避免幸存者偏差。
6. Small-budget validation：只有完成用户批准的启用登记后，才在预算内记录真实成交和行为压力。
7. Model governance：10/30/50 笔节点按既定用途检查；任何参数变化新建版本。
8. Macro shadow mode：先做不影响持仓的影子告警，比较简单市场过滤的增量价值与误报代价。

## 21. Product Readiness Decision

| Dimension | Decision | Rationale |
|---|---|---|
| Product Direction | APPROVED | 用户已明确批准新北极星、边界和优先级 |
| PRD | PRD_DRAFT | 范围、MVP、指标和假设已明确；WP-RISK-01 领域合同与若干数据决策仍开放 |
| Whole Product | NOT_READY_FOR_FULL_AGENT_BUILD | Evidence、Thesis 和确定性风险服务尚未形成可靠读取边界 |
| WP-04 Foundation | READY_TO_CONTINUE_IMPLEMENTATION | Evidence contract 已冻结；WP04-01 persistence 仅存在于未合并分支，main 尚未集成，service/API/typed links 未实现 |
| WP-05 Foundation | NEEDS_DOMAIN_DESIGN | 依赖 Evidence 实现/合同落地 |
| Risk OS | READY_FOR_PRODUCT_AND_DOMAIN_DESIGN | 产品边界已收敛；尚未批准详细技术合同 |
| Read-only Agent | NOT_READY_TO_IMPLEMENT_AS_CORE | 允许原型，不允许声称风险闭环完成 |
| Strategy Profitability | UNPROVEN | 无足够扣成本前瞻证据 |
| Macro Sentinel | PLANNED | Stage 1/2 边界已定，价值与数据可行性未验证 |

因此，本产品已准备好继续 WP-04 Evidence 实现与 WP-RISK-01 领域设计，但没有准备好进行完整 Agent 构建、生产交易准入或收益宣称。

## 22. Change Log

| Date | Change | Authoritative impact |
|---|---|---|
| 2026-09-14 | 建立新北极星、P0-P3、三场景 MVP、双类指标、Assumption Register、宏观两阶段和新工作包依赖 | Supersedes conflicting product-goal and roadmap statements in older canonical docs |
