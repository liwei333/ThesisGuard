# 论衡 ThesisGuard

> **论其逻辑，衡其风险。**
>
> **ThesisGuard — Protect the Thesis. Control the Risk.**

ThesisGuard 是一套面向个人 A 股现金账户的、证据驱动的风险与决策操作系统。

它通过不可覆盖的研究证据、投资逻辑、市场状态、账户风险、交易计划与纪律记录，帮助用户避免无法承受的错误，并以可审计的前瞻数据验证个人交易方法是否存在扣除成本后的优势。

> **先活下来，再用可验证的数据判断自己是否具有优势；Agent 服务于纪律与证据，而不是替代纪律与证据。**

## 产品边界

ThesisGuard 首先是 `Personal Risk OS`，其次是 Research / Evidence / Thesis 系统，AI Agent 是建立在这些确定性事实之上的只读推理与交互层。

它不是：

- 自动交易机器人、券商客户端控制器或代客交易系统；
- 稳定盈利、胜率、回本、年度收益或跑赢指数的保证；
- 精确预测金融危机日期或单日涨跌的模型；
- 在关键数据缺失时仍能给出无条件买入许可的聊天机器人。

当前个人交易模型 v1.3 / 系统 v1.1 的策略验证状态为 **UNPROVEN**。产品可以帮助建立、执行、复盘和迭代个人交易模型，但不能保证任何交易结果。

## 核心原则

### Thesis First

每个主动交易都必须有明确、可证伪、带版本的投资逻辑。股票代码、成本价或 Agent 观点不能替代 Thesis。

### Fact > Narrative

系统区分事实、来源、推断、市场预期、用户假设和 Agent 提案。关键数据必须包含来源、`as_of`、取得时间、freshness 和验证状态。

### Risk Before Opportunity

市场状态、账户状态、未结订单、退出事件和风险预算先于个股机会。关键输入 `MISSING / STALE / CONFLICTING` 或不可核验时，对新增风险执行 fail-closed。

### Immutable History

Evidence、Thesis、Trade Plan、订单、成交、告警、规则版本和纪律记录追加保存。盈利不能抹掉违规，亏损不能自动证明模型错误。

### LLM only proposes

LLM 不是 System of Record。Agent 可以读取、解释、反驳和提出变更，但不能直接写入金融事实、修改风险阈值、解除账户暂停或提交订单。

## 产品能力优先级

| Priority | Capability | Purpose |
|---|---|---|
| P0 | Personal Risk OS | 账户单位净值、回撤、持仓、订单预占、退出、纪律、暂停恢复、市场过滤和 fail-closed |
| P1 | Research / Evidence / Thesis | 保存来源、Evidence 版本、Research Package、Thesis、情景、证伪与增量更新 |
| P2 | Read-only Agent | 读取事实、解释状态、识别缺口、反驳 Thesis、生成提案和要求确认 |
| P3 | Macro Risk Sentinel | 分阶段监测政策、脆弱性、市场压力与价格确认，不承诺危机日期 |

关键路线是：

```text
Evidence → Thesis → Personal Risk OS → Research/Risk UI → Read-only Agent
```

Agent 可以暂时不可用，风险门必须继续工作。Macro Risk Sentinel 不能成为最小交易风险闭环的无限范围阻塞项。

## V1 MVP：三个核心场景

### SC-001 盘前风险检查

盘前回答：当前账户状态、是否有资格进入新交易检查、未处理的 `EXIT_PENDING`、未结订单/撤单待确认/迟到成交、可卖数量、当日保护价、关键数据缺口，以及今天必须做什么、不能做什么。

### SC-002 新交易准入

新增主动股票风险前，检查 Research/Evidence freshness、沪深300和中证1000过滤、Setup B、`Pmax / S0 / T / q_plan`、真实费用与扣成本 RR、账户风险、现金和订单预占、最多 4 只股票与 Position Replacement PK，以及用户是否接受计划亏损。

最终动作只能使用：

```text
ActionDecision = ALLOW / NO TRADE / MANAGE_ONLY / EXIT_PENDING / NOT_APPLICABLE
```

任一关键输入失败或未知且用户请求新增风险时，必须为 `NO TRADE`。

### SC-003 持仓退出与复盘

退出或交易结束时，锁定 `EXIT_PENDING`，记录可卖数量和 T+1/停牌/跌停/拒单/迟到成交/部分成交等客观限制；区分 `EntryClass` 与 `Execution`；计算实际净盈亏，仅在 R0 可核验时计算 `R_net`；记录 MFE/MAE、违规、暂停和整改，不以盈亏改写纪律或策略。

## 冻结交易模型边界

