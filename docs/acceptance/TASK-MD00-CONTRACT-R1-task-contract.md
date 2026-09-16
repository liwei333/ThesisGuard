# TASK-MD00-CONTRACT-R1 — Market Data 文档合同收敛

- Created / evidence cutoff: 2026-09-15（本轮静态核对时点）
- Task type: DOCUMENTATION / ARCHITECTURE_CONTRACT_REVIEW
- Size / risk: MEDIUM / decision-critical semantics, no runtime change
- Authorization: 用户在 Market Data 技术预案审计交付后明确回复“可以你执行下一步吧”；承接已提出的 MD-00 docs-only 合同收敛，不授权业务实现或生产规则启用。
- Required acceptance: `L1_STATIC_REVIEWED`，独立 Reviewer 验收；Compact gate matrix。
- Timing: `PARALLEL_DESIGN_ONLY`；Evidence 修复与 WP-04/WP-05 主线优先。

## Execution core

### Objective / Why now

将 `docs/MARKET_DATA_TECHNICAL_PLAN.md` 的建议收敛为可逐项评审的 Market Data 领域合同草案：身份、Quote/Bar、时间、复权、质量与用途资格、Provider 边界、冻结策略输入、历史重演和验收反例。明确哪些语义已有合同草案，哪些仍需账户实测或后续决策。不得把草案、SDK 文档或历史 PASS 写成生产能力。

### Blocking acceptance criteria

| AC | Required result | Evidence / gate |
|---|---|---|
| AC-01 Scope & baseline | 只新增本任务约定的 docs；既有文件和 Evidence candidate 内容不被本任务修改；记录 main/origin 缓存及真实远程未知 | Git baseline + hashes / Scope, Baseline |
| AC-02 Contract precision | 身份、四类时间与知识可见性、bar 查询谓词、原始/复权尺度、质量和用途资格不混淆；不可 silent fallback | 领域合同 / Contract, Architecture |
| AC-03 Frozen inputs | 对照模型 v1.3 / 系统 v1.1 原文映射双指数、Setup B、S0/Pmax、盘中触发覆盖、流动性和退出输入；不更改规则 | 原文路径与章节、规则矩阵 / Contract |
| AC-04 Honest readiness | Provider 授权/覆盖/时钟/复权因子、阈值、冲突、历史发布机制和留存仍有待关闭项；不宣称 IMPLEMENTED、生产冻结或获准派发实现 | 待关闭登记表 / Evidence |
| AC-05 Independent review | Reviewer 对完整最终合同与范围证据做静态审查并持久化结论；发现问题后修订并复审 | acceptance 文件 / Evidence |

### Allowed scope

- 新增 `docs/MARKET_DATA_DOMAIN_CONTRACT.md`。
- 新增本 task-contract 和 `docs/acceptance/TASK-MD00-CONTRACT-R1-acceptance.md`。
- `/tmp/` 允许临时只读核验快照，不是仓库生产工件。
- Reviewer 只能写本任务 acceptance 文件；不得改写冻结 task-contract、领域合同或其他任务材料。

### Must not do

不得修改 backend、apps、migrations、infra、tests、API/OpenAPI、依赖、AGENTS、authority map、WP 编号或既有审计快照。不得修改、清理、提交 Evidence candidate。不得创建生产 Provider/Router/Adapter、表/API、worker、评分、Agent 能力或券商控制。不得更改模型 v1.3 / 系统 v1.1、Setup B、ActionDecision、风险/恢复参数。不得 commit、push 或发布 ADR 为 APPROVED。

### Verification and three highest-risk counterexamples

1. **伪新鲜 / 历史泄漏**：旧行情响应现在收到；未来补录因子或来源选择被用于过去决策。预期：source time 不重置；按 knowledge visibility 排除当时不可见事实。
2. **漏掉结构失效**：15 秒轮询中间曾触及 S0 后反弹；仅有最新价却宣布可买。预期：coverage 不足为 UNKNOWN；发现真实触及则交由冻结规则永久失效。
3. **价格尺度 / 生命周期混淆**：将最新 QFQ 数字直接填真实委托，或行情 `FRESH` 自动映射 Evidence `VERIFIED` / ActionDecision `ALLOW`。预期：必须可核实执行日换算；三类状态独立。

静态检查包含：文档内链接与章节存在、重复/互相矛盾定义、冻结窗口和边界、待关闭项与实施放行条件、最终业务内容 hashes / Git scope。无业务变更，不运行或新写业务测试；文档反例是未来验收要求，不算已执行测试。

### Expected output / final evidence

一份 `CONTRACT_DRAFT / PROPOSED` 领域合同与一份独立静态验收。PASS 仅表示文档任务通过；不表示 Market Data/WP-04 完成、生产策略验证、账户授权或实现派发。

## Governance appendix

### Fresh baseline

- local `main` / cached `origin/main`: `7d3734bc8346c16f9bbf7f7d9806309949c996de`；真实远程 live HEAD 仍 `UNKNOWN`，上一轮网络核验未成功，本轮不把缓存当远程新证据。
- main 工作区无 tracked diff；七份既有 untracked docs 为前一轮 Market 审计与其他 Evidence 任务记录，全部保留。
- 临时全文件内容快照：`/tmp/thesisguard-md00-baseline-20260915.json`；214 个 Git tracked / untracked 普通文件的 SHA-256，供本轮末尾比较；不是永久验收唯一凭据，最终结果须写入 acceptance。
- Evidence candidate: `codex-wp04-02-evidence-domain-service@bdd70edc153b6ed5def65ed99c41f325df45f066`，已有未提交 services/tests 修复，不属本任务可写范围。
- 新 `TASK-WP04-02-R1C-01-acceptance.md` 已记录其 bounded PASS；R1C-02 仍是后续修复合同。这些是其他任务已有记录，不代表本轮重新执行 PostgreSQL 验证或整个 WP-04 完成。

### Source authority

项目 AGENTS 与 canonical 产品/技术文档优先；模型原文重定位至相邻 tradingModel 的 `last/ThesisGuard_个人交易模型_v1.3_个人适配草案.md` 和 `IterationRecord/个人交易系统_v1.1_基于ThesisGuard_v1.3.md`。路径迁移不授权升级到 v1.2/v1.3 系统候选。Provider 官方资料沿用前一轮带链接且注明证据局限的审计，不把文档宣称替代项目账户实测。

### Compact gate selection

Applicable: Scope, Baseline, Contract, Architecture static, Evidence, independent review. Runtime unit / DB / API / UI / live provider gates: N/A（没有业务变更）；后续实施合同必须重新选 gate，不能继承本任务 PASS。

Executor 不得自签 independent acceptance；Reviewer 可访问文档、冻结规则原文、只读 Git/hash 证据，且只能写 acceptance。主线优先级、实现授权和生产数据政策保持后续决策状态。
