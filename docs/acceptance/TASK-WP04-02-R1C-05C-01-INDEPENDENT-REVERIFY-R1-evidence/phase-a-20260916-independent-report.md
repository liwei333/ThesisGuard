# TASK-WP04-02-R1C-05C-01-INDEPENDENT-REVERIFY-R1 — Phase A independent report

OVERALL: **BLOCKED**

证据时点：2026-09-16，Asia/Shanghai。角色：独立 verifier / 环境与数据库归属调查；仅 Phase A。此次完成环境预检和只读调查，不构成 05C-01 的 PASS 或 Phase B 派发。未启动任何数据库测试，未重跑业务 RED。

阻塞有两项：固定 HEAD/parent/dirty scope 已在本阶段开始前漂移；45 个已盘点名称无法逐库证明属于失败 verifier 的那次运行。精确确认清理名单为 `[]`，拟执行数据库变更为 `[]`，没有清理批准。保持 BLOCKED。

## 授权与保全边界

授权来源为用户本轮明确派发 Phase A，及完整 verifier 合同的 Phase A 条款。所有新脚本、日志、报告、计划和 manifest 仅位于本报告所在的独立 evidence 目录。既有 BLOCKED acceptance、executor 报告/manifest/日志、盘点、候选服务/测试、fixture、verifier、冻结和规范文档全部保留。没有 Git 写操作、依赖安装、shell profile 修改、fixture 修改、数据写入 SQL、DROP、连接终止、迁移执行、容器操作、替代实例或广泛清理。05C-02/R1D 未进入。

技能：using-superpowers、ai-task-governor、systematic-debugging、verification-before-completion。Phase A 用户边界控制执行范围，不用技能扩张到代码修复或测试。完整读取主仓与候选 AGENTS.md、用户列明四份文件、05C-01 dispatch/executor report/policy addendum；原 fixture 及固定 verifier 的字节/fixture 声明用于本阶段预检。此次不声称完整候选业务静态验收已重做。

## 固定基线与实测

| 仓库 | 合同固定 HEAD | 合同固定 parent | 实测 HEAD | 实测 parent | 实测 dirty scope |
| --- | --- | --- | --- | --- | --- |
| main / main | 438738c543e4cae3e805d31324b068c1cd5c7059 | 7d3734bc8346c16f9bbf7f7d9806309949c996de | d3acc1c6f4a2e5ce1fe4b973d7855409c0db1da5 | 438738c543e4cae3e805d31324b068c1cd5c7059 | tracked/index empty；本阶段仅新增独立 evidence |
| candidate / codex/wp04-02-evidence-domain-service | 0cef44fd2ffd929b40e849e607af0bd4c44d14d2 | bdd70edc153b6ed5def65ed99c41f325df45f066 | af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8 | 0cef44fd2ffd929b40e849e607af0bd4c44d14d2 | empty；合同要求 services.py / tests 两处累计 M |

主仓新增提交时间为 16:55:00 +08:00；候选为 16:55:15 +08:00，均早于此次 16:58 工具/DB 预检。实测两个提交的 parent 恰为合同固定 HEAD。候选新增提交仅包含原累计 services/test 两文件 delta，统计为 1723 insertions、34 deletions。该关联与文件一致性解释现状，不能替代合同身份或授权。未要求 clean、未 checkout/reset/rebase、未把新提交静默定为基线。

最终三文件均匹配 verifier 合同（原开发合同初始 services/test 哈希不同，是历史起点，不用于替换最终要求）：

| 文件 | 最终实测 SHA-256 / 合同要求 | 匹配 |
| --- | --- | --- |
| backend/evidence/errors.py | `3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec` | True |
| backend/evidence/services.py | `7ce76b02928019347625048e7d0acb523d74168cd6bbbdf03184163ac277f959` | True |
| tests/test_evidence_services.py | `b5bfcdeb2db6753c71fd146b935dd26229daae0d73da5bda68af437db137b950` | True |

