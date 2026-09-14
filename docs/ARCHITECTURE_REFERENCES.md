# ThesisGuard 架构与文档权威索引

> Authority map updated: 2026-09-14
>
> 本文前半部分定义项目内文档权威关系；后半部分保留 2026-09-12 Agent Runtime 开源架构对标快照。
> 文档存在、验收报告或 proposal 均不是实现证据；实现状态以明确分支的当前源码、迁移和新验证为准。

## 0. 项目内权威关系

### 0.1 分类语义

| Class | Meaning | May prove implementation? |
|---|---|---|
| Canonical decision | 当前产品/架构方向的生效决策 | No；只证明决策 |
| Canonical requirement/design | 当前 PRD/TAD 边界 | No；只证明要求/设计 |
| Implementation contract | 某工作包必须遵守的冻结合同 | No；必须另查代码和验证 |
| Current implementation evidence | 明确分支上的源码、迁移、配置 | L1 only；不自动证明测试或运行 |
| Historical acceptance | 当时命令、结果和 verdict 的记录 | 只对记录时点、分支和 scope 有效 |
| Historical audit | evidence cutoff 时点的状态快照 | 不是真实时间状态源 |
| Proposal / review baseline | 尚未提升为 canonical 的架构建议 | 不授权实现，不覆盖 canonical WP |
| Rebuildable derivative | OpenAPI artifact、RAG/index、cache、UI projection 等 | 不能成为唯一业务真相 |

### 0.2 Canonical sources

| Source | Classification | Authority and boundary |
|---|---|---|
| `docs/PRODUCT_GOAL_REALIGNMENT_2026-09-14.md` | Canonical product decision | 2026-09-14 起的北极星、P0-P3、MVP、指标和工作包依赖 |
| `docs/ThesisGuard_V1_PRD.md` | Canonical requirement, `PRD_DRAFT` | 当前 V1 产品需求；不证明实现 |
| `docs/ThesisGuard_V1_Technical_Architecture_Design.md` | Canonical architecture, `TECH_DESIGN_DRAFT` | 当前架构边界和依赖；不批准未定义 API/表 |
| `docs/CAPABILITY_RUNTIME_DECISION_2026-09-14.md` | Canonical architecture timing decision, `APPROVED — DEFERRED` | Capability Runtime 审计延后到 WP-04/WP-05 合同稳定后；不批准 `WP-CAP-00` 或 Runtime 实现 |
| `AGENTS.md` | Engineering entry guide | 后续 Agent 的简明规则和当前里程碑；细节以上述文件为准 |
| `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md` | Canonical WP-04 implementation contract | Evidence identity/version/provenance/storage/任务边界；不证明整个 WP-04 已实现 |
| `docs/WP03_RESEARCH_PACKAGE_*.md` | Accepted WP-03 implementation contracts | bounded Research behavior；当前代码冲突时重新核验代码 |
| 个人交易模型 v1.3 / 系统 v1.1 current policy | Frozen strategy authority | Setup B、双指数、阈值、准入、退出、暂停恢复和枚举；本次未修改 |

### 0.3 Historical records

| Source | Classification | Handling rule |
|---|---|---|
| `docs/PROJECT_STATUS_AUDIT_2026-09-12.md` | Historical audit | evidence cutoff 2026-09-12；`HANDOFF_READY` 只代表报告完整，不能代表当前产品 ready |
| `docs/acceptance/TASK-WP03-*` | Historical acceptance | 保留原文；按当时 commit/branch/scope 解释 |
| `docs/acceptance/TASK-WP04-*` | Historical acceptance / repair contracts | 保留失败、修复和 PASS 链；按记录时点、分支和 scope 解读；`TASK-WP04-01-GIT-INTEGRATION-R1` 证明本地 main 集成，不等于远端已发布或整个 WP-04 完成 |
| `docs/ThesisGuard_V1_Technical_Architecture_Design (1).md` | Non-canonical historical duplicate | 本次调整前与 canonical TAD 字节相同；无项目引用；保留但不得参与当前仲裁 |

