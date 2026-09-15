# TASK-WP04-02-R1B-R2 Acceptance

**OVERALL: BLOCKED**

## Metadata

- Task ID: `TASK-WP04-02-R1B-R2`，已提供修复候选的独立验收，不是新的 R3。
- Date: 2026-09-15，Asia/Shanghai。
- Verifier: Codex，独立源码/合同/Git/hash 与静态命令核验。
- Report Path: `docs/acceptance/TASK-WP04-02-R1B-R2-acceptance.md`；路径沿用 AGENTS.md 的 docs/acceptance 治理约定。
- Implementation Status: 执行反馈为 `IMPLEMENTATION_COMPLETE`，不是本报告的完成证明。
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`。
- Achieved Acceptance: `L1_STATIC_REVIEWED`（R2 目标接线及相关观察测试的静态核验）；`L2_BUILD_VERIFIED`。
- Missing Acceptance: 新的独立 `L3_CONTRACT_VERIFIED` 与 `L4_DB_VERIFIED`。
- Repair Required: 未建立新代码缺陷，不新增 R3；R2 待独立真实 DB 复验，R1B 未关闭。
- Next Action: 用户明确批准本次独立复验的已披露本地临时 PostgreSQL 操作后，通过正常权限机制执行原 R2 验证矩阵。

## Classification

Task Type: REPAIR acceptance / SMALL，单一生产 exact-target 接线边界。Risk: persistence, immutable audit/history, idempotency, test permission。Touched layers: service/tests；verifier 本轮另有用户授权的 docs-only Sector Crowding 记录。Evidence Matrix: Full。

Selected Gates: G0 baseline, G1 scope, G2 contract, G3 architecture, G4 test, DB persistence, G5 regression, G6 evidence。Frontend/API change/provider/production gates不适用本次修复。已有 R1C/R1D 待修主题不扩大进 R2 验收。

## Fresh Snapshot / Attribution

- Candidate worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`。
- Branch: `codex/wp04-02-evidence-domain-service`。
- HEAD: `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`；parent: `3eb494e6613cf3952ffbaaf4166b8cf3ea801555`。
- BASELINE_CHANGED_FILES = FINAL_CHANGED_FILES: `M backend/evidence/services.py`, `M tests/test_evidence_services.py`。
- Verifier-attributable candidate changes: none。
- Main inspection baseline: `7d4e395d949d8cd050548347f31dd6b492f65834`，10 个既有 untracked 验收/治理文档保留；未 fetch，不声明远端实时状态。
- 相对 candidate HEAD 的累计 diff 为 services 564 行、tests 1102 行差异，包含已存在的 R1B/R1 修复；不能把累计 1599 insertions / 67 deletions 都归因于此次 R2。新接线位置与反馈对应；未取得 R2 修复前完整文件副本，历史动作与精确逐行归因不独立认证。

