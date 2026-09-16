# TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1-INDEPENDENT-REVERIFY — 独立验收

日期：2026-09-16 / Asia/Shanghai。身份：独立验证者；执行工具：Codex。结论：**PASS，仅关闭 PostgreSQL fixture 生命周期独立验证边界。**

本轮依据原 R1 feedback acceptance 第 5 节完整 successor prompt 和用户本次明确派发执行。采用新固定基线及独立四次 CREATE 尝试预算，不追认历史 Git 操作，不替代原 R1 报告，不扩大至业务验收或 Git 集成。未修改候选代码、断言、旧 verifier、冻结合同、模型、迁移或历史证据，未安装依赖或修改 shell profile。

## 1. 基线、输入及 scope

| 仓库 | 分支 | HEAD | Parent | 本轮最终状态 |
| --- | --- | --- | --- | --- |
| 主仓 | main | 0dc2c5fd016af63f4836debf6ffa9d36b41a7703 | d3acc1c6f4a2e5ce1fe4b973d7855409c0db1da5 | 保留既有外部状态及本轮允许产物；index empty |
| 候选 | codex/wp04-02-evidence-domain-service | e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4 | af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8 | clean；index empty |

主仓：`/Users/qianduoduo/Desktop/AI_app/ThesisGuard`。候选：`/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`。入口及最终 branch/HEAD/parent 均匹配用户授权，不自动重定基线，没有 Git 修改。

完整阅读主仓 AGENTS.md、原任务合同附件、原执行报告、feedback acceptance/successor prompt、候选 helper/专门 lifecycle tests/pg_sessionmaker 接线；读取并解析原 manifest、ledger、execution.log 及 Phase A 精确名单。原 manifest 已登记产物的大小/哈希及 29 个原命令记录得到核验。旧结果只作为带版本限定的保存证据。

原合同附件：`/Users/qianduoduo/.codex/attachments/a3c3abcd-a72e-4837-bed6-c2dff1ce4310/pasted-text.txt`，SHA-256 `a3c72d8ab7b8145edaa4e89eb0ab94fede31dc5407144cf83b749d30532f53bc`。当前授权输入与旧合同的替代范围严格限于 successor 指定身份、独立新预算和主仓无关变化分类门槛。

| 候选五个固定文件 | 本轮前后 SHA-256 |
| --- | --- |
| backend/evidence/errors.py | 3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec |
| backend/evidence/services.py | 7ce76b02928019347625048e7d0acb523d74168cd6bbbdf03184163ac277f959 |
| tests/test_evidence_services.py | c54e2306b7ec9625f0498faeebd8a23ceb55c6366769ac0d944f228e2aa84851 |
| tests/evidence_pg_fixture.py | bb84518f354f2f7752881fb529dcd6df31b58085bf32d6728c2ccf6998c3e9db |
| tests/test_evidence_pg_fixture_lifecycle.py | 3887a89945a770ed22bac5839ff6a61e5daf47cb05a8b0105d1cfce8f3c12fc7 |

主仓入口现有状态逐项保留：

| 路径/状态 | 分类及只读依据 |
| --- | --- |
| AGENTS.md / tracked modified | NON_BLOCKING_EXTERNAL_CHANGE；变更为隔离 zcode benchmark/routing；真实 DB、故障路径及独立验收仍由 Codex 承担，未改变冻结金融政策 |
| docs/ZCODE_CAPABILITY_EVALUATION_2026-09-16.md / tracked modified | NON_BLOCKING_EXTERNAL_CHANGE；隔离 benchmark 评审记录 |
| docs/prompts/ZCODE_CAPABILITY_REPAIR_R1_2026-09-16.md / untracked | NON_BLOCKING_EXTERNAL_CHANGE；仅授权临时隔离 benchmark 修复，明确项目/候选只读、不得 DB 操作 |
| docs/acceptance/ZCODE-CAPABILITY-BENCHMARK-20260916-independent.json / untracked | NON_BLOCKING_EXTERNAL_CHANGE；隔离 benchmark 独立结果，不是本任务 fixture 证据；JSON 已完整解析 |
| docs/acceptance/TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1-acceptance.md / untracked | PRESERVED_AUTHORITY_INPUT；本次 successor 合同，原 BLOCKED 记录保留 |

未推断外部变化的作者或授权来源。上述文件本轮前后哈希相同，不恢复 dirty 状态、不撤销提交、不提交这些变化。

## 2. 有效工具环境及子进程发现

每个实际验证命令在候选 cwd 中使用同一 command-local 环境：

