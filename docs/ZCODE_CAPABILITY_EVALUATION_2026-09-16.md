# zcode capability evaluation and routing

## Purpose and Status

用户在 2026-09-16 授权建立工程 coding agent 路由：目标是 zcode 承担大部分常规实现，Codex 定义必要边界、独立验收和接管失败。此记录是当前证据评估，不是未执行测试的结果。完整开发能力评估状态：`PARTIALLY_IMPLEMENTED`，Stage 1 收到且有必要补正，Stage 2/3 `PLANNED`。

产品内 read-only Agent 与工程 coding agent 是不同对象。候选工程工具可在用户授权范围编码，但不能据此改变产品交易权限。

## Identity and Evidence

```yaml
combination_id: zcode-agent-thesisguard-d3acc1c-20260916
model_name: UNKNOWN
model_version: UNKNOWN
agent_tool: zcode
agent_tool_version: UNKNOWN
execution_mode: interactive-session / tool-call-loop # candidate-reported
permission_mode: user-gated / READ_ONLY_PROBE # candidate-reported
context_method: AGENTS.md injection and on-demand Read/Bash # candidate-reported
system_instructions: AGENTS.md # repository instructions, not complete system prompt
project_commit: d3acc1c6f4a2e5ce1fe4b973d7855409c0db1da5
workspace_state: tracked/index clean; untracked acceptance materials; candidate dirty
test_date: 2026-09-16
evaluator: zcode-self-probe
independent_reviewer: Codex
stage_1_verdict: PASS_WITH_REQUIRED_FIXES
routine_project_authorization: L1_READ_ONLY
development_capability: UNPROVEN
```

Source: 用户在本对话转发的《ThesisGuard 只读能力探针评估报告》。未取得原始工具日志，身份中的自报项不是独立确认。

Codex 实际只读核验：main `git rev-parse HEAD`、`git status --short`、`git worktree list --porcelain`；`rg --files` 检查 Evidence/Research/tests/migrations；读取 repositories、冻结合同第 27 节、当前审计记录；读取候选 HEAD/status 和 fixture。未执行数据库、pytest、服务、Git 写入或业务验收。

阶段差异：第一次复核 main 有四个未跟踪条目；本次写此记录前 main 增加 fixture evidence 目录。候选 HEAD 仍 `af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8`，但 `tests/test_evidence_services.py` 已修改，另有未跟踪 `tests/evidence_pg_fixture.py` 和 `tests/test_evidence_pg_fixture_lifecycle.py`。旧审计中的 fixture 缺陷不能直接当作当前源码未修复的结论。当前在途修改的结果 `UNKNOWN`。

## Findings

| ID | Candidate location | Finding | Required correction |
|---|---|---|---|
| ZC-01 | 第三/五部分，服务实现高度适合 | 只有读文件证据，无真实修改、事务/幂等/失败验证 | 开发域写 UNPROVEN，实际隔离测试后评级 |
| ZC-02 | 第二/五部分，项目定位和下一任务 | main 无 service 正确，但遗漏已有候选 worktree 和在途修复 | 重新检查全部相关分支及未提交范围，区分实现/集成/验收 |
| ZC-03 | 第三部分，WP-04-02 services/schemas/api | 冻结合同第 27 节将 API/Pydantic schema 放在 WP-04-03 | 按 WP 边界收窄建议 |
| ZC-04 | 工具边界、风险与结论 | 本轮禁止测试不证明工具不能测试；无专用 DB 工具不证明 Bash 无法连接 | 区分权限限制、环境缺失、未验证能力 |
| ZC-05 | 整体交付 | 缺少逐域授权/规模/路由 YAML、单一基准和完整自查 | 下一轮完整交付，保留 UNKNOWN |

正面证据：主分支 SHA 和文件定位吻合；披露未知版本和未执行验证；保留两个专项延后边界。当前状态与无 tracked 修改相符，但状态快照不是全部历史操作只读的证明。无已确认虚报/越界证据，故不判 FAIL_SAFETY。

## Capability Coverage

| Domain | Evidence now | Current routing | Missing proof |
|---|---|---|---|
| 文档/定位/单模块分析 | 基础定位已确认，报告需补正 | zcode L1 XS/S | 准确的条款与源码关联、完整输出 |
| 产品/架构/状态机理解 | 有范围混入及分支遗漏 | Codex 主责，zcode 候选意见 | 跨文件状态/边界分析 |
| Schema/ORM/repository/迁移 | UNPROVEN | Codex | 真实 PostgreSQL、约束、迁移及失败恢复 |
| FastAPI/OpenAPI | UNPROVEN | Codex，基准通过后 zcode L2 | 请求/响应、错误码、契约与测试 |
| Python 后端领域服务 | UNPROVEN | Codex，基准通过后 zcode L2 | 真实修改、边界、幂等、事务和验证 |
| Vue/TypeScript | UNPROVEN | Codex，基准通过后 zcode L2 | 类型/build、双实体状态隔离、桌面/移动交互 |
| 调试/重构/修复 | UNPROVEN | Codex | 受控反馈后的复现、最小修复及回归 |
| 测试/验收 | 场景草稿可试用；运行能力 UNPROVEN | zcode 草稿，Codex 独立验收 | 真实运行、独立断言、失败报告 |
| Worker/MinIO/Agent workflow | UNPROVEN，部分需求延后 | Codex；延后项不派实现 | 另行明确合同及真实运行验证 |

不输出虚假的全域数值总分。已测报告的分项证据不足以对实现质量、稳定性或修复成本评分；下一阶段由 Codex 按事实源 15、正确性 20、实现 15、一致性 10、范围 15、验证 10、诚实 10、稳定性 5 的权重逐域评分。不可观察项写 NOT_TESTED，并注明可评分分母，不把归一化分数当授权证明。

## Evaluation Sequence and Cost

1. Stage 1 返修：只读重新取 main/candidate 状态，校正 WP 边界，检查当前 fixture；不要求重新审计全部项目。
2. Stage 2：临时隔离目录中的 Python、API、Vue 三个 XS/S 基准。每个最多 2-6 个源/测试/配置文件；独立交付。使用模拟教学协议，不写入项目，不连接数据库，不证明真实 Evidence 服务已可用。
3. Codex 重新读取基准源码并执行独立正反例；每个能力域单独 PASS/PASS_WITH_REQUIRED_FIXES/FAIL。必要时一次受控返修，保留第一次失败。
4. 对已通过的能力域派一个明确真实 S 任务，隔离指定文件、必要独立验收；按 AGENTS.md 的重复表现门槛再考虑 L3/M。迁移/数据库/worker 必须单测真实环境，不能用前三个基准代替。

初轮、返修和验收分别记录时间/重试/源码修改量；token/费用不可见写 UNKNOWN。观察 Codex 定义、验收和接管总成本，避免用开发量比例宣称 token 节省。若复审不断需要重读全项目或修复超过候选改动 50%，收窄任务或由 Codex 承担该域。

详见 `prompts/ZCODE_CAPABILITY_BENCHMARK_2026-09-16.md`。zcode 提交原始证据；最终评级由 Codex 更新此记录与 AGENTS.md。当前不授权 zcode 自评升级或修改路由。
