# TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R2

## A. Execution Core

- Target: **Codex**，角色为独立业务验证者；本轮不修业务代码。
- Objective: 在已独立接受的 fixture 上，对现有 05C-01 correction admission 的 41 个 focused 场景获得新鲜 PostgreSQL 证据。
- Why now: fixture lifecycle 已独立 PASS；05C-01 旧验收仍 BLOCKED，不能提前进入 05C-02、API 或 Git 集成。
- Task type/size: DB_PERSISTENCE_VERIFICATION / SMALL，一个 focused 业务验证边界。
- Required acceptance: L1_STATIC_REVIEWED、L3_CONTRACT_VERIFIED、L4_DB_VERIFIED；Full evidence matrix。
- Dispatch boundary: 用户转发本提示词派发时，授权本轮使用下列新基线、保留历史 UNKNOWN、创建/正常精确释放最多 41 个全新 disposable fixture DB。不授权旧库清理或其他业务操作。本次生成提示词尚未执行数据库测试。

### Read and Baseline

主仓：`/Users/qianduoduo/Desktop/AI_app/ThesisGuard`，main HEAD `0dc2c5fd016af63f4836debf6ffa9d36b41a7703`。
候选：`/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`，branch `codex/wp04-02-evidence-domain-service`，HEAD `e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4`，parent `af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8`，要求 candidate clean/index empty。

先读双方 AGENTS.md，并读以下必要事实源：

- `docs/acceptance/TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1-INDEPENDENT-REVERIFY-acceptance.md` 及其 manifest/ledger。只采用这份报告限 fixture 的最终固定字节验收，不追认旧 BLOCKED 报告或复用旧四次 CREATE 预算。
- 原 `TASK-WP04-02-R1C-05C-01-task-contract.md`、dispatch、acceptance、execution-report；冻结 Evidence contract 与 `docs/WP04_EVIDENCE_CORRECTION_POLICY_ADDENDUM_2026-09-16.md` 的相关准入/replay条款。
- candidate `tests/evidence_pg_fixture.py`、`pg_sessionmaker/db` 接线、四个 focused 测试及调用的相关服务/快照 helper；不要仅依赖旧自报 PASS。
- 历史精确名单 `docs/acceptance/TASK-WP04-02-R1C-05C-01-INDEPENDENT-REVERIFY-R1-evidence/phase-a-20260916-exact-cleanup-plan.json`，保留其中 45 UNKNOWN，不逐库连接/终止/改名/删除。