```text
PATH=/opt/miniconda3/bin:/opt/homebrew/bin:/opt/homebrew/opt/postgresql@16/bin:/usr/bin:/bin:/usr/sbin:/sbin
PYTHONDONTWRITEBYTECODE=1
PYTHONPATH=<candidate>:/opt/homebrew/lib/python3.12/site-packages
Python invocation=/opt/homebrew/bin/python3.12
pytest invocation=/opt/homebrew/bin/pytest
Alembic=/opt/miniconda3/bin/alembic
Ruff=/opt/miniconda3/bin/ruff
mypy=/opt/miniconda3/bin/mypy
```

原有 TG_TEST_ADMIN_DATABASE_URL、TG_R1C_REPLAY_BASELINE、TG_R1C02_REPLAY_PRIOR 均未设置；入口及每个验证 runner 调用再次检查，没有静默清除。真实调用仅局部设置本轮 opt-in、run_id、ledger。使用既有本地 admin 配置；报告、原始日志及 manifest 不包含密码或 DATABASE_URL。

| 工具/检查 | 新鲜结果 |
| --- | --- |
| 显式 Python | 3.12.9；sys.executable 实际解析 /opt/homebrew/opt/python@3.12/bin/python3.12 |
| 显式 pytest | /opt/homebrew/bin/pytest，9.1.1；PATH 的 which pytest 为 /opt/miniconda3/bin/pytest，故始终使用合同指定显式入口 |
| Alembic | /opt/miniconda3/bin/alembic，1.18.5 |
| Python 子进程 which Alembic | /opt/miniconda3/bin/alembic，与父检查一致 |
| heads | /opt/miniconda3/bin/alembic -c migrations/alembic.ini heads → 单 head 000000000004 (head) |
| Ruff | 0.16.1 |
| mypy | 2.3.0 |
| psql 客户端版本（无连接） | 显式 /opt/homebrew/opt/postgresql@16/bin/psql，16.13；未将客户端版本当作服务器版本 |

本轮复用了原成功环境，没有换用默认 shell PATH。每个真实场景的 tools_checked 在实际测试子进程环境内再次确认显式 Python/pytest、Alembic 路径/版本、child discovery 和同一个 head；四次均匹配。

验证者自己的两个错误已保留，未当作候选缺陷或隐去：首次环境探针遗漏现有 `-c migrations/alembic.ini`，退出 255；随后按现有 fixture argv 补齐并成功检查 head，再按 A→B 顺序重新运行确定性节点。首次离线 ledger 评估脚本误以为 body 阶段名为 `body`，触发 AssertionError；固定 helper 实际字段为 `test_body`，按源码和原始 ledger 纠正评估字段后全部通过。两者均仅修改 /tmp 验证执行辅助脚本；原始失败命令、stdout/stderr、辅助源码原版及纠正版均存于单一 manifest/log。没有真实测试重跑或额外 CREATE。

## 3. 验证矩阵与新鲜结果

| 层级/验收关注点 | 最终固定字节上的证据 | 结论 |
| --- | --- | --- |
| AC-01 环境/preflight | 工具、child/head/target 失败的确定性零 CREATE；实际环境探针及四真实节点的 tools_checked/target_checked | PASS |
| AC-02 生命周期异常 | migration/engine/sessionmaker/body 确定性异常与原异常保留；真实 migration/engine/body 注入后精确释放 | PASS |
| AC-03 归属/CREATE | durable PRE_ATTEMPT 与 create_sent 先于 CREATE；ack+精确 name/OID/owner/owner_oid 确认；SQLSTATE 连接/停机/不分类结果 UNKNOWN 不 DROP；ledger 失败保留原异常 | PASS |
| AC-04 精确 teardown | 已知身份匹配才允许释放；identity mismatch、active session、dispose/admin close/DROP 失败按确定性测试 fail closed；真实四资源均零连接、exact DROP、ABSENT | PASS |
| AC-05 范围和保全 | 两仓固定身份及五哈希、候选 clean/index empty、前后全文件哈希比较、旧报告/manifest/log/ledger/verifier 保全、历史 45 UNKNOWN 身份保全 | PASS（按 successor 漂移分类） |
| L1_STATIC_REVIEWED | 完整候选 source 与接线只读审查，未发现已建立的阻塞语义缺陷 | PASS，限 fixture |
| L2_BUILD_VERIFIED | 三 fixture 文件新鲜 Ruff、format-check、mypy、compileall 全部 exit 0；缓存仅独立 /tmp | PASS |
| L3_CONTRACT_VERIFIED | 独立确定性节点 32 passed、4 deselected、零 skip | PASS，限专门生命周期合同 |
| L4_DB_VERIFIED | 单次四真实 PostgreSQL 场景 4 passed、32 deselected、零 skip；本轮 ledger 和八份 catalog 对比 | PASS，限有界四场景 |

