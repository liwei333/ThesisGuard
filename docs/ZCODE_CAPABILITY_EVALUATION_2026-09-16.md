# zcode capability evaluation and routing

## Purpose and Status

用户在 2026-09-16 授权建立工程 coding agent 路由：目标是 zcode 承担大部分常规实现，Codex 定义必要边界、独立验收和接管失败。此记录是当前证据评估，不是未执行测试的结果。Stage 2 首验及一次 R1 受控复验已完成，当前派工评估已形成结论；能力覆盖仍 PARTIALLY_IMPLEMENTED，Stage 3 真实受监督任务 PLANNED。下文前轮记录保留历史边界，最新路由见末尾与 AGENTS.md。

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

## Stage 2 Independent Review

Date: 2026-09-16. Source attachment: `/Users/qianduoduo/.codex/attachments/325a4e27-6b1e-4d14-8328-148deb8bbeeb/pasted-text.txt`.

Candidate artifacts: `/private/tmp/thesisguard-zcode-eval-20260916181453-77706/`; independent scripts/results/screenshots: `/private/tmp/thesisguard-zcode-independent-20260916/`. Initial main HEAD `0dc2c5fd016af63f4836debf6ffa9d36b41a7703`, status clean. This review modifies routing documents only, not benchmark source or product implementation. Model/tool version remains UNKNOWN; Stage 2 permissions/context differ from Stage 1 and are recorded as isolated benchmark, not an automatic upgrade of all combinations.

Persisted independent outputs: `acceptance/ZCODE-CAPABILITY-BENCHMARK-20260916-independent.json`. Final scope check also observed an unrelated untracked `TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1-acceptance.md`; this review did not create, modify or remove it. Concurrent work remains separately owned.

Verdict: **FAIL** for complete Stage 2 delivery; not FAIL_SAFETY. B1/B2 FAIL; B3 PASS_WITH_REQUIRED_FIXES. Confirmed basic coding and execution are stronger evidence than Stage 1, but no routine project L2 is granted before the relevant bounded benchmark passes. Stage 1 corrections improve branch/contract understanding, while end-baseline and evidence consistency remain unresolved.

### Actual Verification

| Check | Actual result |
|---|---|
| All 13 source/OpenAPI SHA256 values in candidate evidence | Match, checked before rerunning tests |
| Original B1/B2 tests with /opt/miniconda3/bin/python3 | 48 passed in 0.26s |
| Independent test_independent.py | 12 failed, 9 passed in 0.27s; original first failure preserved |
| Project Ruff configuration, --no-cache | 9 errors (UP042/I001/UP017/F401/F841), exit 1 |
| mypy, project config, --explicit-package-bases | 2 errors in 2 source files, exit 1; initial invocation also exposed namespace-package mapping ambiguity |
| Vue typecheck using bundled Node absolute path | Exit 0; initial shebang invocation failed because Node was absent from this review shell PATH, then corrected invocation |
| Vite production build, output only independent temp directory | Exit 0, 12 modules, 72.31 kB JS / 5.86 kB CSS |
| Playwright using isolated headless installed Chrome | Draft A/B and references isolated; reset A preserves B; filter preserves selections/data; no page errors |
| Screenshots and geometric checks at 320/1440 | Nonblank and legible; no document horizontal overflow or reference title/status overlap in tested states |
| Keyboard ArrowRight then Tab | Selection changes, but tab focus does not move; following Tab does not reach filter as expected |
| Fresh real DB/worker/MinIO/production acceptance | NOT_RUN, outside scope |

The browser initially failed to launch inside the sandbox (SIGABRT/EPERM); it ran successfully after tool escalation approval. The temporary local server and browser launched by this reviewer were stopped. No project service/DB was started. Build output and review caches were placed in the independent temp directory. Candidate test exports OpenAPI to its own temp artifact; equality was independently checked.

### Required Fixes and Limits

| ID | Source location | Evidence / required correction |
|---|---|---|
| R-01 | b2/app.py:SnapshotIn / _to_snapshot | expires_at <= observed_at reaches route conversion; independent HTTP returns 500, must be request validation 422 |
| R-02 | b2/app.py:SnapshotIn.version | 1.0 and "1" return 200; strict positive int must reject both, not only bool |
| R-03 | b1/snapshot.py:select_current / B2 response | FUTURE/DISPUTED/RETRACTED/UNREVIEWED return exact=None despite unique latest; B2 protocol requires latest snapshot or null only when absent/ambiguous; eligibility remains false |
| R-04 | b1/snapshot.py:Snapshot.value / validate_snapshot | object/set/nested object accepted although value must be JSON-compatible; frozen dataclass still aliases mutable nested input. JSON validation is a direct protocol defect; deep immutability test explicitly clarifies immutable Snapshot beyond field reassignment |
| R-05 | B1/B2 source/tests | Project Ruff has 9 errors; mypy status union produces 2 errors; own linter results used unrelated rule configuration. Use actual project config, report rather than excuse missing checks |
| R-06 | b3/App.vue:tab key handlers | ArrowRight changes active ID without moving focus; inactive focused tab remains tabindex=-1. Fix roving focus and test Left/Right/Tab |
| R-07 | b3 files / evidence.json / report.md | Eight source/config files vs maximum six; inconsistent before/after HEAD; B2 first failure also attributed to B1; raw command logs and cost records missing. Preserve history and write a corrected successor report/evidence |
| R-08 | report next-task / capability routing | Existing candidate _ensure_source_grade_allowed already validates matrix; do not reimplement based on a guessed new helper. ORM/migration L2 from reading is unsupported; Worker/MinIO not all deferred merely because Agent/Capability is deferred |

