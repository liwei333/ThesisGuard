# TASK-WP04-02-R1C-01 — Dispatch Prompt

Status: `READY_FOR_USER_DISPATCH`。这是 dispatcher 的明确执行提示词，沿用既有 R1C-01 目标和验证矩阵，不改冻结合同或既有验收记录；读取文件不等于用户已派发业务或授予工具权限。

## A. Execution Core

你正在维护 ThesisGuard，执行 `TASK-WP04-02-R1C-01`。角色为 EXECUTOR，只修 latest-first lifecycle eligibility。

- Why Now: R1B-R2 的独立历史 PASS 已保留，bdd70ed 基线交接已通过独立文档复核；当前 current-valid 仍错误允许 UNREVIEWED/PENDING_REVIEW/DISPUTED。
- Type / Size: REPAIR / SMALL，单一读取资格边界。
- Required Acceptance: L1_STATIC_REVIEWED、L2_BUILD_VERIFIED、L3_CONTRACT_VERIFIED、L4_DB_VERIFIED；Full Evidence Matrix。
- 主仓：`/Users/qianduoduo/Desktop/AI_app/ThesisGuard`。
- 候选：`/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`。
- 分支：`codex/wp04-02-evidence-domain-service`。
- 起始 HEAD：`bdd70edc153b6ed5def65ed99c41f325df45f066`。
- parent：`f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`；候选必须 clean。

### Required Reading / Preflight

主仓文档必须从主仓读取，不假设它们已存在于候选 worktree：完整阅读 AGENTS.md、本提示词、`docs/acceptance/TASK-WP04-02-R1C-01-task-contract.md`、baseline-confirm 合同及来源/独立复核报告、R1B-R2 独立 PASS、原 R1 repair program、冻结 `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md` relevant current/lifecycle/correction 章节及例23–26/41。检查候选 services、repositories 的 current/exact/history 实现、tests、fixtures、测试配置。

业务修改只允许：

- `backend/evidence/services.py`
- `tests/test_evidence_services.py`

errors.py 保持原字节；三业务文件和三个 /tmp verifier 起始哈希必须匹配既有 R1C-01 合同。核对真实 branch/HEAD/parent/status/hash 任一不符则 BLOCKED，不重新确认已通过的基线，也不静默更换基线。

### Top Blocking AC

1. current-valid 先取得最高 version；生命周期维度仅最新 VERIFIED 可以通过，并保留当前 exact source version RETRACTED 排除检查。其他六状态返回 None；缺失 series 仍 None；不能 fallback 旧 VERIFIED。
2. 普通 same-series correction 与 ordinary identity-changing replacement 的最新 UNREVIEWED 不继承 prior exact VERIFIED 的资格；exact 历史查询和 history listing 仍能读取旧版本。
3. 修改 services 前，在真实 PostgreSQL fixture 中取得业务断言 RED，证明未修基线错误允许 UNREVIEWED/PENDING_REVIEW/DISPUTED；权限错误、setup error、Mock 或改 verifier 不算 RED。
4. 最小修复后新增反例、原 R1A/R1B/wiring verifier、完整 service/regression/static 矩阵通过；保护 immutable children、合法历史支持 replacement、invalid-input no-residue 和 caller-owned transaction。
5. 最终只留下授权两文件业务修改；errors/verifiers/冻结合同/schema/migrations/Git HEAD 不变。提供 AC 对应位置、red/green 命令结果、before/final 状态与哈希，不能自行宣布 PASS。

### Must / Execution Strategy

先加测试，取得 RED，再修改服务代码，取得 GREEN。不要 reset/checkout/revert 已提交基线来制造 RED。

七生命周期状态都要覆盖：VERIFIED 正例；UNREVIEWED、PENDING_REVIEW、DISPUTED、REJECTED、INVALIDATED、RETRACTED 反例。包括 prior VERIFIED + latest 不合格时不回退、ordinary correction、replacement、missing series、exact/history，以及最新 VERIFIED 但 exact source version RETRACTED 的既有保护。

优先使用现有公开命令构造合法状态；若后续状态表缺陷使状态不可表达，只在已有真实 PostgreSQL fixture 内通过 ORM 追加完整且约束合法的不可变测试行，并列明该构造只验证读取资格，不验证生命周期写命令正确性。禁止修改生产 lifecycle 写命令、修改历史行或调整数据库约束来迁就测试；无法合法构造则 BLOCKED。

