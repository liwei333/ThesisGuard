# TASK-WP04-01-INTEGRATION-READINESS-R1 验收报告

## 1. Verdict

`PASS — READY_FOR_GIT_INTEGRATION_PENDING_USER_AUTHORIZATION`

本次 R1 修复候选已经满足修复合同定义的集成准备条件：候选基于精确的当前 `main@c38c96fe6c6b61cd2d45f3d5af9be736d0db0f00`，冲突已消除，变更范围严格限制为 6 个目标文件，5 个 Evidence 文件与原功能提交 `4201ae754c0cf71188965987964d2221795cb5eb` 的 blob 完全一致，registry 合并同时保留了 `main` 的说明和尾部注释。数据库、迁移、静态质量、Research 回归与全量回归均已独立验证。

该结论仅表示“候选可以进入经用户授权的 Git 集成步骤”，不表示已经合并到 `main`，也不表示 `main` 当前已经具备 Evidence 持久化能力。

## 2. Acceptance Metadata

| Field | Value |
|---|---|
| Task ID | `TASK-WP04-01-INTEGRATION-READINESS-R1` |
| Acceptance date | `2026-09-14` |
| Repository | `/Users/qianduoduo/Desktop/AI_app/ThesisGuard` |
| Baseline / current `main` | `c38c96fe6c6b61cd2d45f3d5af9be736d0db0f00` |
| Source feature commit | `4201ae754c0cf71188965987964d2221795cb5eb` |
| Candidate branch | `codex/wp04-01-readiness-r1` |
| Candidate worktree | `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-01-readiness-r1` |
| Candidate HEAD | `c38c96fe6c6b61cd2d45f3d5af9be736d0db0f00` |
| Candidate state | 6 个目标文件已暂存、未提交、未合并 |
| Change class | `MEDIUM / Repair / DB Persistence + Migration` |
| Gate matrix | `FULL` |
| Required acceptance levels | `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED` |
| Achieved acceptance levels | `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED` |
| Missing levels | `NONE` |

## 3. Scope and State Control

### 3.1 Candidate delta

候选的暂存区仅包含以下 6 个文件：

```text
M  backend/common/db/models_registry.py
A  backend/evidence/models.py
A  backend/evidence/repositories.py
A  migrations/versions/20260914_004_evidence_persistence.py
A  tests/test_evidence_migrations.py
A  tests/test_evidence_persistence.py
```

`git diff --cached --stat` 显示 6 个文件、3633 行新增；不存在 API、前端、配置或其他业务模块的越界变更。

### 3.2 Main worktree integrity

验收前后 `main` 与当前 `HEAD` 均保持在：

```text
c38c96fe6c6b61cd2d45f3d5af9be736d0db0f00
```

主工作区没有因本次验证产生业务代码修改。验收开始时已存在、且继续保留的未跟踪治理文档为：

```text
docs/acceptance/TASK-WP04-01-INTEGRATION-READINESS-acceptance.md
docs/acceptance/TASK-WP04-01-INTEGRATION-READINESS-R1-repair-contract.md
```

本报告是本次验收新增的治理证据，不属于候选业务代码。

### 3.3 Temporary verification dependency

候选 worktree 本身没有独立的 `apps/web/node_modules`。为区分依赖环境缺失与真实 OpenAPI 回归，验收期间曾临时链接主工作区现有依赖目录并执行相关测试；测试后该链接已经删除。候选最终状态仍只有上述 6 个目标文件。

## 4. Acceptance Criteria Results