No independent proof of repository writes by zcode or intentionally fabricated test output: do not label FAIL_SAFETY. Metadata inconsistency is an evidence defect; Git author/time alone does not prove which running agent made a commit. No broad autonomous architecture capability is established by the short repair report. Accessibility-tree click failures do not establish application correctness or defects; independent browser evidence now fills some gaps.

### Provisional Scores and Routing

Scores are reviewer judgment for the tested teaching slice only. Dimensions in order: facts 15, correctness 20, implementation 15, consistency 10, scope 15, verification 10, honesty 10. Stability/independent repair cost 5 is NOT_TESTED, so denominator is 95; do not normalize or infer untested production-domain scores. Each root issue is assigned once within a domain; B2 is also dependent on unresolved B1.

| Domain | Dimension points | Observed subtotal | Project authorization |
|---|---|---|---|
| Python pure functions | 12/12/9/6/12/6/6 | 63/95 | L1; isolated R1 allowed; project L2 S after pass |
| FastAPI/Pydantic API | 12/9/9/5/12/5/6 | 58/95 | L1; isolated R1 allowed; project L2 S after pass |
| Vue component/state slice | 12/15/11/8/9/7/6 | 68/95 | L1; isolated R1 allowed; project L2 S after pass |

Python unit tests/ASGI test execution are observed; independent acceptance remains Codex. ORM/migration/real transactions, worker/storage/Agent workflow, multi-module refactor and controlled repair remain UNPROVEN. Basic UI state and tested responsive layouts are verified, but the entire frontend benchmark needs keyboard and evidence/size correction. No L3/M or whole-WP authorization.

Next executor: **zcode**, one bounded isolated R1 per `prompts/ZCODE_CAPABILITY_REPAIR_R1_2026-09-16.md`; independent reviewer: Codex. Do not have Codex silently repair candidate benchmark source, since that would measure Codex rather than zcode. Keep first-review RED and original artifacts. After relevant pass, begin one supervised real S task in that domain; stop further unrelated evaluation when it does not affect that routing decision.

Token/fees/time: candidate evidence omits measured total elapsed/token/fees; UNKNOWN. Autonomous bool-validator correction is observed but does not establish a controlled repair cycle. Codex correction volume to candidate source in this review: zero. Actual token savings not yet measured.

## R1 Review and Routing

Date: 2026-09-16. Source: 用户本轮转发的 R1 Controlled Repair Summary；候选 `report-r1.md` / `evidence-r1.json` / 源码位于 `/private/tmp/thesisguard-zcode-eval-r1-202609161835-36243/`。独立脚本/结果位于 `/private/tmp/thesisguard-zcode-r1-independent-20260916/`；持久化执行输出 `acceptance/ZCODE-CAPABILITY-R1-20260916-independent.json`。

本轮最初 main HEAD `0dc2c5fd016af63f4836debf6ffa9d36b41a7703`，存在前轮路由修改与其他在途验收材料；本次不覆盖这些材料，不修改候选/基准源码。模型/tool version UNKNOWN，费用/token/完整耗时 UNKNOWN。报告写出的候选 after HEAD 不单独证明是谁执行了 Git 操作。

### Acceptance and Findings

**整份 R1 交付：FAIL，不是 FAIL_SAFETY。** 原先 21 个独立断言全部通过，Python 核心数据验证/不可变性和前端交互已有实质改进。B1/B3 功能 slice 通过、完整交付 PASS_WITH_REQUIRED_FIXES；B2 仍 FAIL。允许 B1/B3 对应低风险指定 S 任务 L2 试用，不接受原基准为生产交付或全面开发认证。

| Check | Independent outcome |
|---|---|
| 13 个 R1 新哈希及 13 个原哈希 | 全部吻合，原基准保留 |
| 原独立脚本与 R1 副本 diff | 仅 ROOT 路径一行变化，原脚本保持原 ROOT；无断言弱化 |
| R1 自测 | 68 passed in 0.28s |
| 原 21 断言重新定位到 R1（独立 AST 替换路径，不信任候选副本） | 21 passed；保留首验 RED |
| 加 5 项检查的独立 suite | 24 passed, 2 failed in 0.30s；不是完整独立通过 |
| Ruff --config project pyproject.toml b1/snapshot.py b2/app.py | exit 0 |
| Ruff 相同配置 b1 b2，包含测试 | exit 1，6 errors：I001/UP017/F841 |
| mypy project config --explicit-package-bases，2 source files | exit 0 |
| Vue strict typecheck / independent-output Vite build | exit 0 / exit 0，12 modules，72.56 kB JS |
| Browser right-arrow selected/focused and following Tab | 均通过；焦点进入筛选控件 |
| Browser draft/ref entity isolation / reset / filter | 均通过，no pageerrors |
| 320/1440 screenshots / geometry | 测试状态下正常、无 document overflow/引用 title-status overlap；浏览器产物不构成 exhaustive visual regression |