### 0.4 Proposals and review baselines

| Source | Status | Non-authority boundary |
|---|---|---|
| `docs/AGENT_RUNTIME_ARCHITECTURE.md` | Proposal / stale current-state section | Agent Runtime 设计参考；内部 WP-06～WP-08 重编号不属于 canonical WP identity |
| `docs/MEMORY_ARCHITECTURE.md` | Proposal | Memory 设计参考；Memory 不替代领域事实 |
| `docs/STRUCTURED_OUTPUT_CONTRACTS.md` | Proposal / contract design baseline | 结构化输出建议；自动提交 actor 边界须由后续 canonical 决策确认 |
| `docs/AGENT_INTERRUPT_AND_RESUME.md`、`docs/AGENT_RUNTIME_AND_INTERRUPT_DESIGN.md`、`docs/TOOL_RUNTIME_AND_APPROVAL.md` | Proposal | 不证明 Runtime/Tool/Approval 已实现 |

### 0.5 Current implementation qualifiers

- local `main@d8f38dd`：已包含 WP-04-01 persistence foundation。业务提交 `cb36e84515fddc8183630757a01078c655a1b8c2`，集成治理提交 `d8f38dd443f95da848338ebda901c288c4bc153a`，独立验收 `TASK-WP04-01-GIT-INTEGRATION-R1` 为 `PASS`；真实 PostgreSQL Evidence focused suite 为 `18 passed`，Alembic head 为 `000000000004`。
- `origin/main@c38c96f`：尚未包含上述两个本地提交；不得把本地集成事实写成远端已发布。
- WP-04 当前整体状态为 `PARTIALLY_IMPLEMENTED`：仅 Evidence ORM models、repositories、Alembic migration 0004、model registry、persistence/migration tests 已进入 local main。WP-04-02 Evidence Domain Service、WP-04-03 Evidence API/OpenAPI、WP-04-04 Research exact Evidence references、worker、MinIO writes、parser/extractor pipeline、embedding、pgvector/RAG 和 Thesis integration 尚未实现。
- 当前下一项业务开发任务为 `TASK-WP04-02 Evidence Domain Service`；Capability Runtime 保持 `APPROVED — DEFERRED`，不得作为下一主线任务。
- 任何“IMPLEMENTED / VERIFIED”必须带分支、scope、证据级别和观察日期。
- 当前源码与历史文档冲突时，重新运行验证并记录新 evidence；不要改写历史报告。

## 1. Agent Runtime 开源架构对标：研究方法与证据边界

> 以下内容是 2026-09-12 的 Architecture Review 基线（非实现说明）。对标对象为 OpenAI Codex、xAI Grok Build、DeepSeek Harness 当时公开主干文档与源码；适用范围仅为 ThesisGuard V1 只读 Agent，不包含自动交易。

### 1.1 证据边界

本对标只把项目官方仓库、官方协议文档和官方源码作为架构事实来源。博客、营销文章和二手解读不作为协议证据。链接指向公开 `main`/`master`，因此这是 2026-09-12 的快照，不是对未来版本的承诺。

本节所称本地 ThesisGuard 证据来自当时工作树 `main@4226b11157e7d7edd68feec31ffbae8cd2a781d7`、当时的三条本地提交历史、代码、迁移、测试及 Compose 观察。该描述是历史快照，已被 2026-09-14 authority map 的当前分支说明取代；不得把它当作当前实现状态。

## 2. 一页结论

ThesisGuard 不应复制任何一个项目的完整框架。最合适的组合是：

- 借 Codex 的 `Thread → Turn → Item` 清晰边界、`expectedTurnId` 定向 steer、interrupt 与 fork/compact 语义。
- 借 Grok Build 的 safe-point interject、每次 prompt 文件快照、持久化 actor 单写者、flush-and-ack 和可回退检查点。
- 借 DeepSeek Harness 的 `SessionEvent` 追加日志、Agent inbox 的 next-turn/next-step 投递、可取消 Tool Pipeline、结构化 Tool Result、fail-closed Approval。
- 拒绝复制三者面向通用编程 Agent 的重量级插件/终端/工作区生态；ThesisGuard V1 需要的是一个模块化单体内的最小可靠 Runtime。