七个固定 verifier SHA 全部匹配；完整逐文件值在 `phase-a-20260916-integrity-check.json`。原测试前 191662 bytes SHA 为 `dce8c3644441399ef443d54073c3121e8f59ebcd330c6955458c5db703056308`。旧保护 map 的主仓 283 / 候选排除授权两文件后 63 文件无 mismatch；executor manifest 的 80 个条目长度和 SHA 全匹配，executor report SHA `e1678c9818f6673cf950433c3ae3b183c3a45f83b36e7cb0828da65d09057dfd` 匹配。

此次 before/after 快照核对主仓 505、候选 184 个已有文件：modified / removed / added-outside-evidence 均为空。证据目录从快照保护集合排除，避免把本阶段合法新增视为候选漂移。Git HEAD/parent/branch 在此次前后相同，候选 tracked/index 保持 empty。

## 成功 executor 与失败 verifier 环境

成功 executor 的 `environment.json` 和 `final2-focused-final-hash.json` 提供实际路径、版本、PATH/PYTHONPATH、UTC start/end、exit 0 和日志 SHA。该 focused 历史运行是 08:25:45.098143–08:26:28.336842 UTC；此次只检查其 artifact 完整性，不沿用为独立 runtime PASS。

原失败 verifier 的旧 acceptance 记录：显式 Homebrew pytest、candidate/Homebrew PYTHONPATH，未明确组装含 Alembic 的 command-local PATH；41 selected / 337 deselected、41 setup ERROR、exit 1，`FileNotFoundError: 'alembic'` 位于原 fixture subprocess.run。失败的完整有效 PATH、精确开始/结束时刻、逐 node UUID DB mapping 没有在现存 main docs 中保留。此次 /private/tmp 任务相关文件名搜索发现缓存，没有找到该失败任务的 raw log/command metadata。不能把当前父 shell 的 PATH 冒充历史失败子进程 PATH。

fixture source 证实先用 UUID CREATE DATABASE，然后调用裸 `alembic upgrade head`；try/finally 在成功迁移/engine setup 后才开始，因而缺失 Alembic 会在进入 yielded cleanup 前失败。此次只读源码，未调用 fixture 或 upgrade。该错误属于工具发现/setup，不是业务断言 RED；没有因此授权修复业务代码或 fixture。

当前通过正常 require_escalated、login=false，在候选 cwd 使用以下明确 command-local 环境完成预检；后续若被派发实际测试，必须复用这一环境及显式 pytest 路径：

```text
PATH=/opt/miniconda3/bin:/opt/homebrew/bin:/opt/homebrew/opt/postgresql@16/bin:/usr/bin:/bin:/usr/sbin:/sbin
PYTHONDONTWRITEBYTECODE=1
PYTHONPATH=/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service:/opt/homebrew/lib/python3.12/site-packages
pytest executable=/opt/homebrew/bin/pytest
python executable=/opt/homebrew/bin/python3.12
```

三个 diagnostic variables：TG_TEST_ADMIN_DATABASE_URL、TG_R1C_REPLAY_BASELINE、TG_R1C02_REPLAY_PRIOR 全部 UNSET（未静默 unset 掩盖既有配置）。没有安装依赖。PATH 是进程局部标准环境项，没有 shell/profile 持久更改。

| 工具 | 采用的既有路径 | 实测版本 | exit |
| --- | --- | --- | --- |
| python | /opt/homebrew/bin/python3.12 | Python 3.12.9 | 0 |
| pytest | /opt/homebrew/bin/pytest | pytest 9.1.1 | 0 |
| alembic | /opt/miniconda3/bin/alembic | alembic 1.18.5 | 0 |
| ruff | /opt/miniconda3/bin/ruff | ruff 0.16.1 | 0 |
| mypy | /opt/miniconda3/bin/mypy | mypy 2.3.0 (compiled: yes) | 0 |
| psql | /opt/homebrew/opt/postgresql@16/bin/psql | psql (PostgreSQL) 16.13 (Homebrew) | 0 |