本仓库的产品文档不得静默改变个人交易模型 v1.3 / 系统 v1.1：

- 新主动交易只验证 Setup B；
- 市场过滤使用拟入场日前一完整交易日的沪深300和中证1000；
- 研究、市场、价格数量、空间、退出事件、账户执行意愿六项准入全部通过；
- 判断无法完成时 `AssessmentStatus=UNKNOWN`，新增风险 `ActionDecision=NO TRADE`；
- 股票最多 4 只，第 5 只必须 Position Replacement PK；
- 不使用杠杆、不摊低成本、不下移保护价；第一轮不主动加仓、不做 T；
- 订单预占现金、市值和风险；退出触发后使用 `EXIT_PENDING`；
- 账户暂停、有限恢复和恢复耗尽按冻结规则执行；
- 旧仓与长期 ETF 单列，历史记录不可覆盖。

详细冻结参数以个人交易模型 v1.3 / 系统 v1.1 的当前有效合同为准。本次产品目标调整没有修改任何阈值或路径。

## 当前实现状态

证据截止：2026-09-14。状态不从目录名、提交标题或任务名推断。

| Area | State | Evidence boundary |
|---|---|---|
| WP-01 Engineering Skeleton | IMPLEMENTED（本地工程骨架） | 不代表生产就绪 |
| WP-02 Instrument + Watchlist | PARTIALLY_IMPLEMENTED | 有代码/迁移/测试；正式数据源与完整用户边界未证明 |
| WP-03 Research Package | Capability `IMPLEMENTED`；verification evidence：targeted backend L3 `VERIFIED`；overall quality-gate result `UNKNOWN` | 16 项当前 Research 测试通过；committed OpenAPI artifact 存在既有漂移，因此不能声称全部门禁绿色 |
| WP-04 Evidence | PARTIALLY_IMPLEMENTED | local `main@d8f38dd` 已集成 WP-04-01 persistence foundation：Evidence ORM models、repositories、Alembic migration 0004、model registry、persistence/migration tests；业务提交 `cb36e84515fddc8183630757a01078c655a1b8c2`，集成治理提交 `d8f38dd443f95da848338ebda901c288c4bc153a`；`origin/main@c38c96f` 尚未包含这两个本地提交；service/API/worker/MinIO/parser/embedding/RAG/Thesis integration 未实现 |
| WP-05 Thesis Engine | DESIGN_ONLY / NOT_STARTED | 仅设计材料和占位包 |
| WP-RISK-01 Personal Risk OS | DESIGN_ONLY / NEEDS_DOMAIN_DESIGN | 产品边界和冻结策略存在；账户/订单/风险内核未实现 |
| WP-06 Research UI | PLANNED | 不把原型当成风险闭环 |
| WP-07 Read-only Agent | DESIGN_ONLY / PLANNED | Agent Runtime 文档是 proposal；代码仅占位 |
| WP-08 Incremental Update | PLANNED | 尚无完整端到端实现 |
| WP-ALERT-01 / WP-MACRO-01 / WP-VALIDATION-01 | PLANNED | 无实现或价值验证 |

当前里程碑：**post-WP-04-01 / WP-04-02 Evidence Domain Service next**，同时可以准备 `WP-RISK-01` 的产品与领域设计。Whole Product 状态为 **NOT_READY_FOR_FULL_AGENT_BUILD**。

`TASK-WP04-01-GIT-INTEGRATION-R1` 已独立验收本地 main 集成：真实 PostgreSQL Evidence focused suite 为 `18 passed`，当前 Alembic head 为 `000000000004`。这只证明 WP-04-01 persistence foundation，不代表整个 WP-04 或产品闭环完成。

Capability Runtime 当前为 **APPROVED — DEFERRED**：`ADR-2026-09-14-CAP-01` 只记录延后时机，不授权 `WP-CAP-00`、Provider/Router/Adapter 或 Runtime 实现。

2026-09-12 的项目状态审计是历史时点快照，不是实时状态；历史 WP-03/WP-04 acceptance 与 repair contract 只按记录时点、分支和 scope 解读，不是当前所有能力已实现的证明。

## 工作包与依赖

既有 WP-01 至 WP-08 的编号与历史验收引用不变：

- WP-01：Engineering Skeleton
- WP-02：Instrument + Watchlist
- WP-03：Research Package
- WP-04：Evidence
- WP-05：Thesis Engine
- WP-06：Research UI
- WP-07：Read-only Agent
- WP-08：Incremental Update

新增非冲突工作包：

- WP-RISK-01：Personal Risk OS
- WP-ALERT-01：Basic Policy & Market Alert
- WP-MACRO-01：Systemic Risk Sentinel
- WP-VALIDATION-01：Forward Validation & Model Governance

