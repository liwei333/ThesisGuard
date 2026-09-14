# TASK-WP04-01-GIT-INTEGRATION-R1 验收报告

**OVERALL: PASS**

## Metadata

- Task ID: `TASK-WP04-01-GIT-INTEGRATION-R1`
- Date: `2026-09-14`
- Verifier: Codex independent verifier
- Report Path: `docs/acceptance/TASK-WP04-01-GIT-INTEGRATION-R1-acceptance.md`
- Implementation Status: 已在本地 `main` 完成精确 fast-forward 集成、独立治理文档提交和集成后复验；未 push
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Missing Acceptance: `NONE`

## Changed Files Snapshot

- `BASELINE_CHANGED_FILES`: 正式验收开始时，`main@d8f38dd443f95da848338ebda901c288c4bc153a` 已包含任务的两个提交；工作区另有 `AGENTS.md`、`docs/ARCHITECTURE_REFERENCES.md` 和 `docs/CAPABILITY_RUNTIME_DECISION_2026-09-14.md` 三项可归因于后续 Capability Runtime 延后决策的未提交治理变更。
- `FINAL_CHANGED_FILES`: 上述三项非本任务治理变更保持不变；本次 verifier 另新增本验收报告。
- Task-attributable Changes:
  - `cb36e84515fddc8183630757a01078c655a1b8c2`：6 个 WP-04-01 Evidence persistence 业务/测试文件；
  - `d8f38dd443f95da848338ebda901c288c4bc153a`：4 份 WP-04-01 集成治理文档；
  - 本验收报告：verifier 持久化证据。
- Attribution: `CERTAIN`

## Classification

- Task Type: `GIT_INTEGRATION`, `DB_PERSISTENCE`, `MIGRATION`
- Risk Type: 默认分支变更、数据库完整性、不可变版本、幂等、审计、回归
- Touched Layers: Git history、ORM models、repository、migration、model registry、tests、acceptance docs
- Task Size: `MEDIUM`
- Evidence Matrix Type: `Full`
- Selected Gates: G0 Baseline、G1 Scope、G2 Contract、G4 Test、DB Persistence、G5 Regression、G6 Evidence
- Not Applicable Gates: G3 Architecture（本任务集成已验收实现，不批准架构或公共 API 变化）

## Top Blocking AC Results

| Top AC | Result | Evidence |
|---|---|---|
| TOP-AC-01 本地 `main` 必须以 fast-forward 方式只接入已验收候选 | `PASS` | `cb36e845...` 的唯一 parent 为 `c38c96f...`；`main` 历史无 merge commit |
| TOP-AC-02 业务提交和治理提交必须分离、范围精确 | `PASS` | `cb36e845...` 恰好 6 个业务/测试文件；`d8f38dd...` 恰好 4 个验收文档 |
| TOP-AC-03 已验收 Evidence 内容不得在 commit/merge 时漂移 | `PASS` | 5 个 Evidence blob 与来源提交 `4201ae7` 逐一一致；registry 只新增 12 行 imports |
| TOP-AC-04 集成后的真实 PostgreSQL 行为必须通过且无 skip | `PASS` | verifier 重跑 Evidence focused suite：`18 passed, 0 failed, 0 skipped` |
| TOP-AC-05 集成不得引入已知基线之外的新回归 | `PASS` | OpenAPI 专项 `1 failed, 9 passed`；全量 `1 failed, 84 passed`；唯一失败均为已知 canonical artifact 漂移 |
| TOP-AC-06 不得 push、修改后续模块或修复范围外 OpenAPI 漂移 | `PASS` | `origin/main` 仍为 `c38c96f...`；两个提交不含 API/前端/config/WP-04-02 文件；OpenAPI 失败仍存在 |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | `PASS` | 历史精确为 `c38c96f → cb36e845 → d8f38dd`；执行报告、前置 BLOCKED 报告与 readiness PASS 报告可访问 |
| G1 Scope | `PASS` | 两个提交分别严格为 6 个业务/测试文件和 4 个治理文档，无夹带 |
| G2 Contract | `PASS` | fast-forward、提交分离、无 push、集成后验证和反馈边界全部满足 |
| G3 Architecture | `NOT_APPLICABLE` | 未修改公共架构、API、配置或后续工作包行为 |
| G4 Test | `PASS` | verifier 新鲜执行 Evidence、Research、OpenAPI、全量、Ruff、mypy、compileall、Alembic checks |
| DB Persistence | `PASS` | 真实 PostgreSQL Evidence 测试 18/18，通过迁移、约束、版本/current/tombstone/幂等行为 |
| G5 Regression | `PASS` | Research 16/16；全量唯一失败与已知基线完全一致，没有新增失败 |
| G6 Evidence | `PASS` | Full Evidence Matrix 完整；Git 对象、blob、实际命令和负向检查均由 verifier 独立读取/运行 |

## Full Evidence Matrix

