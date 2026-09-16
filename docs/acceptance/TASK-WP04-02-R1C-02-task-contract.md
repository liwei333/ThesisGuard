# TASK-WP04-02-R1C-02 — Lifecycle Command Matrix Repair

Status: `READY_FOR_USER_DISPATCH`；读取本文件不自动执行业务或授予工具权限。

## A. Execution Core

- Task ID: `TASK-WP04-02-R1C-02`。
- Objective: 对齐现有review/dispute/invalidation/retraction命令的from/to状态与审计kind，合法命令追加N+1，非法命令无残留。
- Why Now: R1C-01已独立PASS；当前status命令仍过宽或缺合法分支。先修该写入边界，再做trusted registry。
- Role / Type / Size: EXECUTOR / REPAIR / SMALL，现有status命令的一个状态表边界。
- Required Acceptance: L1_STATIC_REVIEWED、L2_BUILD_VERIFIED、L3_CONTRACT_VERIFIED、L4_DB_VERIFIED；Full matrix。

### Baseline / Required Reading

主仓 `/Users/qianduoduo/Desktop/AI_app/ThesisGuard`：完整读取AGENTS.md、本合同、R1C-01正式验收报告、R1C-01 task-contract/dispatch-prompt、原R1 repair program、冻结Evidence合同第12/13节及相关命令/错误/审计定义。相关治理文档从主仓读，不假设候选有副本。

候选 `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`；branch `codex/wp04-02-evidence-domain-service`；HEAD `bdd70edc153b6ed5def65ed99c41f325df45f066`；parent `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`。