Canonical critical path：

```text
WP-01 → WP-02 → WP-03 → WP-04 → WP-05 → WP-RISK-01
      → WP-06 → WP-07 → WP-08 → WP-ALERT-01
      → WP-MACRO-01 → WP-VALIDATION-01
```

WP-RISK-01 的领域设计可以与 WP-04/WP-05 的基础工作并行。前瞻验证是生产规则启用的治理要求，不是最后补写一份报告。

## 成功如何定义

产品直接负责：交易前计划覆盖、日终对账、关键数据错误放行、超数量、扩大止损/风险、拖延退出、未知持仓或订单下新增风险、历史覆盖、规则版本化、ActionDecision 可追溯、Evidence 来源时间戳、告警可靠性和数据中断 fail-closed。

产品只观察、不承诺：扣费 Expectancy、Profit Factor、胜率、平均盈亏 R、回撤与恢复、相对基准表现、分 Regime/产业/持有期/退出表现、资金占用、滑点费用、信号频率、宏观告警误报/漏报/提前量，以及对用户时间和情绪的影响。

10 笔用于行为检查，30 笔用于阶段评价，50 笔以上才开始更系统的参数研究。这些节点都不证明盈利，也不自动允许提高风险预算。

## Macro Risk Sentinel

Stage 1 `Basic Policy & Market Alert` 保存权威政策原文、来源、发布日期、生效日期、适用对象和影响路径，并结合市场宽度、流动性和价格确认，只映射是否允许新增风险或是否需要账户复核。

Stage 2 `Systemic Risk Sentinel` 扩展到信用、杠杆、房地产、银行/非银、跨境与美元流动性、信用利差、估值、波动、融资和多资产去杠杆压力，并验证误报、漏报和提前量。

它表达脆弱性与压力，不是确定性金融危机预测器。初期不凭单一宏观分数自动清空已有持仓；任何未来强制降仓规则必须独立版本化、回放、前瞻模拟并由用户批准。

## 技术栈

| Layer | Technology |
|---|---|
| Frontend | Vue 3 + TypeScript + Vite + Pinia + Vue Router |
| API | Python 3.12+ + FastAPI + Pydantic v2 |
| Database | PostgreSQL 17 + pgvector |
| Migration | Alembic |
| Cache / Queue | Redis + Dramatiq |
| Object Storage | MinIO（S3-compatible） |
| Infrastructure | Docker Compose |

架构采用模块化单体。PostgreSQL 保存结构化 durable truth；MinIO 保存原始文件；Redis 用于缓存、队列或实时分发；pgvector 用于检索。Redis、pgvector、LLM 和通知系统都不能成为金融事实的唯一真相。

## 开发命令

```bash
# Development
make dev
make dev-api
make dev-web
make worker

# Database
make migrate
make migrate-gen

# Quality
make test
make lint
make typecheck
make frontend-check

# Docker
make up
make down
make logs
make rebuild
```

## 文档入口与权威关系

- [产品目标调整决策](docs/PRODUCT_GOAL_REALIGNMENT_2026-09-14.md)：目标、优先级、MVP、成功定义和依赖的首要来源。
- [V1 PRD](docs/ThesisGuard_V1_PRD.md)：当前产品需求与验收边界。
- [V1 TAD](docs/ThesisGuard_V1_Technical_Architecture_Design.md)：当前 canonical 技术架构边界。
- [架构与文档权威索引](docs/ARCHITECTURE_REFERENCES.md)：canonical、historical、proposal、implementation contract 分类。
- [Capability Runtime 延后决策](docs/CAPABILITY_RUNTIME_DECISION_2026-09-14.md)：`ADR-2026-09-14-CAP-01`；Capability Runtime 当前 `APPROVED — DEFERRED`，不授权 `WP-CAP-00` 或 Runtime 实现。
- [WP-04 Evidence Domain Contract](docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md)：Evidence 的冻结 implementation contract；不代表 WP-04 整体已实现。当前本地 main 只集成 WP-04-01 persistence foundation。
- [WP-04-01 Git 集成验收](docs/acceptance/TASK-WP04-01-GIT-INTEGRATION-R1-acceptance.md)：本地 `main@d8f38dd` 集成验收记录；不表示远端已发布。
- [2026-09-12 项目状态审计](docs/PROJECT_STATUS_AUDIT_2026-09-12.md)：历史时点审计，不是当前状态源。

## Disclaimer

ThesisGuard 是个人研究、风险控制、决策支持和复盘工具，不构成证券投资顾问、收益承诺或自动交易服务。所有真实交易均需用户自行核对账户、行情、证券规则、券商能力和计划亏损，并由用户最终确认。