| AC | Requirement | Implementation Evidence | Verification Evidence | Boundary/Negative Evidence | Verdict |
|---|---|---|---|---|---|
| AC-01 [BLOCKING] | 候选必须从精确授权基线 fast-forward 进入本地 `main` | `cb36e845...` parent=`c38c96f...`; `d8f38dd...` parent=`cb36e845...` | `git rev-list --parents`、`git log`、`git rev-parse HEAD main` | 两个新提交均为单父提交，无 merge commit | `PASS` |
| AC-02 [BLOCKING] | 业务提交只能包含 6 个目标文件 | commit `cb36e845...` | `git show --name-status cb36e845...` 恰好列出 6 个文件 | 无 API、前端、配置、WP-04-02 或其他模块文件 | `PASS` |
| AC-03 [BLOCKING] | 治理提交只能包含 4 份指定文档 | commit `d8f38dd...` | `git show --name-status d8f38dd...` 恰好列出 4 个文件 | 与业务提交分离；没有 squash/amend 痕迹 | `PASS` |
| AC-04 [BLOCKING] | Evidence 实现内容保持已验收语义 | models/repositories/migration/two test files + registry | 5 个 blob candidate/source SHA 相同；逐文件 `git diff --exit-code` 为 0 | registry 保留主线 docstring、中文说明和 future-model comments；无 conflict marker | `PASS` |
| AC-05 [BLOCKING] | 集成后 Evidence DB/迁移合同真实可用 | ORM、repository、revision 0004、focused tests | 真实 PostgreSQL：`18 passed, 2 warnings in 12.20s`，0 skip | 非 SQLite/mock；覆盖重复身份、版本/current、tombstone、迁移往返等反例 | `PASS` |
| AC-06 [BLOCKING] | 既有 Research 行为不得回归 | WP-03 Research implementation | `16 passed, 4 warnings in 10.24s` | 无 Research 文件改动；旧路径测试全绿 | `PASS` |
| AC-07 [BLOCKING] | 静态质量和迁移图必须健康 | 集成后的 `main` tree | Ruff 通过；mypy 48 files 通过；compileall 退出 0；Alembic `000000000004 (head)` | 无额外 Alembic head、类型错误或 lint 错误 | `PASS` |
| AC-08 [BLOCKING] | 不得引入基线外回归 | 集成后的 85-test suite | OpenAPI `1 failed, 9 passed`; full `1 failed, 84 passed` | 唯一失败精确为既有 `test_canonical_openapi_artifact_matches_current_fastapi_app` | `PASS` |
| AC-09 [BLOCKING] | 不得 push 或扩大下一阶段范围 | 本地 log/ref/tree | `origin/main=c38c96f...`; `main=d8f38dd...` | 无 WP-04-02、OpenAPI 修复、provider/runtime 或其他功能提交 | `PASS` |

## Commands Actually Executed

| Command | Result | Purpose |
|---|---|---|
| `git status --short --branch` | `main...origin/main [ahead 2]`，另有 3 项已归因的后续治理变更 | 锁定当前状态和 attribution |
| `git rev-parse HEAD main origin/main codex/wp04-01-readiness-r1` | `d8f38dd...`, `d8f38dd...`, `c38c96f...`, `cb36e845...` | 验证本地集成和未 push 边界 |
| `git log` / `git rev-list --parents` | 精确父子链 `c38c96f → cb36e845 → d8f38dd` | 验证 fast-forward 与提交分离 |
| `git show --name-status <commit>` | 业务 6 文件；治理 4 文件 | 验证提交范围 |
| `git diff-tree --check` | 两个提交均退出 0 | diff hygiene |
| `git ls-files -u` | 无输出 | 排除未解决冲突 |
| 5 个文件的 `git rev-parse <commit>:<file>` 与 `git diff --exit-code` | blob 全部匹配 `4201ae7` | 排除 commit/merge 语义漂移 |
| registry 精确 diff + conflict marker 搜索 | 仅新增 Evidence imports；无 marker | 验证冲突解决 |
| `find apps -maxdepth 3 -name node_modules -type l -print` | 无输出 | 排除残留临时依赖链接 |
| `pytest ... test_evidence_migrations.py test_evidence_persistence.py` | `18 passed, 2 warnings in 12.20s` | 真实 DB/迁移/仓储验证 |
| `pytest ... test_research_api.py test_research_persistence.py` | `16 passed, 4 warnings in 10.24s` | Research 回归 |
| `ruff check backend/ apps/` | `All checks passed!` | lint |
| `mypy --explicit-package-bases backend apps --ignore-missing-imports` | `Success: no issues found in 48 source files` | 类型检查 |
| `python -m compileall -q backend apps migrations tests` | exit 0 | 编译检查 |
| `alembic -c migrations/alembic.ini heads` | `000000000004 (head)` | migration graph |
| `pytest ... tests/test_frontend_openapi_client.py -rs` | `1 failed, 9 passed, 2 warnings in 0.65s` | 已知 OpenAPI 漂移对照 |
| `pytest -p no:cacheprovider -q` | `1 failed, 84 passed, 4 warnings in 116.81s` | 全量回归 |