## 3. 能力对比矩阵

| 维度 | OpenAI Codex | xAI Grok Build | DeepSeek Harness | ThesisGuard 决策 |
|---|---|---|---|---|
| 会话模型 | Thread、Turn、Item；持久化 thread 可 resume/fork | Session、prompt queue、conversation turn | Session 追加事件；Agent driver 与 session 分离 | `Session → Run → Turn → Step → ToolCall`，业务对象独立 |
| 中途输入 | `turn/steer` 要求 active turn 和 `expectedTurnId` | Interject 进入 active session buffer，在 safe point 消费 | `steer` 投到 next-step inbox；idle 时可开启新 turn | `run_id + expected_revision`，仅在 safe point 应用 |
| 中断 | `turn/interrupt`，完成状态为 interrupted | Session command/interject 与取消机制 | `cancel` 中止 active driver，可选择清空 inbox | cooperative cancel；副作用提交区不可硬杀 |
| 暂停/恢复 | thread resume 恢复持久化历史 | `/resume`；持久化 actor flush | persistence backend + session open/read/append/flush | PostgreSQL checkpoint 为准，Redis 仅唤醒/租约 |
| 回退 | fork 到历史边界；compact 特殊 turn | `/rewind` 恢复文件并截断会话，具破坏性 | append-only session 更偏事件投影 | V1 不做破坏性 rewind；只建新 revision/fork |
| 上下文压缩 | `thread/compact/start` | `/compact`，可自动或手动 | 可由插件/driver 组合 | 摘要是可重建派生物，绝不代替业务事实 |
| Tool | Item 生命周期、审批请求与最终结果 | 通用 coding tools + workspace/checkpoint | definition/schema、pre/execute/post、guard、result | 小型 Tool Registry + 固定 pipeline，无插件平台 |
| Tool 输出 | 协议化 Item/Result | 类型化 Rust message | canonical output schema + immutable result | Pydantic v2 合同，schema hash + 语义校验 |
| Approval | server request，turn 边界清理 pending approvals | 以会话命令/工具权限为主 | `ask/never`、无 answerer 时 fail closed | 精确绑定 call/args/revision，超时或 revision 变化即失效 |
| Durable event | thread/turn/item 持久化通知模型 | persistence actor FIFO、原子落盘 | append-only `SessionEvent` 是交互事实源 | PostgreSQL `agent_event` 是 runtime 审计源；业务库仍是业务事实源 |
| Live event | turn/item notifications | session actor 消息 | Agent live status / capability seams | SSE 可丢、可重放 cursor；不可当状态真相 |
| 扩展机制 | app-server protocol + provider/tool layers | Rust crates、extensions、subagents | Cordis 插件树/capability seams | 仅定义 4–5 个稳定 Port；拒绝通用插件容器 |

## 4. OpenAI Codex：借什么，为什么

### 4.1 可借鉴

Codex app-server 把 Thread 定义为会话，把用户一次输入到 Agent 最终响应定义为 Turn，把用户消息、推理、命令、文件修改等定义为 Item；客户端可通过生成的 JSON Schema/TypeScript 定义跟随协议版本。这比“一个 chat 表加一列 status”更适合作为清晰边界。[Codex app-server README](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md)

