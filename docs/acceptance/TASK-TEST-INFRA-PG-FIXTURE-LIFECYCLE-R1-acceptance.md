# TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1 — Feedback acceptance

Date: 2026-09-16 / Asia/Shanghai
Role: independent feedback reviewer and task dispatcher
Overall: BLOCKED — final-byte independent runtime verification and successor baseline authorization remain required

## 1. Verdict and evidence boundary

The executor's preservation stop was correct under its original contract. This review does not convert that stop into a business failure, restore unrelated files, recreate a historical dirty state, or retroactively authorize subsequent commits.

The implementation and saved bounded evidence are coherent. Static review found no established blocking semantic defect requiring a repair dispatch now. However, the four real PostgreSQL scenarios ran before the final CREATE-outcome classification and exception-preservation changes. Their results cannot be attributed to all final code bytes. No fresh pytest, PostgreSQL, SQL, migration, container, or Git mutation was executed in this review.

Original 05C-01 remains BLOCKED. Fixture acceptance, 05C-01 business acceptance, 05C-02, R1D, and full WP04-02 acceptance are separate boundaries.

## 2. Independently observed current baseline

| Repository | Branch | HEAD | Parent | Initial working tree/index |
| --- | --- | --- | --- | --- |
| Main | main | 0dc2c5fd016af63f4836debf6ffa9d36b41a7703 | d3acc1c6f4a2e5ce1fe4b973d7855409c0db1da5 | clean/empty |
| Candidate | codex/wp04-02-evidence-domain-service | e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4 | af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8 | clean/empty |

These are later commits than the executor's stopped snapshot. Candidate HEAD contains only the three authorized fixture-related files. The reviewed test_evidence_services.py commit diff changes necessary imports and pg_sessionmaker/request wiring, not domain commands or business assertions. Main HEAD incorporates the previously observed AGENTS routing additions and documentation/evidence. Current AGENTS changes are coding-agent routing additions, not changes to frozen financial rules. Commit actors and authorization were not inferred from commit existence.

Current file SHA-256:

| File | SHA-256 |
| --- | --- |
| backend/evidence/errors.py | 3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec |
| backend/evidence/services.py | 7ce76b02928019347625048e7d0acb523d74168cd6bbbdf03184163ac277f959 |
| tests/test_evidence_services.py | c54e2306b7ec9625f0498faeebd8a23ceb55c6366769ac0d944f228e2aa84851 |
| tests/evidence_pg_fixture.py | bb84518f354f2f7752881fb529dcd6df31b58085bf32d6728c2ccf6998c3e9db |
| tests/test_evidence_pg_fixture_lifecycle.py | 3887a89945a770ed22bac5839ff6a61e5daf47cb05a8b0105d1cfce8f3c12fc7 |

Creating this acceptance file introduces one authorized untracked document in main; it does not move either branch.

Final preservation check observed additional external main changes during this review: tracked AGENTS.md and docs/ZCODE_CAPABILITY_EVALUATION_2026-09-16.md, plus untracked docs/prompts/ZCODE_CAPABILITY_REPAIR_R1_2026-09-16.md. Read-only diff inspection shows benchmark evaluation/routing updates; real PostgreSQL/failure-path execution and final independent acceptance still route to Codex. These do not change the reviewed candidate, financial policy or fixture evidence. They are recorded as NON_BLOCKING_EXTERNAL_CHANGE for this feedback review, preserved, and not attributed to an actor. Both fixed HEAD/parent pairs remain unchanged and candidate stays clean. The main initial clean observation is not a final clean claim.

## 3. Evidence matrix

| Acceptance concern | Reviewed evidence | Decision |
| --- | --- | --- |
| Scope and current identity | Read-only git status/rev-parse/show; candidate commit scoped to three files | Current identity established; successor must explicitly adopt it |
| Fixture lifecycle design | Complete helper and dedicated test source review; CREATE covered by finalization; exact name/OID/owner checks; no forced DROP/connection termination; ambiguity retained | Static support, not a proof of all runtime failure paths |
| Deterministic RED/GREEN | Saved original fake migration-failure RED; final 32 passed / 4 deselected | Saved executor evidence supported, not independently rerun here |
| Real bounded scenarios | Ledger has four create_sent, four created, four dropped, zero cleanup_failed; created/dropped identity tuples match; eight catalog database arrays match | Supports the recorded earlier-byte run and bounded release |
| Final-byte real validation | Manifest distinguishes real-run hashes from final hashes | Missing; cannot declare fixture PASS |
| Artifact integrity | Manifest SHA-256 236a67b8adbeb1b6f408b8bfb6318ca1330134e83754f8cf0ea0363840a7a4ab; three indexed final artifacts size/hash match; final code hashes match | Consistent saved evidence |
| Existing file protection | Rechecked manifest baseline maps: main 388/389 unchanged (AGENTS routing changed); candidate 183/184 unchanged (authorized fixture wiring changed) | Matches disclosed scope, no inferred provenance |
| Historical databases | Saved catalog and ledger support preservation of 45 UNKNOWN targets | No deletion authorization; no current DB observation claimed |