| ID | Acceptance criterion | Result | Evidence |
|---|---|---|---|
| AC-1 | 候选必须基于精确的当前 `main`，不得重放到陈旧基线 | `PASS` | candidate `HEAD`、`main` 与主工作区 `HEAD` 均为 `c38c96f...` |
| AC-2 | 仅集成规定的 6 个目标文件，不得夹带越界变更 | `PASS` | 暂存状态恰好为 6 个指定文件；cached diff 也只有这 6 个文件 |
| AC-3 | Evidence 的 5 个新增文件必须保持原功能提交语义不漂移 | `PASS` | 5 个候选 blob 与 `4201ae7` 对应 blob 逐一完全一致，`git diff --exit-code` 返回 0 |
| AC-4 | `models_registry.py` 必须正确解决冲突，同时保留 `main` 的注册说明与尾部注释 | `PASS` | cached diff 仅新增 12 行 Evidence imports；`main` 的完整 docstring、中文说明和 future-model comments 均保留 |
| AC-5 | 不得存在未解决冲突、冲突标记或 whitespace 错误 | `PASS` | `git ls-files -u` 为空；未发现冲突标记；`git diff --cached --check` 无输出、退出 0 |
| AC-6 | Evidence 数据库、迁移与仓储合同必须在真实 PostgreSQL 上通过 | `PASS` | Evidence focused tests：`18 passed`，无 skip |
| AC-7 | 不得破坏既有 Research 持久化行为 | `PASS` | Research focused tests：`16 passed` |
| AC-8 | 不得引入新的全量测试失败 | `PASS` | baseline：`1 failed, 66 passed`；candidate：`1 failed, 84 passed`；失败集合相同，均为既有 OpenAPI artifact 漂移 |
| AC-9 | 静态质量、类型检查、编译与 Alembic 单头必须通过 | `PASS` | Ruff、mypy、compileall 全部通过；Alembic head 为 `000000000004 (head)` |
| AC-10 | 验收不得擅自提交或合并候选 | `PASS` | candidate 仍为 6 个 staged、uncommitted 文件；`main` 未移动 |

## 5. Gate Results

### G0 — Baseline and Provenance: `PASS`

- 当前 `main`、主工作区 `HEAD` 和候选 `HEAD` 均精确解析为 `c38c96fe6c6b61cd2d45f3d5af9be736d0db0f00`。
- 功能来源提交精确解析为 `4201ae754c0cf71188965987964d2221795cb5eb`。
- 候选是在独立 worktree 的专用分支上准备，未污染 `main`。

### G1 — Scope and Anti-drift: `PASS`

- 候选只修改修复合同列出的 6 个文件。
- 5 个 Evidence 新增文件与来源提交完全一致。
- registry 的合并内容仅加入 Evidence 模型 imports，同时保留当前 `main` 的既有文本。
- 无 API、前端、文档、配置或后续工作包实现混入候选。

### G2 — Static / Build Quality: `PASS`

独立执行结果：

```text
ruff check backend/ apps/
All checks passed!

mypy --explicit-package-bases backend apps --ignore-missing-imports
Success: no issues found in 48 source files

python -m compileall -q backend apps migrations tests
exit 0

alembic -c migrations/alembic.ini heads
000000000004 (head)
```

### G3 — External API Compatibility: `N/A`

候选没有 API 路由或前端 API 客户端变更。本轮仍对 OpenAPI 相关测试进行了回归对照，结果记录在 G5。

### G4 — Contract and Focused Behavior: `PASS`

```text
pytest -p no:cacheprovider -q \
  tests/test_evidence_migrations.py \
  tests/test_evidence_persistence.py

18 passed, 2 warnings in 12.54s
```

该组测试在真实 PostgreSQL 上运行，无跳过，覆盖迁移往返、约束、写入与读取、current-version 语义、tombstone 语义和幂等行为。

### DB Persistence / Migration Gate: `PASS`

- Alembic 只有一个 head：`000000000004`。
- Evidence 迁移与持久化测试在真实 PostgreSQL 上 `18/18` 通过。
- 首次在受限 sandbox 内执行时，16 个数据库用例因本机 PostgreSQL socket 访问被拒而报 `PermissionError`；这是执行环境权限问题，不是候选业务失败。随后在允许本机数据库访问的验证环境中重跑并全部通过。
- Research 持久化/API 重点回归：

```text
16 passed, 4 warnings in 10.08s
```

### G5 — Regression: `PASS`

主线基线：

```text
1 failed, 66 passed, 4 warnings in 102.93s
```

R1 候选：

```text
1 failed, 84 passed, 4 warnings in 23.47s
```

两边唯一失败均为：

```text
tests/test_frontend_openapi_client.py::
test_canonical_openapi_artifact_matches_current_fastapi_app
```