`turn/steer` 不是开启新 turn，而是把输入追加到当前 regular turn；它要求 `expectedTurnId`，如果当前 turn 不存在、目标不匹配、正处于 review 或 manual compact 则拒绝。这一做法直接解决“旧 UI 请求误导向新的活动任务”的竞态。ThesisGuard 采用更适合自身持久化模型的 `expected_run_revision`，保留同样的 compare-and-set 思想。[Codex app-server README：turn/steer](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md#turnsteer)

`thread/resume` 恢复历史与 token 使用，`thread/fork` 复制历史到明确边界，`thread/compact/start` 把压缩作为可观察的特殊 turn；这些语义说明 resume、fork、compact 必须是协议操作，而不能只是 prompt 技巧。[Codex app-server protocol](https://github.com/openai/codex/tree/main/codex-rs/app-server-protocol)

Codex 的 approval 是 server request，并在 turn 开始、完成和中断时清理未决请求；最终 command/file item result 才是权威结果。这支持 ThesisGuard 将 Approval 与 ToolCall 做强绑定，而不是把“用户似乎同意过”放进自然语言历史。

### 4.2 不照搬

- 不照搬 coding Agent 的 shell、文件 patch、MCP 生态；V1 工具域是研究读取、结构化提案和受控领域写入。
- 不把 Codex Item 原样作为业务审计模型；Thesis、Evidence、Trade Plan 有自己的不可变业务版本。
- 不为了协议兼容实现通用 IDE/app-server；FastAPI + SSE 足够满足单用户 V1。

## 5. xAI Grok Build：借什么，为什么

### 5.1 可借鉴

Grok Build 的 mid-turn interjection 被放入 active session 的 pending buffer，由 session actor 在 `process_conversation_turn` 的下一个 safe point 消费；API 返回 queued，而不是伪装成已生效。这是 ThesisGuard soft interrupt 的直接参考。[Grok Build `interject.rs`](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-shell/src/extensions/interject.rs)

其 subagent message delivery 区分 Queue 与 Steer：正在运行时 steer 在当前 turn 的安全边界送达，queue 则保护为下一 turn；idle 时投递规则另行处理。ThesisGuard 同样必须让普通追加消息与改变当前目标的 steer 成为显式不同的操作。[Grok Build subagents guide](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/docs/user-guide/16-subagents.md) 与 [`message_delivery.rs`](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-shell/src/session/message_delivery.rs)

Session persistence 采用 FIFO 单写者，稳定落盘使用 FlushAndAck，写文件采用临时文件加原子 rename；持久化消息覆盖 chat、plan、rewind point、signal、compaction checkpoint 和 usage。ThesisGuard 虽使用 PostgreSQL，但仍应采用单一状态机写入路径和“提交后才 ack”的原则。[Grok Build `persistence.rs`](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-shell/src/session/persistence.rs)

`/rewind` 会恢复 prompt 时的文件快照并截断对话，`/fork` 派生新会话，`/compact` 可自动或手动压缩。这提醒我们：rewind 是有破坏性的产品语义，不能用“撤销”按钮含混表达。[Grok Build sessions guide](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/docs/user-guide/17-sessions.md)

### 5.2 不照搬

- 不引入文件工作区快照；ThesisGuard 的等价物是业务 snapshot/version 引用和 runtime checkpoint。
- 不实现破坏性截断业务历史；append-only 是项目硬约束。
- 不复制多 subagent 管理、终端 UI、coding tool 集合和 Rust actor 全套结构。

## 6. DeepSeek Harness：借什么，为什么

### 6.1 可借鉴

Harness 把 Session 设计成追加的类型化 `SessionEvent` 日志，模型历史是投影；durable 事件包括 turn/step/user/tool 等生命周期。这正适合恢复、重放和审计，但 ThesisGuard 只把它作为“Agent 交互事实源”，不能越权成为投资业务事实源。[DeepSeek Harness Session](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/session.md)

Agent 接口把 driver 与 session 分离，并明确提供 `send`、`followup`、`steer`、`inject`、`cancel`、`whenIdle`；inbox 区分 nextTurn 与 nextStep。ThesisGuard 可借这套投递语义，同时把公共接口压缩为 `submit / steer / pause / resume / cancel`。[DeepSeek Harness Core](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/core.md)

Tool subsystem 要求 canonical output schema、timeout、cancellation signal，并采用 parse/freeze arguments → pre-execute allow/deny/ask → monotonic guards → execute wrappers → post-execute → finalize → immutable result 的流水线。它比“模型决定后直接调函数”可靠，适合财务研究的高审计要求。[DeepSeek Harness Tools](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/tools.md)

Approval 支持 `ask|never`，没有 answerer 时 fail closed；请求绑定 agent/tool/callId/reason/signal。ThesisGuard 进一步绑定 `args_hash` 和 `run_revision`，以避免旧批准跨 revision 复用。[DeepSeek Harness Approval](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/approval.md)

Persistence 提供 create/open/read/append/flush/close 和 JSONL/SQLite 后端，并强调 flush checkpoint 与 crash recovery。ThesisGuard 不需要复制后端选择器，但必须具备同等级别的 append/flush/recovery 合同。[DeepSeek Harness Persistence](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/persistence.md)

### 6.2 不照搬

Harness 的 Cordis 插件树、profile/bundle 与 capability seam 适合通用可替换运行时；ThesisGuard 当前只有一个产品、一个部署拓扑、少量稳定工具，引入它会把业务进度消耗在容器、生命周期和依赖注入元框架上。[DeepSeek Harness Architecture](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md)

## 7. 统一语义映射

| 通用概念 | Codex | Grok Build | DeepSeek Harness | ThesisGuard |
|---|---|---|---|---|
| 长生命周期容器 | Thread | Session | Session | AgentSession |
| 一次用户目标执行 | Turn | conversation turn/prompt | turn | Run + 一个 primary Turn（P0） |
| 一次交互边界 | Turn | prompt | turn | Turn |
| 一次模型/工具推进 | Item 序列 | loop iteration | Step | Step |
| 改变当前方向 | steer + expectedTurnId | interject/steer at safe point | nextStep steer | intervention + expectedRevision |
| 下一项工作 | 新 turn | queue | nextTurn | queued Turn/Run |
| 中止 | interrupt | cancel/session command | cancel | cooperative cancel |
| 恢复 | resume | resume | persistence open | checkpoint resume |
| 分支 | fork | fork | 可由事件历史构造 | P1 hypothesis fork |
| 回退 | fork 到历史边界 | destructive rewind | 追加事件/投影 | 新 revision，不删除历史 |

## 8. 2026-09-12 对标提案的约束性结论（非 canonical）

1. **Session 不是业务数据库。** Agent event 能恢复交互，Evidence/Thesis/Trade Plan 的事实与版本仍由领域服务负责。
2. **只有一个并发控制数：Run Revision。** Turn/Step/ToolCall 都记录它；V1 不再引入 Intent Epoch 或 Plan Epoch。
3. **Steer 必须定向。** 请求携带 run id 与 expected revision；不匹配返回冲突，不能静默投给“当前某个任务”。
4. **中断在 safe point 生效。** Tool 正在运行时 cooperative cancel；已提交的不可变业务记录不回滚，只能追加纠正版本。
5. **Tool Result 先审计、后应用。** 旧 revision 结果可保存，但标为 stale 且禁止进入后续上下文或领域提交。
6. **Approval 不是聊天文本。** 它是有过期时间、作用域、参数哈希和 revision 的持久化对象。
7. **Compact 只压缩对话投影。** 事实从领域数据库重取，不能依赖摘要回忆。
8. **P0 拒绝通用插件系统与多 Agent。** 先做 4–5 个端口、固定工具注册表和单 active run。

## 9. 来源登记

1. [OpenAI Codex app-server README](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md)
2. [OpenAI Codex app-server protocol](https://github.com/openai/codex/tree/main/codex-rs/app-server-protocol)
3. [xAI Grok Build repository](https://github.com/xai-org/grok-build)
4. [xAI Grok Build session source tree](https://github.com/xai-org/grok-build/tree/main/crates/codegen/xai-grok-shell/src/session)
5. [xAI Grok Build sessions guide](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/docs/user-guide/17-sessions.md)
6. [DeepSeek Harness architecture](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md)
7. [DeepSeek Harness core](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/core.md)
8. [DeepSeek Harness session](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/session.md)
9. [DeepSeek Harness tools](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/tools.md)
10. [DeepSeek Harness approval](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/approval.md)
11. [DeepSeek Harness persistence](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/persistence.md)