对 `test_create_source_backed_evidence_persists_children_queries_and_audit` 中初始 UNREVIEWED 的 current-valid 非空断言，按冻结合同改为 None；保留其 exact/current、children、links、audit 等原断言，另增加合法 VERIFIED current-valid 正例。逐项说明更正依据，不删除/skip/xfail/弱化原测试，不把全局 fixture 默认改成 VERIFIED 来隐藏问题。

修复仅完成生命周期维度，不等于所有 source grade/F restriction、freshness、角色 eligibility、trusted 来源资格均已完成；禁止扩大本切片或宣布整个 R1C/WP04-02 完成。

### Required Verification

从候选执行，使用项目既有 Python/pytest/ruff/mypy 环境。原 R1C-01 合同 H 中完整命令矩阵必须全部执行；不可只引用历史 PASS：

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_services.py -k "r1c or current_valid or lifecycle" -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_r1_wiring_20260915.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_reverify.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1a_verifier.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_persistence.py tests/test_migrations.py tests/test_evidence_migrations.py tests/test_research_api.py tests/test_research_persistence.py -rs
ruff check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
ruff format --check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
MYPYPATH=. mypy --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1c-01-mypy backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
PYTHONPYCACHEPREFIX=/tmp/tg-r1c-01-pycache python -m compileall -q backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
alembic -c migrations/alembic.ini heads
git diff --check
git status --short --branch --untracked-files=all
git rev-parse HEAD HEAD^
shasum -a 256 backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py /tmp/test_wp04_02_r1b_r1_wiring_20260915.py /tmp/test_wp04_02_r1b_reverify.py /tmp/test_wp04_02_r1a_verifier.py
```

focused RED/GREEN 测试命名必须确保被上述 selector 选中，报告实际节点及 deselected 数；若关键测试未被 selector 选中，另明确运行其节点，不得把零节点或旧测试结果当覆盖。不是要求所有新增测试在 baseline 都失败，要求至少真实触达已知缺陷的断言失败。

数据库仅使用既有本地 `127.0.0.1:15432` disposable fixture 路线，确认 TG_TEST_ADMIN_DATABASE_URL 未重定向外部/共享/生产实例；权限必须走正常机制。既有 fixture 的临时库创建、库内迁移和该精确临时库 teardown 是测试步骤，不授权任意 SQL、业务数据库迁移或 broad cleanup。已知残留必须报告准确库名，不能自行广泛清理。

Alembic head 必须保持 `000000000004`。对长命令使用可恢复运行会话，并保持进度沟通，不能绕行审批。

### Must Not / Stop Conditions

不修改 source/verifier/contract/migration/model/repository/schema/API/docs；本业务任务不改主仓现有治理文件；不 commit、merge、rebase、reset、checkout、push。依赖升级、全局 fixture 改造、状态转换表、trusted registry、R1D、API/Research typed refs、Agent/Capability/Sector Crowding 都不在范围内。

基线不符、权限拒绝、DB setup/cleanup 异常、无法取得真实 RED、意外全绿、需要修改禁止文件或越界实现时，停止并输出 BLOCKED 及具体证据。服务缺陷造成预期 RED 是修复输入，不等于环境阻断。通过原矩阵需要越界时不得修改合同降低标准。

### Final Deliverables

只能报告 IMPLEMENTATION_COMPLETE 或 BLOCKED。报告 preflight、真实 RED、最终 GREEN、完整命令与 exit/result、AC->实现/测试节点、exact/history 与不回退证据、最终两文件 diff 和 SHA、errors/verifier 不变、HEAD 不变及临时库异常/残留已知情况。不能声明未运行的检查通过或未扫描全实例却声称无任何残留。

## B. Governance Appendix

使用 systematic-debugging、test-driven-development、verification-before-completion；需要任务治理时遵守 ai-task-governor 的 core invariants、anti-drift、acceptance levels 和 evidence-based acceptance。不得改变 AC/验证矩阵或自我验收。

本任务完成后等待独立验收。R1C 后续状态表、trusted deterministic correction registry、R1D 和 TASK-WP04-02-REVERIFY 仍待完成；WP04-03/04、Sector Crowding与 Capability Runtime 不自动解锁。