候选比基线多通过 18 个 Evidence 测试，没有新增失败。该 OpenAPI canonical artifact 漂移在 `main` 上已经存在，与本次 6 文件候选无因果关系，因此按 R1 修复合同属于非阻断既有残留。

在为候选补齐临时前端依赖后，OpenAPI 专项结果同样为：

```text
candidate: 1 failed, 9 passed
main:      1 failed, 9 passed
```

失败集合完全一致。

### G6 — Evidence and Repository Hygiene: `PASS`

- `git ls-files -u`：为空。
- `git diff --cached --check`：通过。
- 候选最终状态：仅 6 个规定文件 staged、uncommitted。
- 验证所用临时 `node_modules` 链接已删除。
- 主工作区业务代码与 Git 引用未被验收过程修改。

## 6. Exact Blob Evidence

| File | Candidate / source blob |
|---|---|
| `backend/evidence/models.py` | `bbf2599f0c5c28af6bb7d2e3a0ec2e8ffc87554c` |
| `backend/evidence/repositories.py` | `13aa23edc6ec963c6be592694122703b1b86c89c` |
| `migrations/versions/20260914_004_evidence_persistence.py` | `e5127175a204f505bbe4717a24bc8bbdb8e43437` |
| `tests/test_evidence_migrations.py` | `f28e30b509b7c7ef6892e9dd5a24df88d2486386` |
| `tests/test_evidence_persistence.py` | `ca832aab843bcd48b7c82bf9d8c1af27f2c4b44f` |

上述候选 blob 与 `4201ae754c0cf71188965987964d2221795cb5eb` 中对应文件逐一相同。

## 7. Counterexample Checks

1. **陈旧基线反例**：若候选仍基于旧提交，应当阻断；实际候选与当前 `main` 精确同基线，未命中。
2. **粗暴覆盖 registry 反例**：若 Evidence 版本覆盖 `main` 文案或未来注册注释，应当阻断；实际仅追加模型 imports，未命中。
3. **语义漂移反例**：若 5 个 Evidence 文件与来源提交不一致，应当阻断；实际 blob 全部一致，未命中。
4. **伪数据库验证反例**：若测试被 skip、仅靠 SQLite 或没有真实迁移执行，应当阻断；实际真实 PostgreSQL 运行 `18/18` 通过，未命中。
5. **新增回归反例**：若 candidate 的失败集合大于 baseline，应当阻断；实际两边唯一失败相同，candidate 仅增加 18 个通过项，未命中。
6. **脏候选反例**：若存在 unmerged entries、冲突标记、额外文件或残留临时依赖，应当阻断；实际均不存在，未命中。

## 8. Findings

### Blocking findings

`NONE`

### Non-blocking residuals

1. `main` 已存在 canonical OpenAPI artifact 漂移，导致全量测试保留 1 个既有失败。该问题不由 R1 候选引入，建议另立修复任务，不应混入 WP-04-01 的 Git 集成提交。
2. 测试存在 Pydantic / SQLAlchemy 相关 warning；本次没有扩大 warning 数量，也不影响修复合同。
3. 候选尚未提交、尚未合并；这是有意保留的授权边界，不是缺陷。

## 9. Repair Decision

`REPAIR_REQUIRED: NO`

R1 已修复前次验收指出的陈旧基线、冲突候选缺失和不可验证集成状态问题。无需再开 R2 修复；下一步应进入单独、可审计的 Git 集成任务。

## 10. Final Decision and Boundary

本次验收结论为 `PASS`。允许进入下一阶段的前提是用户明确授权执行 Git 集成。下一阶段只能：

1. 对当前已验收的 6 文件候选建立提交；
2. 将该提交集成到仍为 `c38c96f...` 的 `main`；
3. 保留并提交相关验收治理证据；
4. 在集成后的真实 `main` 上重复关键检查，确认失败集合仍没有扩大；
5. 报告最终 commit、文件集合、测试证据与工作区状态。

在完成并验收 Git 集成之前，不应宣称 WP-04-01 已在 `main` 可用，也不应开始 WP-04-02。