Current review achieved repository/source/artifact inspection. Executor static and runtime results remain qualified saved evidence. Required independent final-byte fixture validation is not yet achieved. Scope drift alone is not proof of faulty candidate code.

## 4. Next task decision

Recommended successor: TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1-INDEPENDENT-REVERIFY.

Executor: Codex, following current main AGENTS routing for database/failure-path work. No zcode delegation. User dispatch of the explicit successor prompt is needed to adopt the current baseline and approve a new separate maximum-four-database verification budget. The exhausted original four-database budget is not reset or reused.

The successor is verification-only. It may write its own report, raw logs and new ledger, but may not change candidate code, fixtures, historical evidence or Git history. A discovered semantic failure gets FAIL and a narrow repair recommendation; there is no inline repair during verification. No full business suite is included in this bounded task.

After fixture PASS, next priority is independently reverify the original 05C-01 business boundary using the accepted fixture and an explicitly sized run budget. Do not enter 05C-02/R1D before 05C-01 PASS. UNKNOWN databases need not be deleted merely to conduct a bounded run that preserves them; environmental inability to create/release exactly owned resources would be a separate blocker.

## 5. Proposed complete successor prompt (not dispatched by this report)

```text
你正在维护 ThesisGuard（论衡）。

执行 TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1-INDEPENDENT-REVERIFY。
身份：独立验证者；本任务不是修复实现、完整业务验收或 Git 集成。
执行者为 Codex。按当前主仓 AGENTS.md 的 DB/故障路径路由，不派发 zcode。

授权：本次派发明确采用以下当前提交作为新的复验基线，并批准本任务在既有
127.0.0.1:15432 实例中新建最多四个 disposable 数据库、执行既有 fixture 所需的
迁移及测试、仅按精确资源归属释放本次新建数据库。此为独立的新预算，不重置或复用
原 R1 已耗尽的四库预算；不追认既有 Git 操作，不授权清理历史 45 个 UNKNOWN 库。
本授权仍须通过产品正常权限机制；审批拒绝时不得绕行。

仓库：
main: /Users/qianduoduo/Desktop/AI_app/ThesisGuard
candidate: /Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service

固定基线：
main branch main
HEAD 0dc2c5fd016af63f4836debf6ffa9d36b41a7703
parent d3acc1c6f4a2e5ce1fe4b973d7855409c0db1da5
candidate branch codex/wp04-02-evidence-domain-service
HEAD e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4
parent af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8
candidate 工作区 clean，index empty。
main 允许本轮反馈验收文件未跟踪；其他既有状态逐项记录，不恢复或提交。
本轮已观察到 AGENTS.md、docs/ZCODE_CAPABILITY_EVALUATION_2026-09-16.md 的 benchmark/routing
修改及 docs/prompts/ZCODE_CAPABILITY_REPAIR_R1_2026-09-16.md 未跟踪；只读核验其仍不改变
DB 执行/独立验收路由、冻结政策或本任务证据后，作为既有外部状态保留。

固定候选 SHA-256：
backend/evidence/errors.py
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec
backend/evidence/services.py
7ce76b02928019347625048e7d0acb523d74168cd6bbbdf03184163ac277f959
tests/test_evidence_services.py
c54e2306b7ec9625f0498faeebd8a23ceb55c6366769ac0d944f228e2aa84851
tests/evidence_pg_fixture.py
bb84518f354f2f7752881fb529dcd6df31b58085bf32d6728c2ccf6998c3e9db
tests/test_evidence_pg_fixture_lifecycle.py
3887a89945a770ed22bac5839ff6a61e5daf47cb05a8b0105d1cfce8f3c12fc7

先完整阅读：
主仓 AGENTS.md；原 TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1 的任务合同；
docs/acceptance/TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1-execution-report.md；
docs/acceptance/TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1-acceptance.md；
原 evidence/manifest.json、resources.jsonl、execution.log；
候选 helper、专门 lifecycle tests 和 pg_sessionmaker 接线；
既有 Phase A exact-cleanup-plan.json（取得精确 45 UNKNOWN 名称/OID/owner）。
本文仅替代旧任务固定身份、用尽预算和机械的主仓全 scope 停止门槛，其余安全约束保留。
不得修改旧合同或将新基线冒充旧任务的原始基线。

目标：在最终固定字节上取得独立、新鲜、有界的 fixture 生命周期验证。
仅允许新建：
docs/acceptance/TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1-INDEPENDENT-REVERIFY-acceptance.md
docs/acceptance/TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1-INDEPENDENT-REVERIFY-evidence/ 下本轮产物。
新 evidence 目录、ledger、run_id 必须独立且不覆盖已有文件；若已有同名运行产物，停止确认，
不得清空旧 ledger 来重复获得预算。缓存仅放独立 /tmp 目录。
禁止改候选任何文件、旧 tests/fixtures、verifier、历史报告、冻结合同、模型、迁移、API、业务服务。
禁止 commit/merge/rebase/reset/checkout/push、安装或升级依赖、替代 DB/代理/Docker 实例、
换 host/port、终止其他连接、DROP FORCE、模糊匹配删除、广泛清理及逐库连接 UNKNOWN。

步骤：
1. 只读核验 branch/HEAD/parent/scope/五文件哈希及旧证据 hash。
   入口身份或候选哈希不匹配则 BLOCKED，不自动采用再漂移的基线。
2. 核验环境及子进程工具发现，复用原成功环境：
   PATH=/opt/miniconda3/bin:/opt/homebrew/bin:/opt/homebrew/opt/postgresql@16/bin:/usr/bin:/bin:/usr/sbin:/sbin
   PYTHONDONTWRITEBYTECODE=1
   PYTHONPATH=<candidate>:/opt/homebrew/lib/python3.12/site-packages
   pytest 显式 /opt/homebrew/bin/pytest；Python 显式 /opt/homebrew/bin/python3.12。
   检查 TG_TEST_ADMIN_DATABASE_URL、TG_R1C_REPLAY_BASELINE、TG_R1C02_REPLAY_PRIOR 原本未设置，
   如已设置则停止，不静默清除。解析到 Alembic 的绝对路径并确认单 head 000000000004。
   使用既有本地配置，不将密码写入报告。ledger 使用本轮绝对路径，run_id 唯一。
3. 不开真实 DB，先新鲜运行专门 lifecycle tests 的确定性节点：
   /opt/homebrew/bin/pytest -p no:cacheprovider -q tests/test_evidence_pg_fixture_lifecycle.py -k 'not real' -rs
   预期 32 passed、4 deselected、零 skip。独立审查 CREATE 已确认后各阶段失败、
   CREATE 不确定、identity mismatch/active sessions、ledger 写失败、原异常保留及精确 teardown。
   如需 verifier-owned 补充反例，只在本轮 evidence 下建确定性验证器，不改生产/候选文件，
   不额外访问 DB。不要求制造新的业务 RED。
4. 确定性检查通过后，经正常审批，在最终哈希上仅运行一次四个真实节点：
   TG_RUN_PG_FIXTURE_LIFECYCLE_REAL=1
   /opt/homebrew/bin/pytest -p no:cacheprovider -q tests/test_evidence_pg_fixture_lifecycle.py -k real -rs
   同时明确传入 TG_EVIDENCE_PG_LEDGER=<本轮全新绝对 ledger 路径> 和 TG_EVIDENCE_PG_RUN_ID。
   按原测试前置建立本轮空 ledger（新文件，不覆盖）；全程总 CREATE 尝试最多四次。
   覆盖 normal / migration fault / engine fault / body fault。
   每次记录精确 run/node/name/OID/owner、归属确认、零连接、DROP 和 ABSENT。
   四次之前/之后 admin catalog 比较，历史 45 UNKNOWN 名称/OID/owner 不变。
   任一归属不确定、cleanup failure、预算耗尽、权限阻塞时停止后续创建，不自动补跑。
   只有身份明确、仅本任务所有的资源可按既有 fixture 精确释放；保留并报告其他不确定资源。
5. 对三个 fixture 文件新鲜执行 Ruff、format-check、mypy、compileall；缓存放 /tmp。
   核对最终五哈希、候选工作区/index、两仓身份、旧报告/ledger/verifier 保全。
   不运行 full Evidence service、七份业务 verifier 或 Research 回归：本任务只关闭 fixture 边界。

漂移处理：候选代码/身份、冻结政策、当前任务授权依据、运行环境或受保护历史证据变化，
或影响无法判断时 BLOCKED。主仓单纯新增无关文档/未跟踪文件或 docs-only 提交，不机械判定
业务 FAIL：先只读审查其是否影响本任务依据，明确无影响则记录 NON_BLOCKING_EXTERNAL_CHANGE，
保留并继续；如影响则停止。不覆盖、撤销或归因他人变更。

证据只保留必要的前后快照、原始 stdout/stderr、实际 argv/cwd/脱敏环境/时间/退出码、
资源 ledger、单一命令与产物 SHA manifest、正式独立验收报告；不为每条断言新建治理文档。
结果输出 PASS / FAIL / BLOCKED。PASS 要求最终固定字节的确定性、四真实场景和静态检查
全通过且无 skip、setup/teardown/cleanup failure，四库预算及历史资源保全得到证明。
如真实错误来自注入，应明确区分预期故障与未预期测试错误。

最终解释原四库结果与本轮新四库结果的版本和预算区别。
仅可关闭 fixture 验证；不得宣布 05C-01、R1C、WP04-02 完成，不授权 Git integration。
若 fixture PASS，建议下一任务为 05C-01 独立业务复验，另列其预算与 fixture ledger 前置；
不得直接进入 05C-02/R1D。若 FAIL，只报告最小反例和窄修复边界，不当场改代码。
```

## 6. Review actions

This review used ai-task-governor for evidence/boundary acceptance and ai-task-prompt-architect for a single bounded successor. Relevant instructions were read before task actions. Read-only git and source/JSON/hash inspections were performed. No subagent, external write, database operation or test run was performed. Only this acceptance document was added; no history was committed or pushed.