Fresh hashes，均匹配反馈最终值：

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
2f90167c131cf91c715fc7fb19ead5af9745fab3259c7af0c875474bb0ce444f  backend/evidence/services.py
a8b5e8e814230b21d732f2e973a62cdd0b69d00455ea29130b1750994d8bed2a  tests/test_evidence_services.py
909f50bd902ecd9c0013121681b614fcbc302f718cc7c9d5dc96f6237d106786  /tmp/test_wp04_02_r1b_r1_wiring_20260915.py
```

## Top Blocking AC / Full Evidence Matrix

| AC | Requirement | Implementation Evidence | Fresh Verification Evidence | Boundary / Negative Evidence | Verdict |
|---|---|---|---|---|---|
| TOP-AC-01 | 真正的新 exact ID 在新版本/children 写入前用于所有 DERIVED create/replacement/append 校验 | services.py:714 显式新 ID；:760 带实际 target，先于 db.add/flush；:1398 / :1445 覆盖共同 append；:1159 replacement 复用 create | 独立读取调用顺序和新四路径测试；静态命令通过 | 新版本尚未 add 时做查询，不是通过 provisional insert 获取 ID；仍缺真实 DB 三节点及四路径 timing 实测 | BLOCKED |
| TOP-AC-02 | exact self / reachability defense 实际运行且无残留 | _validate_derivation_links 和 _support_graph_reaches_exact_version 使用 exact IDs；生产调用已传 target | 独立读取 helper、wiring verifier 与转发真实实现的观察器 | 不把 same-series 禁止代替 exact graph；未在本轮运行 self/multi-hop/no-residue 反例 | BLOCKED |
| TOP-AC-03 | 保护合法 replacement、metadata-only N+1、历史 children、R1A 与其余 R1B | 原 R1B/R1 合同与 replacement/append 路径；新增观察测试未代替真实 DB 操作 | 源码检查 only；反馈声称旧 verifier 4 / 12 passed | 历史/自述结果不等于当前独立回归；R1C/R1D 不在此 scope | BLOCKED |
| TOP-AC-04 | 原完整矩阵全绿、errors 不变、两文件范围与 HEAD 不变 | Fresh status / hashes / HEAD；wiring verifier hash 未变 | Ruff / format / mypy / compileall / heads / diff check exit 0 | 所有六条 PostgreSQL pytest 未由本 verifier 执行；权限来源未独立核验 | BLOCKED |

## Gate Results

| Gate | Verdict | Evidence / limitation |
|---|---|---|
| G0 Baseline | PASS | Candidate branch/HEAD/parent/status/final hashes匹配；合同与执行反馈可读取 |
| G1 Scope | PASS | 当前净候选变化仅允许的两文件，errors byte-identical；新增四路径观察器转发真实 validator/helper/flush，没有以 stub 替代；不认证过去所有工具操作 |
| G2 Contract | BLOCKED | L1 接线对应要求，缺少必需的新独立行为证据 |
| G3 Architecture | PASS | 新 ID 私有分配、不进入请求 hash/调用者 API；校验先于 add/flush；服务未新增 commit 或 schema 变更 |
| G4 Test | BLOCKED | 静态检查全绿；原六条 DB pytest 没有本轮结果 |
| DB persistence | BLOCKED | Fixture 可读取但未执行，不宣称当前 DB 健康、实际写入/清理或 no-residue |
| G5 Regression | BLOCKED | 缺少当前 R1A/R1B/full service/35-case regression 的独立结果 |
| G6 Evidence | BLOCKED | Full matrix显式保留缺失证据；执行者自述不能关闭行为/DB gates |

## Commands Actually Executed

从 candidate worktree 执行以下命令，均 exit 0：

```bash
git status --short --branch
git rev-parse HEAD HEAD^
git diff --stat
git diff --check
shasum -a 256 backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py /tmp/test_wp04_02_r1b_r1_wiring_20260915.py
ruff check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
ruff format --check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
MYPYPATH=. mypy --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1b-r2-acceptance-mypy backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
PYTHONPYCACHEPREFIX=/tmp/tg-r1b-r2-acceptance-pycache python -m compileall -q backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
alembic -c migrations/alembic.ini heads
```

结果：Ruff All checks passed；3 files already formatted；mypy no issues（已有 unused config section note）；compileall/diff check 无错误；revision graph head 为 `000000000004`。heads 是本地 revision graph，不证明当前数据库已迁移。

另外读取了 AGENTS、原 R2 / R1 execution / permission supplement、repair program、来源文档、target-aware create/append/replacement/helper、四路径测试、wiring verifier 和真实 DB fixture。没有 pytest、DB connect、Docker、任意 SQL、escalation retry、Git 历史变更或业务文件编辑。

## Executor Claims — Not Fresh Independent Results

附件声称修复前 red 为 3 failed，修复后 wiring 3 passed、旧 R1B 4 passed、R1A 12 passed、R1B focused 9 passed、full service 100 passed、regression 35 passed。它还声称曾得到显式用户授权并通过正常 escalation。

本 verifier 未取得这些原始工具结果或用户授权事件，不据此否认执行者当时可能已获批准；但也不将附件自述提升为独立实测或当前拒绝后的重试授权。旧 R1B-R1 acceptance 的 FAIL 保持其历史意义，不用新静态观察覆写历史。

## Permission / Required Input

现有 permission-resume 文件仍标为 PENDING_USER_AUTHORIZATION。这可能是未同步的文档，不单独证明历史授权不存在。当前可见用户消息要求记录及验收，没有明确采用原风险披露后的六条 DB pytest 授权；鉴于此前拒绝明确禁止绕路重试，本轮未重试相同 DB 结果。

需要用户明确批准：从精确 candidate worktree，通过正常权限机制运行原 R2 六条 pytest，连接本机 `127.0.0.1:15432` 的测试管理库；fixture 创建随机临时数据库，在临时库运行现有迁移与测试，正常只终止/清理本次自己创建的临时库。操作消耗本地资源，失败可能留临时库，须报告而不广泛清理。

授权不包括 main/Git 修改、共享/生产 DB reset 或迁移、任意 SQL/按前缀清理、外部实例、改端口/代理/Docker 绕路、环境重配置、修改 verifier 或业务合同。工具若仍拒绝须保持 BLOCKED，不绕过。

## Findings / Decision

- BLOCKING：当前验收所必需的独立真实 PostgreSQL 行为与回归证据无法在已可核验授权内补足。
- NON-BLOCKING：观察测试转发真实实现，候选接线顺序确实改善；静态检查与哈希匹配不证明所有业务 AC。
- 新代码 Repair Required：NO，未建立 R3 缺陷；不能将 permission/evidence block 误报为 semantic FAIL。

唯一整体结论为 BLOCKED。保持候选不动。下一任务仅为 `TASK-WP04-02-R1B-R2-INDEPENDENT-REVERIFY`；PASS 后再选原 repair program 中的 R1C，仍不授权 R1D、WP04-03 或 Git integration。后续复验记录新报告，不覆写本次 BLOCKED 或旧 FAIL。
