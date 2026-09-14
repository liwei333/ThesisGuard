# ThesisGuard Capability Runtime 延后决策

> Decision ID: `ADR-2026-09-14-CAP-01`
>
> Date: 2026-09-14
>
> Status: **APPROVED — DEFERRED**
>
> Decision type: Architecture timing and task-dispatch guard
>
> Authority boundary: 本文记录 Capability Runtime 专项审计与实现的执行时机。它不覆盖 `PRODUCT_GOAL_REALIGNMENT_2026-09-14.md`、当前 canonical PRD/TAD 或冻结交易模型，也不证明任何 Runtime、Model Backend 或 Agent Backend 已实现。

## 1. Decision

当前**不执行**完整的《ThesisGuard Capability Runtime 架构专项审计》，不新增 canonical `WP-CAP-00`，也不实现 `backend/capability_runtime/`、模型 Provider、Agent Adapter 或 Capability Router。

主建议采用原专项评估候选中的：

```text
D. 等 WP-04 / WP-05 后再做
```

该方向不是被否决，而是被明确延后。未来仍应在第一个真实 Model/Agent 接入之前，冻结 provider-neutral 的执行边界；当前优先保证：

```text
Evidence → Thesis → Personal Risk OS
```

## 2. Why Deferred

1. 当前 canonical 产品决策为 `NOT_READY_FOR_FULL_AGENT_BUILD`；Evidence、Thesis 和确定性风险服务优先于 Agent。
2. 当前工作首先需要完成 WP-04 的实现、集成和独立验收闭环，随后稳定 WP-05 的领域合同与 Proposal 边界。
3. 现有 proposal 已覆盖大量基础结论：`LLMProviderPort`、跨 provider 结构化输出、三层验证、只读 Agent、Tool Policy、observability 和 durable-truth 边界。现在再做完整审计会产生大量重复设计和文档权威冲突。
4. 尚无真实 Capability Runtime 消费者、provider 配置或模型调用实现；过早冻结多维动态路由、Agent transport 和 health/cost 策略会放大抽象成本。
5. `ModelBackend` 与 `AgentBackend`、capability-based routing、technical fallback 与 quality escalation 等问题确有价值，但不会阻断 WP-04-02、WP-04-03 或 WP-04-04 的确定性领域实现。

## 3. Dispatch Guard

后续任何任务分派器在提出以下工作前，必须先读取本文件：

- Capability Runtime；
- 多模型、模型切换、primary/secondary model；
- Capability Router 或 Backend Registry；
- OpenAI-compatible adapter；
- 本地模型、金融模型或外部模型接入；
- Codex/Research/Browser/CLI/HTTP Agent adapter；
- `backend/capability_runtime/` 或 `backend/agent/runtime/` 的新实现；
- 新工作包 `WP-CAP-00` 或其他 Capability Runtime 工作包。

若第 4 节触发条件尚未满足，任务状态必须保持：

```text
DEFERRED_BY_ADR-2026-09-14-CAP-01
```

此时不得把 Capability Runtime 当作下一主线任务；应返回当前 canonical critical path，优先 Evidence、Thesis 和 Personal Risk OS。

## 4. Normal Trigger Conditions

完整 Capability Runtime 专项架构审计只在以下条件全部满足后进入可派发状态：

1. WP-04-01 已完成本地集成后的独立验收，不只存在提交或执行者自检；
2. WP-04-02 Evidence Domain Service 已通过验收；
3. WP-04-03 Evidence API/OpenAPI 已通过验收；
4. WP-04-04 Research exact Evidence references 已通过验收；
5. WP-05 的核心领域合同、版本化读取和 Proposal/validation 边界已经稳定，至少达到可作为 Runtime consumer contract 的状态；
6. 审计使用本地仓库的精确 `main` HEAD，worktree clean，并记录 commit SHA；不得仅审计落后于本地的 GitHub 默认分支；
7. 审计仍为 `READ / ANALYZE / DESIGN / REPORT`，不得在同一任务中实现代码或创建 canonical 工作包。

满足以上条件后，Capability Runtime 审计应在以下事件之前完成：

- 首个真实外部 LLM/金融模型被业务模块调用；
- 首个本地模型或 OpenAI-compatible backend 被接入；
- WP-07 Read-only Agent 开始实现；
- 业务代码开始出现 provider-specific 分支或第二个 provider 需求。