最终确认的确定性命令时间：2026-09-16T11:49:11.552067+00:00 至 2026-09-16T11:49:14.194856+00:00，pytest 32 passed / 4 deselected，0.36s。此前同字节确定性 run 同样 32 passed / 4 deselected，但首次工具探针尚未补齐，因此复验一次明确恢复 A→B 顺序；两次均不开真实数据库。

唯一真实调用时间：2026-09-16T11:49:35.529139+00:00 至 2026-09-16T11:49:51.875978+00:00，pytest 4 passed / 32 deselected，13.95s。命令带 `-x`，首个未预期测试错误即停止；无追加/补跑。实际 argv/cwd/脱敏局部环境/UTC 时间/退出码/stdout/stderr 见 execution.log 与 manifest。

Ruff：All checks passed；format-check：3 files already formatted；mypy：Success: no issues found in 3 source files；compileall：exit 0，pycache prefix 在独立 /tmp。两类既有依赖 deprecation warnings 及 mypy unused-section note 已保留；没有 skip、未预期 setup/teardown/test error 或 cleanup failure。

## 4. 本轮精确资源与释放证据

run_id：`0348c037ded74f91b992077a49fd9d9c`。独立 ledger：`/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1-INDEPENDENT-REVERIFY-evidence/resources.jsonl`。总预算四次 CREATE 尝试；实际四次 create_sent、四次 created、四次 cleanup_checked、四次 drop_sent、四次 dropped，0 create_failed、0 cleanup_failed、0 ownership uncertainty。本轮预算已耗尽，不意味着允许第五次创建或重新清空 ledger。

每个节点均先通过 admin postgres 确认目标名字 ABSENT，再确认 CREATE ack 和 OID/owner。释放前关闭所拥有的 engine/admin/session，重新从 admin 查询精确身份相符和 pg_stat_activity 计数为 0，仅执行 `DROP DATABASE "<该完整精确名称>"`，检查 ack 后目录查询为 ABSENT。没有 IF EXISTS/FORCE、连接终止或历史库处置。

共同身份：host `127.0.0.1`、port `15432`、admin database `postgres`、owner `thesisguard`、owner_oid `10`。node 完整前缀为 `tests/test_evidence_pg_fixture_lifecycle.py::test_real_postgres_resource_lifecycle`，下表列出参数；每资源的完整 run/node/attempt/name/OID/owner 和事件时间在 ledger/after.json。

| 场景/node 参数 | attempt_id / 数据库完整名称 | OID | 释放前连接 | 结果 |
| --- | --- | --- | --- | --- |
| [normal] | 986c40d28d2e4b828ea78706127e1d4d / tg_wp04_service_986c40d28d2e4b828ea78706127e1d4d | 8327525 | 0 | CONFIRMED → exact DROP → ABSENT |
| [migration_fault] | 46fa5ca4e7e64fe49119979e73069571 / tg_wp04_service_46fa5ca4e7e64fe49119979e73069571 | 8328225 | 0 | CONFIRMED → exact DROP → ABSENT |
| [engine_fault] | 7fe7afdba012426fa8a4bb459699f5ed / tg_wp04_service_7fe7afdba012426fa8a4bb459699f5ed | 8328226 | 0 | CONFIRMED → exact DROP → ABSENT |
| [body_fault] | c762b6f9e00247079d363e07e23bf30f / tg_wp04_service_c762b6f9e00247079d363e07e23bf30f | 8328926 | 0 | CONFIRMED → exact DROP → ABSENT |

normal 实际迁移及建立 sessionmaker，SELECT 1 后 rollback/关闭 session，再正常关闭 fixture。migration fault 在已确认 CREATE 后、upgrade 调用处注入 CalledProcessError(returncode 19)，此场景不把一次未执行的迁移视为成功。engine fault 在真实迁移完成后注入 engine factory 异常；body fault 在真实迁移、engine/sessionmaker 及 SELECT 1 后，通过 generator.athrow 注入同一异常对象。真实迁移成功事件总计三次，与设计一致。

ledger 的三条 primary_error 分别为 migration/CalledProcessError、engine/InjectedFailure、test_body/InjectedFailure，全部是预期注入；pytest 验证原异常对象或 returncode 并确认没有 cleanup note。normal 无 primary_error。它们不是三次未预期测试失败。