pytest 的 shebang 是 `/opt/homebrew/opt/python@3.12/bin/python3.12`；Alembic/mypy shebang 是 `/opt/miniconda3/bin/python`。混合工具来源是原成功 executor 的配置，不能只凭裸 command 名称假定同一 Python。当前裸 `pytest` which 为 `/opt/miniconda3/bin/pytest`；未来测试必须显式 Homebrew pytest。Python 库版本为 pytest 9.1.1、pytest-asyncio 1.4.0、asyncpg 0.31.0、SQLAlchemy 2.0.52、boto3 1.43.93，与历史成功环境一致。

子进程以与原 fixture 相同的 `{**os.environ, 'DATABASE_URL': ...}` 继承方式检查（DATABASE_URL 仅为不访问 DB 的无密码占位；heads 不连接 DB）：`shutil.which('alembic')` 返回 `/opt/miniconda3/bin/alembic`，exit 0；同一继承环境执行 `alembic -c migrations/alembic.ini heads` 返回 `000000000004 (head)`，exit 0。当前 command-local PATH 解决了预检中的工具发现前置；不声称 pytest fixture/migration/DB 测试已通过。版本、真实路径、shebang、工具 executable 指纹、子进程实际 PATH/PYTHONPATH 和原始 stdout/stderr 在 effective-environment JSON 中。

psql 是 16.13，既有服务端是 17.11；旧 `psql --list` 曾因 catalog 列重命名失败。此次使用现存 asyncpg 0.31.0 的精确只读 SQL，避免重复错误的 psql list 命令；没有安装客户端或换实例。

## 实际实例、名单与逐库元数据

所有连接的客户端目标固定 `127.0.0.1:15432`，只使用原 fixture 已有账号。服务端报告 PostgreSQL 17.11、内部地址 172.24.0.4/32、内部端口 5432、postmaster_start=2026-09-16 01:22:57.242534+00:00。这是既有端点的服务端返回值，未据此直接访问其他地址或操作容器。

角色 thesisguard 是 superuser/createdb/login；拥有 PostgreSQL 权限不等于具有删除授权。全部连接以 startup setting `default_transaction_read_only=on` 和专用 application_name 建立，逐库实测 transaction_read_only=on。实际执行 SQL 仅 SELECT；完整 SQL/参数/结果在 readonly-query-log JSON 和目录/cache 元数据 JSON，没有执行任何数据写入 SQL。

此次实际 before-name 快照为 49 库：原盘点 45 个全部存在，另有 `postgres`、`template0`、`template1`、`thesisguard`。这些其他库仅在 admin catalog 名单中观察，未进入逐库内容调查或清理名单。after 名单也为 49，added_names=[]、removed_names=[]。before/after 是此次调查的快照，不能补成旧失败运行的 before snapshot。

45 库每库 owner=thesisguard、non-template、allowconn=true、connlimit=-1、datacl=NULL、database comment=NULL。逐库连接全部 SUCCESS；仅 public schema（pg_database_owner / standard public schema）、plpgsql 1.0，用户 relations/routines 均无，large_object_count=0；没有 Alembic version table、没有 Evidence/Research 用户表。这里的“空”限于明确检查的目录对象范围，不宣称所有系统文件或系统 catalog 为空。

活动连接的两次精确 datname 查询覆盖所有45库：调查前、逐库连接关闭后均没有其他 session，包含 idle 在内；排除了本调查 admin backend。连接状态只代表观察时点，不能保证未来无并发使用。

PG 当前 logging_collector=off、log_destination=stderr、log_statement=none、log_min_duration_statement=-1；pg_current_logfile=NULL，pg_ls_logdir 报 `could not open directory "log": No such file or directory`。这项只读目录诊断本身返回错误并已保存，不能写成日志目录检查成功；没有去容器读取日志，也没有修改日志配置。

45 库目录 creation=NULL；PostgreSQL catalog 不提供可靠数据库创建时间。目录 access/modification/change 是实际元数据，逐库保存在 exact-cleanup-plan 和 directory-metadata JSON。此次连接后目录时间在 08:58:48 UTC 附近更新，不能解释为原创建时间。