## 5. Exceptional Early Trigger

若在 WP-04/WP-05 完整闭环前，某个已批准的工作包确实需要调用真实模型进行抽取或推断，可以提前派发一个**缩小版架构 ADR**，但必须同时满足：

1. 存在已批准、可定位的真实 consumer，而不是“未来可能需要”；
2. consumer 的输入、输出、领域验证和权限边界已经明确；
3. 任务只解决阻断该 consumer 的最小接口，不升级为完整 Capability Runtime；
4. 不引入多 Agent、动态 Agent、MCP、Tool Loop、Memory、Workflow DSL、模型市场或插件市场；
5. 输出仍是 proposal/ADR，实施必须另立任务并独立验收。

缩小版 ADR 最多处理：

- `ExecutionBackend` 的最小类型边界；
- `OpenAICompatibleModelBackend`；
- ThesisGuard 自有的结构化结果 envelope；
- secrets、timeout、trace 和 technical fallback；
- 与调用方 Domain Service 的 Proposal/validation 边界。

它不得提前设计完整 Agent Backend、复杂多维路由或自治 Runtime。

## 6. Future Audit Scope

达到触发条件后，专项审计应重点回答以下仍未冻结的问题：

1. 是否需要独立的 `Capability Runtime`，还是扩展现有 Agent proposal 中的稳定 Ports 即可；
2. `ModelBackend` 与 `AgentBackend` 是否共享统一父协议，同时使用不同 capability metadata 和生命周期语义；
3. `Capability → Backend` 是否取代简单的 primary/secondary model 配置；
4. OpenAI-compatible 模型、本地模型、远端服务和本地/远端 Agent 的 adapter 边界；
5. `Technical Fallback`、`Quality Escalation`、`Critic / Second Opinion` 的严格区分；
6. ThesisGuard 自有的 structured result 如何复用现有 Structured Output Contracts，且不形成第二套冲突合同；
7. 静态部署配置、运行时配置、secret 引用和审计配置的边界；
8. trace、latency、token、cost、health、fallback reason 与隐私脱敏；
9. 金融任务分别应由 deterministic service、小模型、金融模型、推理模型还是 Agent 承担；
10. `backend/capability_runtime/` 与 `backend/agent/` 是否应分别承担外部智能基础设施和 ThesisGuard Agent 产品层。

## 7. Decisions Already Preserved

未来审计不得重新打开或弱化以下边界，除非另有显式 canonical 决策：

- LLM only proposes；
- Agent is read-only；
- PostgreSQL is durable truth；
- Risk OS is deterministic decision authority；
- missing/stale/conflicting critical data must fail closed；
- Evidence、Thesis、Trade Plan、风险和纪律历史不可覆盖；
- Model/Agent 输出不能直接成为 Verified Evidence、TradeDecision、RiskState、Order、Fill 或 DisciplineState；
- Domain Service 必须独立执行 schema、semantic、source、version、permission 和 domain validation；
- 不实现自动交易、券商控制、复杂多 Agent、Agent swarm、动态 Agent generation 或通用插件市场。

## 8. Future Task Shape

触发条件满足后，先派发一个架构审计任务，不直接派实现任务。其最小交付物应为：

1. 当前实现与现有 proposal 的去重/冲突矩阵；
2. Architecture Decision，明确 `YES / NO / LATER`；
3. Model/Agent boundary；
4. capability routing contract；
5. structured result 与既有合同的复用方式；
6. 配置、secret 和 observability 边界；
7. technical fallback / quality escalation / critic 语义；
8. 金融任务路由矩阵；
9. 最小 Foundation 的 `PROPOSED` 范围、依赖、AC 和测试；
10. 明确的非目标与过度设计阻断项。

未经用户对审计结论的另一次明确批准：

- 不得分配 canonical `WP-CAP-00`；
- 不得修改 canonical roadmap；
- 不得创建 Runtime 业务代码；
- 不得接入任何 provider 或 Agent。

## 9. Supersession Rule

本决策持续有效，直到发生以下任一事件：

1. 用户明确批准新的 Capability Runtime timing/architecture decision；
2. canonical 产品目标或 TAD 以可追踪决策显式取代本文件；
3. Exceptional Early Trigger 被证明满足并形成新的、范围更窄的 ADR。

仅出现新模型名称、供应商营销能力、API 兼容声明或“未来可能需要”不构成取代本决策的理由。