## 5. 历史 UNKNOWN 与实际 catalog 保全

精确输入：`/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-INDEPENDENT-REVERIFY-R1-evidence/phase-a-20260916-exact-cleanup-plan.json`，SHA-256 `635ba4aad0468c15b4360733c784d52f4430f03477a14ef8a271a1e32bada360`；既有 45 个名称的归属继续为 UNKNOWN，不因共同前缀、owner 或数量改判。confirmed cleanup 列表仍为空。

四个场景各自有一份真实 catalog_before 和 catalog_after；八份按完整 name/OID/owner 数组比较完全相同，每份实际列出 49 个库。以下为本轮 admin catalog 中实际身份（45 UNKNOWN + 四个非清理目标）；本轮未逐库连接 UNKNOWN，未读取其内容、终止连接或清理。历史库 owner 均为 thesisguard，但 owner 单独不证明归属。

| 实际名称 | OID | Owner | 本轮分类 |
| --- | --- | --- | --- |
| postgres | 5 | thesisguard | EXCLUDED；非本轮资源 |
| template0 | 4 | thesisguard | EXCLUDED；非本轮资源 |
| template1 | 1 | thesisguard | EXCLUDED；非本轮资源 |
| tg_wp04_service_01c0f5f8121e450b9c71ace44928c802 | 8325396 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_0685f5c993834a349abaf61fc3e3b657 | 8325415 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_11e6867d5f3542b293cdfd4a4fead7cf | 8325419 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_13471ec2ece84b93b8407e29c6054a6f | 8325405 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_1c5af01292b24f1aaec6fd4637403885 | 8325409 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_1ddedcea542a49f796be0bda8b9ac972 | 8325404 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_1f6901c614364010b70a6ea69fa01385 | 8325391 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_1fb496c5fa934a4b96d850d08ae192da | 8325387 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_28cbba54558442e4b7bff6179cf71746 | 8325421 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_29b5f21b05e64c35bcfba641816cee26 | 8325411 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_3cf61d305a374021b958d8c32c3cf5a0 | 8325399 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_3f430b834ec8486a892dad86209b9c48 | 8325389 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_430bc500937c40f19fd82fba561d6087 | 8325384 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_45c63d3d38894f7ea7643f10d250f370 | 8325390 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_470ab881404544a6995142c846276e47 | 8325410 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_4f008d22a8154f82954820a749edfeff | 6893828 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_534131d65bb74a449f6eaf7c31648b21 | 8325407 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_53f41488c0dd47d88d4591bec041a7a7 | 8325416 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_58cbbcc50bb44e5aad52b85c1c56c155 | 8325400 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_5d4c8451727743f79f7abdb40a4d88dc | 6893827 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_5f625721e89d4e728e9bd0d64d93dd17 | 8325412 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_69104f67fa53491589b4701388407499 | 8325393 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_737b02e3182f41b7a963126331b81279 | 8325398 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_758b5d420b0e400089a7b4b243cc3b0e | 8325403 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_762754d8160247888e78b9417afedb2c | 8325406 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_79a475ac90224a4b99082d145d292c15 | 8325395 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_81815e010a3d4f00973b55e8c8f1c856 | 8325402 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_90a93dc7364d4d9d92520f20675aed5c | 8325383 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_90be9919c0ff4891a0350ae6d28f5226 | 8325401 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_9725b95671f94617a4f29806a20db7a8 | 8325385 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_99f9613e82ea4c738deef31efbef215d | 8325388 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_b6f8802bd7e243eba1e6e0e138b40ebe | 8325397 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_bed9e7cc62514f188fe67180264772eb | 8325408 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_c52791461a844e15b463397e1670aeb6 | 8325414 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_ca3fc690d42142278b9dd2b8e76de967 | 6893825 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_d71be47c791b40788f67cdd0958c50e9 | 8325417 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_dc37c69cb5354bd18e5a3dcd01812e31 | 8325420 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_dd591583d60d4f8287f4adce3d5d1cfe | 6893826 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_de58a56a5edf406eb94693a9b9e83dba | 8325382 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_f33a4b72076e4499899debaf5e88885b | 8325392 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_f510786c26d24a2c98218f8949e8e7fb | 8325418 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_f5e42809dab54b8ca01a35a34f4ce0cb | 8325386 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_f62a9d9bee2147b7a6fbcf4ecc3d851f | 8325394 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_f99981ab17b74ba7a1028c973689388c | 8325422 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| tg_wp04_service_fa9205d9393e4de0a9bf75eca36ffc1b | 8325413 | thesisguard | UNKNOWN；八次身份一致，禁止清理 |
| thesisguard | 16384 | thesisguard | EXCLUDED；非本轮资源 |