物理变化如实记录：每库 before size=7,569,935 bytes，after size=7,730,867 bytes，增加160,932 bytes。每库随后读到 pg_internal.init 文件 size=160,932 bytes、modification/change 同在此次连接时段。据此推断大小变化与后端初始化缓存有关；缺少调查前的逐文件快照，不能断言绝对因果或物理零写入。SQL 只读不意味着物理磁盘字节不变，此次没有对缓存文件做清理。

下面每行都关联各自的 catalog/contents/session 证据；对象列依次为用户 relations / routines / large objects，连接为 before / after。所有行都不列为清理目标。

| 精确名称 | OID | owner | 对象 | 连接 | failed-verifier 归属 | 清理目标 |
| --- | --- | --- | --- | --- | --- | --- |
| `tg_wp04_service_01c0f5f8121e450b9c71ace44928c802` | 8325396 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_0685f5c993834a349abaf61fc3e3b657` | 8325415 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_11e6867d5f3542b293cdfd4a4fead7cf` | 8325419 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_13471ec2ece84b93b8407e29c6054a6f` | 8325405 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_1c5af01292b24f1aaec6fd4637403885` | 8325409 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_1ddedcea542a49f796be0bda8b9ac972` | 8325404 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_1f6901c614364010b70a6ea69fa01385` | 8325391 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_1fb496c5fa934a4b96d850d08ae192da` | 8325387 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_28cbba54558442e4b7bff6179cf71746` | 8325421 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_29b5f21b05e64c35bcfba641816cee26` | 8325411 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_3cf61d305a374021b958d8c32c3cf5a0` | 8325399 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_3f430b834ec8486a892dad86209b9c48` | 8325389 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_430bc500937c40f19fd82fba561d6087` | 8325384 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_45c63d3d38894f7ea7643f10d250f370` | 8325390 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_470ab881404544a6995142c846276e47` | 8325410 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_4f008d22a8154f82954820a749edfeff` | 6893828 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_534131d65bb74a449f6eaf7c31648b21` | 8325407 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_53f41488c0dd47d88d4591bec041a7a7` | 8325416 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_58cbbcc50bb44e5aad52b85c1c56c155` | 8325400 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_5d4c8451727743f79f7abdb40a4d88dc` | 6893827 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_5f625721e89d4e728e9bd0d64d93dd17` | 8325412 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_69104f67fa53491589b4701388407499` | 8325393 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_737b02e3182f41b7a963126331b81279` | 8325398 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_758b5d420b0e400089a7b4b243cc3b0e` | 8325403 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_762754d8160247888e78b9417afedb2c` | 8325406 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_79a475ac90224a4b99082d145d292c15` | 8325395 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_81815e010a3d4f00973b55e8c8f1c856` | 8325402 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_90a93dc7364d4d9d92520f20675aed5c` | 8325383 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_90be9919c0ff4891a0350ae6d28f5226` | 8325401 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_9725b95671f94617a4f29806a20db7a8` | 8325385 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_99f9613e82ea4c738deef31efbef215d` | 8325388 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_b6f8802bd7e243eba1e6e0e138b40ebe` | 8325397 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_bed9e7cc62514f188fe67180264772eb` | 8325408 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_c52791461a844e15b463397e1670aeb6` | 8325414 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_ca3fc690d42142278b9dd2b8e76de967` | 6893825 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_d71be47c791b40788f67cdd0958c50e9` | 8325417 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_dc37c69cb5354bd18e5a3dcd01812e31` | 8325420 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_dd591583d60d4f8287f4adce3d5d1cfe` | 6893826 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_de58a56a5edf406eb94693a9b9e83dba` | 8325382 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_f33a4b72076e4499899debaf5e88885b` | 8325392 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_f510786c26d24a2c98218f8949e8e7fb` | 8325418 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_f5e42809dab54b8ca01a35a34f4ce0cb` | 8325386 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_f62a9d9bee2147b7a6fbcf4ecc3d851f` | 8325394 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_f99981ab17b74ba7a1028c973689388c` | 8325422 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |
| `tg_wp04_service_fa9205d9393e4de0a9bf75eca36ffc1b` | 8325413 | thesisguard | 0/0/0 | 0/0 | UNKNOWN | NO |

## 归属证据、确认名单与不确定名单

本次主仓 docs 全文精确名称检查中，每个名称仅命中旧 observed inventory JSON，没有 executor/failed-verifier log 的 CREATE DATABASE 名称—node/run对应关系。检查文件数及逐名称 path/line 在 historical-attribution-check JSON。原 fixture 使用 uuid4 且在缺失 executable 时并不打印其 test_db_name；旧 acceptance 提供41 setup ERROR计数，却没有生成名称映射或失败前名单。

OID 存在41个连续值8325382–8325422，另4个为6893825–6893828。这与“41失败 / 45 observed”的线索相容，但不是逐库运行归属证明；未把连续组列为确认，也未把4个较小 OID 库武断称为其他任务库。四个较小 OID 名称分别为：

- tg_wp04_service_ca3fc690d42142278b9dd2b8e76de967
- tg_wp04_service_dd591583d60d4f8287f4adce3d5d1cfe
- tg_wp04_service_5d4c8451727743f79f7abdb40a4d88dc
- tg_wp04_service_4f008d22a8154f82954820a749edfeff

确认名单：`[]`（0）。不确定名单：上表全部45个精确名称（45），machine plan 的 unknown_names 完整保留。PostgreSQL owner、prefix、计数、OID分组、目录年龄、空对象和无活动连接的组合仍缺失核心 run-specific provenance，不能证明是失败 verifier 的可处置库。

## 拟操作与风险

当前 proposed_mutating_operations=[]、approved_cleanup_names=[]：不拟执行任何 DROP 或连接终止，没有生成可执行清理脚本。不能对空确认名单请求一个实际上覆盖 UNKNOWN 的隐含批准。

后续需要 dispatcher 明确处理固定身份漂移，并补充精确名称与可处置授权运行的对应证据；若仍无法归属，需要用户针对 UNKNOWN 的处置方向和另行有边界的合同，不能猜测。形成新的精确确认目标及操作计划并取得明确批准后，才可能进入获派发的 Phase B。届时须再次核对既有端点、精确名称、OID、owner、内容和连接；任何改变/活动连接应停止，不能以默认 FORCE/终止绕过。不得 prefix/glob 删除、扩大到未列名库或其他4个实际系统/业务库。许可、清理和新测试派发是不同前置，本次只读操作的正常提权批准不是清理批准。

主要风险：错误归属导致误删别的任务库；时间点 idle 不能代替执行时连接检查；读连接会改变物理缓存/目录时间，削弱年龄推断；候选字节匹配不能代替固定 commit/scope 身份。没有展示业务缺陷，不授权业务修复，也不把环境预检作为 L3/L4 成功。

## Phase A evidence matrix / handoff

| 要求 | 此次独立证据 | 结论/限制 |
| --- | --- | --- |
| 固定HEAD/parent/dirty + final hashes | before/after files、Git完整stdout、integrity JSON | identity/scope MISMATCH；最终3哈希匹配；BLOCKED且不重定基线 |
| 既有工具及真实child PATH/heads | normally approved environment命令；effective-environment JSON | preflight checks exit0；没有test/fixture执行 |
| 实际名单/45库归属、对象、连接 | before/after catalogs、每库metadata、目录/缓存、历史全文检查 | 45都UNKNOWN，0 confirmed，0 mutating operations |
| 原全业务/verifier/regression矩阵 | 此阶段未执行 | L3_CONTRACT_VERIFIED/L4_DB_VERIFIED缺失；Phase B未授权 |
| 文件与旧证据保全 | 505/184前后map、283/63旧map、7verifier、80artifact | 无本阶段已有文件修改或删除；所有新产物仅独立目录 |

正式 verdict 为 BLOCKED。这是独立 Phase A 报告，保留旧正式 BLOCKED acceptance；未宣告05C-01 PASS、R1C/WP04-02完成或Git集成。