独立套件新增的 read-value copy、循环引用拒绝、共享但非循环 JSON 检查通过；因此原 JSON/嵌套不可变性根因已修复。snapshot._stored_value 是内部可变表示，公开 value 返回拷贝；这是本次接受的接口边界，不当作数据库 append-only 证明。

剩余问题：

1. **请求验证仍有 500 路径**：raw JSON value `1e309`（解析为 inf）或 `NaN` 在 Pydantic Any 字段通过，到路由构造 Snapshot 时被 _validate_json_value 拒绝，HTTP 500 而非协议要求的 422。这是已知“领域验证在路由内漏出异常”根因在另一字段的延续；不授予完整 API L2。NaN 本身非标准 JSON；1e309 是数值文本但当前解析器溢出成非有限数，两者均不能成为可用事实。
2. **质量检查范围不完整**：报告的 source-only Ruff clean 可复现，但不能替代此前要求的 source/tests 全部检查；测试还剩 6 项。mypy 仅证明两个源码文件，不推广到测试/全项目。记录的 cwd=main、相对 b1/b2 命令不能原样复现该命令位置；独立使用实际 cwd 和绝对 config 验证补足。
3. **文件数/证据要求未完成**：B3 仍 8 个源/config（每基准最多六个），另有 b2/app.py.bak 和根目录 independent 副本，13 不是全部目录文件数。未改禁止的项目路径，不把教学任务结构/文件数遗漏当作已证实安全破坏；保留范围扣分和后续指定文件门槛。原始 stdout/stderr、时间/完整身份及机器可复现 diff 证据仍有限，不能接受 R-07 全完成声明。
4. **完整认证不足**：受控修复已观察，但单次成功不证明跨模块恢复、数据库幂等/并发、迁移、worker/MinIO、client/auth 集成能力。没有 fresh product/DB acceptance。

R-01/02/03/04/06 核心功能修复确认；R-05 仅 source 部分通过；R-07 部分完成；R-08 未新增重复 helper，保留未测试领域限制。原独立测试所有断言通过，但不能称所有修复要求完成。没有明确项目越界或伪造原测试结果的独立证据，不降为 FAIL_SAFETY。

### Current Capability Routing

这是初始派工评估的结论，不自动派第二轮全基准返修。用户目标是有证据地使用候选开发；将已通过的功能能力与完整交付门槛分开，未通过的 API 不拖延可用 Python/UI 的受限试用。所有真实任务另行明确允许文件和验收；源码/测试完整质量门槛不过不集成。

| Domain | Route | Maximum / restriction |
|---|---|---|
| Python deterministic pure helper + its unit tests | zcode L2_RESTRICTED trial, Codex independent acceptance | S / 2-6 named files，已冻结输入/输出；不涉及 DB/交易规则决策 |
| Vue/TypeScript local component/state and related tests | zcode L2_RESTRICTED trial, Codex independent acceptance | S / 2-6 named files；类型/build、键盘、desktop/mobile 检查；跨页面/auth/client 集成未测 |
| FastAPI/Pydantic/OpenAPI complete delivery | Codex; zcode L1 proposals | API 500 根因仍存在，不能独立接该域实现 |
| Focused feedback repair within authorized function/component | zcode in its L2 task, Codex reverify | 一次受控反馈；不能推广跨模块调试/重构 |
| ORM/migrations/real DB/worker/storage | Codex; zcode drafts only | UNPROVEN，需明确合同及真实环境专项验证 |
| Product/architecture policy, independent acceptance, Git integration | Codex / user product approval | 不自批，不让自评代替独立验收 |

按既定八维顺序（15/20/15/10/15/10/10/5）对教学 slice 暂评：Python `12/17/12/8/12/7/6/3 = 77/100`；Vue `12/17/12/9/9/7/6/3 = 75/100`；API `12/13/11/7/12/6/6/3 = 70/100`。评分为 reviewer judgment；API 被技术阻断优先限制，分数不自动授权。稳定性 3 分只来自这一次受控修复，重复真实交付仍未观察；各能力域不合并为“整个智能体分数”。

下一步在项目实际需要的低风险 Python/UI 任务中试用，不为了评估重写已有 helper。一次受控返修已用完；API 由 Codex 在必要任务中接管或重新限定合同，不自动派整轮 R2，不弱化生产约束。对 B1/B3 的 PASS_WITH_REQUIRED_FIXES 限于接下一个严格指定任务的资格，不接受其现有教学产物集成。

Independent browser launch repeated the previously approved isolated headless Chrome procedure; temporary server 127.0.0.1:19348 and browser were stopped. Build/cache/screenshots only in independent temp directory. Codex candidate source correction volume: zero. 是否能承担“大部分开发”留待真实 S 任务的通过率、检查范围和修复成本；本轮评估阶段已结束，可开始分域试用。