本輪清理范围仅上节四个已证明归属的新资源，均已释放；剩余待清理本轮名单为空。历史 45 个 UNKNOWN 不列入拟执行目标，无后续数据库操作待执行。

## 6. 原四库与本轮四库的版本、预算区别

| 记录 | Run ID | CREATE 预算 | 真实结果及版本归属 |
| --- | --- | --- | --- |
| 原 R1 保存执行证据 | b2404b6ba2f348dbb962fb822177bc42 | 原独立预算 4/4，已用尽 | 原 4 passed / 29 deselected；helper 和专门 tests 为最终加固前版本，只支持那次记录的字节；原报告 BLOCKED 保留 |
| 本轮独立最终字节复验 | 0348c037ded74f91b992077a49fd9d9c | 用户新批准预算 4/4，已用尽 | 新鲜 4 passed / 32 deselected；最终固定五哈希验证；本轮 fixture PASS |

原真实运行 helper SHA-256：`2a5eeda1edcce7905fdc85ba7d4429aeb2b56d1d22a83573d1bc65b26318bd14`；原真实运行专门 tests SHA-256：`029c9c24176d43cee22d8b82f715e14c6c9b45b8dbc7802e52fccd4fa122e618`。本轮分别为第 1 节固定最终哈希。原 fixture 接线文件哈希与本轮固定值相同；原结果不追认为最终全部字节的独立验证。

| 原 R1 已释放资源（仅历史记录，本轮未操作） | OID |
| --- | --- |
| tg_wp04_service_c014108206a84be18b3eef20bb238d19 | 8325423 |
| tg_wp04_service_b9725319f4194a9bb13a29983c90ba57 | 8326123 |
| tg_wp04_service_99981375cf3f44fdbcfa4a107acd50de | 8326124 |
| tg_wp04_service_120283d9ce8b4861bf9386617acad778 | 8326824 |

## 7. 证据保护、产物与限制

前后比较：397 个主仓入口文件哈希全部不变，368 个受保护 acceptance 文件哈希全部不变（包括 Git 忽略的旧原始日志），186 个候选入口文件哈希全部不变。候选最终 clean/index empty；两仓 HEAD/parent/branch 均不变。只新增本报告及独立 evidence 目录五个必要文件：before.json、after.json、execution.log、resources.jsonl、manifest.json。测试缓存/执行辅助源码在独立 `/private/tmp/tg-pg-independent-29r_qwxr`；辅助源码也作为 manifest 的审查数据保存，未写入候选或旧 verifier。

| 旧证据 | 本轮核验 SHA-256（原件未修改） |
| --- | --- |
| 原 R1 evidence/manifest.json | 236a67b8adbeb1b6f408b8bfb6318ca1330134e83754f8cf0ea0363840a7a4ab |
| 原 R1 evidence/execution.log | 338a5202c20c58e8cf7c94f2ed3ebfbdcc303c2135252e40c9dfccf51782bcb6 |
| 原 R1 evidence/resources.jsonl | 7cc9359e2ca8676bb4c25b23e66fa95a026b4aab4ec522a6237772c0217b2ef7 |
| 原 R1 execution-report.md | dfa5d5648e7597ec8bd5cf174f315f0a9d91eb1dc3f770bc819669d6d6f18b90 |

本轮限制：真实验证仅四个获批场景。连接中断/停机、CREATE 回执不确定、ledger 写失败、identity/连接漂移及 cleanup failure 等其他失败路径取得确定性测试证据，没有额外真实故障预算。迁移 fault 是调用处异常注入；不声称验证 PostgreSQL 服务器故障或真实 Alembic 内部失败。不可中断的进程死亡无法由 Python finally 保证释放；此类未来不确定资源仍须精确调查，不允许强制清理。catalog 保全只证明八次观测中的 name/OID/owner 完整一致，不声称历史数据库内容的当前验证，也不证明其归属。

**下一任务仅建议另行派发 05C-01 独立业务复验**：使用本轮接受的固定 fixture，单独明确 CREATE 尝试预算、全新 run_id/空 ledger、精确释放及历史 UNKNOWN 保全前置。本任务不运行 full Evidence service、七份业务 verifier 或 Research 回归；不宣告 05C-01、R1C、WP04-02 完成，不进入 05C-02/R1D，不授权 Git 集成。