**起点已dirty且恰好两文件modified；不是clean gate。保留全部已验收R1C-01变更，不reset/checkout或先commit。**

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
cecffcd52371baf6bb6e85e733e565f4720e78d3d50fb65503b5d74998517df3  backend/evidence/services.py
aabe09b394fa4d23a13f245c512afc11d8c2100e3c85ab7b2569f89133d4e7e4  tests/test_evidence_services.py
909f50bd902ecd9c0013121681b614fcbc302f718cc7c9d5dc96f6237d106786  /tmp/test_wp04_02_r1b_r1_wiring_20260915.py
0f7cea4d14735bd165b75d756444259a64483a97e6a338227bc09af806490cc9  /tmp/test_wp04_02_r1b_reverify.py
66be45f354d1df34370eedd9811b3bc68cf29852d45027ea576a67975b18ddfe  /tmp/test_wp04_02_r1a_verifier.py
857914f073c552be98f895a456d2f0ec486452e1c9aed06a87176c6e7fefd48a  /tmp/test_wp04_02_r1c_01_independent_20260915.py
```

先核对以上状态/哈希并读取相关services/private status helpers、models、repositories、tests/fixtures。缺失或不符则BLOCKED，不静默更换基线或修改独立verifier。

### Top Blocking AC

1. 下表合法status命令成功且恰好追加N+1；其余七状态×命令/decision组合返回既有invalid-state错误，除既有同请求幂等重放；不把REJECTED/INVALIDATED/RETRACTED作为旧行可原地提升。
2. 普通review使用REVIEW_REQUEST/REVIEW_DECISION，dispute resolve必须DISPUTE；invalidation/retraction分别用INVALIDATION/RETRACTION。时间、actor、kind、reason完整且语义正确；不能继承旧audit字段伪装新事件。
3. 非法输入/非法transition/expected-version conflict不写version、children、idempotency、audit；合法status append保留内容/children、exact lineage、历史，服务不commit。已有same-request replay行为保持，不顺带重构R1D。
4. 先真实PG RED再最小修复GREEN；完整命令组合正反矩阵、R1C-01资格/历史、R1A/R1B/verifiers与完整回归/static全通过。
5. 仅授权两文件业务修改、errors/verifiers/contract/schema/HEAD不变；提供基线与本任务增量证据，不能自我验收或宣布整个R1C/WP04-02完成。

### Selected Frozen Transition Matrix

使用现有public函数；不新增API/schema。verify_or_reject的DISPUTED分支承接冻结resolve_dispute两种语义，不要求新增公开函数。

| Existing function / decision | Allowed from | To | audit kind |
|---|---|---|---|
| request_review | UNREVIEWED | PENDING_REVIEW | REVIEW_REQUEST |
| verify_or_reject / VERIFIED | PENDING_REVIEW | VERIFIED | REVIEW_DECISION |
| verify_or_reject / REJECTED | UNREVIEWED、PENDING_REVIEW | REJECTED | REVIEW_DECISION |
| verify_or_reject / VERIFIED | DISPUTED | VERIFIED | DISPUTE |
| verify_or_reject / REJECTED | DISPUTED | REJECTED | DISPUTE |
| mark_disputed | VERIFIED | DISPUTED | DISPUTE |
| retract_or_invalidate / INVALIDATED | VERIFIED | INVALIDATED | INVALIDATION |
| retract_or_invalidate / RETRACTED | VERIFIED、DISPUTED | RETRACTED | RETRACTION |

此表只覆盖四个现有status命令；**不是create/import/replacement/ordinary/trusted correction完整状态表的关闭证明**。InstrumentLink不是Research/Thesis downstream consumption，不能因reject命令删掉历史或instrument children。若冻结合同中消费限制需尚未实现模块才能校验，报告边界，不新增模块假装闭环。

### Scope / Must / Must Not

只允许改candidate services.py、tests/test_evidence_services.py，必要private status helper可最小调整。沿用现有错误code与公开签名。

先加真实PG矩阵测试取得RED，再修生产。至少包含：UNREVIEWED直接reject合法；PENDING_REVIEW或REJECTED mark_disputed非法；UNREVIEWED/REJECTED/DISPUTED invalidate非法；DISPUTED resolve两分支audit kind DISPUTE；DISPUTED retract合法；terminal状态不得经四个status命令再次晋升；expected-version与invalid decision失败无残留。

测试状态优先由冻结合法公开路径建立；不可表达时，按R1C-01约定只在真实fixture合法追加测试版本，不改生产检查或旧行。不能仅测happy path，必须列出七状态与各命令/decision的完整允许/拒绝组合。

已有 `test_revision_lifecycle_and_tombstone_are_append_only` 使用DISPUTED→INVALIDATED成功，属于冻结合同冲突。按原repair program更正：DISPUTED分支用合法RETRACTED结尾，另测VERIFIED→INVALIDATED，并添加DISPUTED→INVALIDATED拒绝与无残留反例；保留原children、history、correction等断言。不能保留错误成功期望、删除整个测试或弱化为任意错误。

保留R1C-01 VERIFIED-only/latest-first及source RETRACTED保护、R1A/R1B精确版本/children、事务/幂等既有行为。完整hash/replay/UNKNOWN_OUTCOME/concurrency属于R1D，不在本任务改造。

不修改errors、models/repositories/schema/migrations、旧报告/冻结合同/verifier、API/UI/worker等；不commit/merge/rebase/reset/checkout/push。trusted registry、initial import资格、ordinary/trusted correction完整规则及更广泛grade/freshness资格是后续剩余项，不能新增任意trusted实现。

### Required Verification

从候选运行，正常权限机制，既有127.0.0.1:15432 disposable fixture；TG_TEST_ADMIN_DATABASE_URL不得重定向外部/共享/生产。临时库创建、库内迁移和精确teardown是测试步骤，不授权任意SQL、业务库migration或broad cleanup。

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_services.py -k "r1c or current_valid or lifecycle or state_transition" -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1c_01_independent_20260915.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_r1_wiring_20260915.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_reverify.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1a_verifier.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_persistence.py tests/test_migrations.py tests/test_evidence_migrations.py tests/test_research_api.py tests/test_research_persistence.py -rs
ruff check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
ruff format --check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
MYPYPATH=. mypy --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1c-02-mypy backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
PYTHONPYCACHEPREFIX=/tmp/tg-r1c-02-pycache python -m compileall -q backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
alembic -c migrations/alembic.ini heads
git diff --check
git status --short --branch --untracked-files=all
git rev-parse HEAD HEAD^
shasum -a 256 backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py /tmp/test_wp04_02_r1b_r1_wiring_20260915.py /tmp/test_wp04_02_r1b_reverify.py /tmp/test_wp04_02_r1a_verifier.py /tmp/test_wp04_02_r1c_01_independent_20260915.py
```

独立R1C-01 verifier正常运行，TG_R1C_REPLAY_BASELINE必须未设置；不运行该诊断RED开关来验收本任务。focused命名需实际选中全部新关键节点；报告selected/deselected与命令exit，保留000000000004 head。

### Stop Conditions / Expected Evidence

基线/hash/status不符、权限拒绝、fixture setup/cleanup异常、无法取得真实RED/意外全绿、需要越界或修改合同/verifier时BLOCKED；已知临时库残留需精确报告，不广泛清理。

报告IMPLEMENTATION_COMPLETE或BLOCKED，提供完整状态/decision矩阵、audit映射、RED/GREEN、无残留与immutable-history证据、全部命令结果、before/final HEAD/status/SHA、本任务增量与已有R1C-01变更区分。不能把expected RED当环境错误或未跑检查称通过。

## B. Governance Appendix

使用systematic-debugging、test-driven-development、verification-before-completion；遵守ai-task-governor core invariants/anti-drift/acceptance levels/evidence-based acceptance。不得改AC/验证标准或自我宣布PASS。

本任务通过只关闭四个status命令矩阵；trusted/correction/import完整资格、R1D和原TASK-WP04-02-REVERIFY仍需完成，API/Research typed refs尚未解锁。Sector Crowding、Capability Runtime保持延后。