## Counterexample / Negative Verification

| Risk | Checked? | Evidence | Verdict |
|---|---|---|---|
| 非 fast-forward 或隐藏 merge commit | 是 | 两个新提交均为单父提交，业务提交直接继承授权基线 | 未命中 |
| 业务提交夹带下一工作包/API/配置改动 | 是 | 文件集合严格为 registry、2 个 Evidence 文件、migration、2 个测试 | 未命中 |
| commit hook 或 merge 改写已验收内容 | 是 | 5 个 blob 与来源完全一致；registry 精确 diff 符合约定 | 未命中 |
| 数据库测试依赖 skip、SQLite 或 mock | 是 | 18 个测试连接真实 PostgreSQL，0 skip | 未命中 |
| 修复 Evidence 时破坏 Research | 是 | Research 16/16，且 Research 文件未修改 | 未命中 |
| 用既有 OpenAPI 漂移隐藏新失败 | 是 | 专项和全量的失败 node id 均唯一且精确匹配既有基线 | 未命中 |
| 未授权 push 或远端分支移动 | 是（以本地 refs 为证据） | `origin/main` 仍为 `c38c96f...`，本地 `main` ahead 2 | 未命中；未联网 fetch，不把本地 remote-tracking ref 表述为远端实时强证明 |
| 临时依赖符号链接污染仓库 | 是 | node_modules symlink 搜索为空 | 未命中 |

## DB Persistence Result

- Schema constraints: focused migration/persistence suite 在真实 PostgreSQL 上通过，包括必填、唯一、外键和枚举/检查约束路径。
- Read semantics: current/latest、source-version、状态和 lineage 读取语义通过测试。
- Replace semantics: replacement/new-series 与旧 current 结果不回流路径由 focused suite 覆盖。
- Active/inactive/deleted/status: tombstone/retracted/current 状态语义由 focused suite 覆盖。
- Transaction boundary: 多表 repository 写入与失败不产生部分权威状态的测试通过。
- Version/snapshot/history: revision `3 → 4 → 3 → 4`、append-only 版本与 current 解析通过。
- Real persistence vs InMemory/Fake/Mock: `L4_DB_VERIFIED` 来自真实 PostgreSQL，不依赖 InMemory/Fake/Mock 替代。

## Blocking Findings

`NONE`

## Non-Blocking Findings

1. canonical OpenAPI artifact 漂移仍导致专项和全量测试各保留同一个既有失败。它不是本任务引入，但使仓库全量门禁仍非全绿；应在 WP-04-03 API/OpenAPI 之前建立独立修复或明确纳入该任务的前置修复阶段。
2. 测试仍产生 Starlette/httpx、AnyIO HTTP 422 等弃用 warning；数量未因本任务扩大。
3. 本地 `main` 比 `origin/main` 超前两个提交；未 push 符合本任务边界，但远端尚不包含本地集成成果。
4. 当前工作区有 3 项由后续用户授权的 Capability Runtime 延后决策产生的未提交治理文档变更。它们不是 WP-04-01 集成漂移，但在下一业务开发任务前应与本验收报告一起完成治理收尾。
5. README、PRD、TAD、AGENTS 和 architecture authority map 中仍有“WP-04-01 未合并 / main 为 CONTRACT_ONLY”的历史当前态描述；在本次集成后已形成 documentation drift，需要最小状态同步，但不得改写历史 acceptance 记录。

## Regression Result

- Result: `PASS`
- Preserved behavior: Research API/persistence、已有 health/config/instrument/watchlist/system/tasks 测试均保持；全量通过项从集成前 66 增至 84。
- Regression gaps: 未做生产部署或真实用户验证；不属于本地 WP-04-01 persistence integration 的 Required Acceptance。

## Repair Required

- `NO`
- Repair ID: `N/A`
- Failed AC/Gate: `NONE`

## Final Decision Rationale

`PASS`。授权基线、fast-forward 历史、两个提交的精确边界、blob 完整性、registry 冲突解决、真实 PostgreSQL 行为、Research 回归、静态质量和全量失败集合均由 verifier 独立核验。所有 Blocking AC 和选定 Gate 都有足够证据。唯一测试失败是合同明确允许且已经在原基线存在的 canonical OpenAPI artifact 漂移，没有新增失败或范围漂移。

该 PASS 只关闭 `TASK-WP04-01-GIT-INTEGRATION-R1` 和 WP-04-01 persistence foundation 的本地 main 集成，不代表整个 WP-04、Evidence Service/API/worker/MinIO/RAG、WP-05 或产品已完成，也不证明远端或生产环境就绪。

## Next Action

先执行一个 docs-only 的治理收尾任务：提交本报告和 `ADR-2026-09-14-CAP-01`，并把 canonical README/PRD/TAD/AGENTS/architecture authority map 中已经过期的 WP-04-01 current-state 描述同步为“persistence foundation 已在本地 main 通过验收；WP-04 service/API/typed links 仍未实现”。该任务完成并独立验收后，再派发 `TASK-WP04-02` Evidence Domain Service。