核验固定 SHA256：

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec backend/evidence/errors.py
7ce76b02928019347625048e7d0acb523d74168cd6bbbdf03184163ac277f959 backend/evidence/services.py
c54e2306b7ec9625f0498faeebd8a23ceb55c6366769ac0d944f228e2aa84851 tests/test_evidence_services.py
bb84518f354f2f7752881fb529dcd6df31b58085bf32d6728c2ccf6998c3e9db tests/evidence_pg_fixture.py
3887a89945a770ed22bac5839ff6a61e5daf47cb05a8b0105d1cfce8f3c12fc7 tests/test_evidence_pg_fixture_lifecycle.py
```

主仓已有 AGENTS/zcode评估修改和未跟踪验收材料逐项记录并保留；只读分类与当前测试/金融规则无关的外部变化为 NON_BLOCKING_EXTERNAL_CHANGE，不恢复、不提交。涉及候选字节、fixture、规则或调用路由的漂移不能静默重定基线。

### Top Blocking AC

1. 两仓身份、candidate clean、五哈希及相关规则匹配；本轮不改 source/tests/fixtures/contracts/旧证据/Git，保留主仓入口状态。
2. 创建前验证实际父/子工具环境、target、单 Alembic head；用全新唯一 run_id 和全新空 ledger，最多 41 次 create_sent，单次 focused invocation，禁止业务测试补跑/追加 CREATE。
3. 四个节点合计 41 测试在真实 PostgreSQL 上无 skip/xfailed/setup/teardown error：20 forbidden、16 allowed、3 ordinary COMMITTED replay、2 disclosed legacy COMMITTED replay；断言保持原样。
4. commit/fresh-session 九表全列一致性、拒绝不遗留内外幂等 key/历史、合法 replacement routing/child/audit、历史 replay 只读和新写准入分别取得实际证据。既有历史 seed 不证明新写允许。
5. 本轮每个新资源有归属与释放证据，精确 name/OID/owner/owner_oid、零残留连接、正常 DROP 后 ABSENT；前后 admin catalog 完整 identity array 相同，45 UNKNOWN 保留；产物可复现且范围不变。

### Scope and Required Verification

采用 fixture 已成功的 command-local 环境，不改 shell profile或共享环境：

```text
PATH=/opt/miniconda3/bin:/opt/homebrew/bin:/opt/homebrew/opt/postgresql@16/bin:/usr/bin:/bin:/usr/sbin:/sbin
PYTHONDONTWRITEBYTECODE=1
PYTHONPATH=<candidate>:/opt/homebrew/lib/python3.12/site-packages
Python=/opt/homebrew/bin/python3.12
pytest=/opt/homebrew/bin/pytest
Alembic=/opt/miniconda3/bin/alembic
```

先核验该环境存在并按原成功记录确认实际 interpreter/pytest、child shutil.which('alembic')、`alembic -c migrations/alembic.ini heads` 单 head `000000000004`。检查 `TG_TEST_ADMIN_DATABASE_URL / TG_R1C_REPLAY_BASELINE / TG_R1C02_REPLAY_PRIOR` 未设置，不静默清除；其他诊断变量也检查与当前四测试是否相关。

测试 cwd 固定为 candidate，只采用已核验本地 `postgresql+asyncpg` admin `127.0.0.1:15432/postgres` 既有配置；不泄露 password/URL。只允许 admin 元数据和本轮新 disposable DB 的测试写入；迁移仅由现有 fixture 对新资源执行 upgrade head，不执行共享库 migrate/db-reset。用新唯一 evidence 目录内全新空绝对 JSONL ledger 设置 `TG_EVIDENCE_PG_LEDGER` 及 `TG_EVIDENCE_PG_RUN_ID`。不复用、覆盖或清空旧 ledger。

先确认模块加载无额外 DB 副作用，再用下面四个精确节点 collect-only，必须正好 41；collect 阶段没有 CREATE。保存收集清单，然后仅一次真实运行，禁用 cacheprovider，使用 `-x -vv -s --tb=short`：

```text
tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue
tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit
tests/test_evidence_services.py::test_r1c05c01_committed_exact_replay_read_only
tests/test_evidence_services.py::test_r1c05c01_legacy_forbidden_prior_committed_replay
```

预算按 create_sent 的所有尝试计，不按成功 DB 数计。每个 param 节点共享函数域的 db/pg_sessionmaker，最多一个新 DB；若收集/fixture行为导致超过预算则在创建前停，不改 fixture 来绕预算。真实运行首个未预期 assertion/setup/teardown/cleanup错误即停止后续节点，保留原错误与已创建精确资源状态，不重跑。

不重复已验收的四个真实 fixture 场景；不跑 full service、七份业务 verifier、Research/persistence/migration 回归。这是**原完整 05C-01 验收矩阵的第一片新鲜证据**，不是删减/替代原 AC5；剩余完整矩阵保持待验证，本轮 focused PASS 不能关闭 05C-01/R1C/WP04-02 或进入 05C-02。历史测试前缀字节变化仅采用已接受 fixture接线，旧断言/verifier不得改变。

### Stop Conditions and High-Risk Examples

- 旧 COMMITTED replay 可以只读返回原结果，但不能让同样 forbidden prior 的新 key 通过；必须独立覆盖两类路径。
- 拒绝时调用者仍 commit：fresh session九表全列要与之前完全相同，不能只比较行数或 db.new。
- parent 能找到 Alembic、child 找不到：禁止 CREATE；检查真正测试子进程环境，不换壳假验。
- CREATE ack/身份/清理归属不确定，或 target出现其他连接：fixture fail closed，不 FORCE/pg_terminate_backend/前缀批量删除；报告精确名单与 UNKNOWN。
- 缺少目标服务/工具/凭据、identity/hash漂移、候选 dirty、收集不是41、环境诊断变量污染、需要改合同/断言或超预算：停止并给 BLOCKED；业务断言失败记录 FAIL，不能误报环境 BLOCKED或现场修业务代码。

### Evidence and Final Response

只新增主仓 `docs/acceptance/TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R2-acceptance.md` 及同 ID `-evidence/` 中必要 before.json、after.json、execution.log、resources.jsonl、manifest.json；路径已存在则不覆盖。缓存/验证辅助代码用新的 `/private/tmp/` 目录；manifest 保存辅助源码及关键哈希，原始工具输出脱敏。

保存实际 argv/cwd/局部脱敏环境、UTC起止/exit、收集节点、五哈希/前后 scope/catalog、每个场景与资源ledger映射；Full matrix映射五AC及 Required/Achieved/Missing acceptance。不要用旧自报 PASS 代替这次证据。

最终作为**独立 verifier**输出 PASS / FAIL / BLOCKED，仅限本 focused task，并列实际测试结果、尝试预算使用、新资源全部释放或剩余 UNKNOWN、证据路径、仍待验证的原 full matrix。如果业务 FAIL，只建议一个后续最小 Repair，不在本 verifier task 实现。

## B. Governance Appendix

使用 ai-task-governor 的 core invariants / anti-drift / evidence-based acceptance：保持未变实现独立验证，Blocking AC失败即任务 FAIL，不自批业务改动。这里 Codex 是未参与该业务实现的验证者；不是业务 executor 自验后自批。

标准延后：05C-02/R1D、整个 WP04-02关闭、Git集成、Evidence API、Research/Thesis/Agent、Capability Runtime、Sector Crowding、新产品/金融规则及历史库清理均不在本任务授权范围。
