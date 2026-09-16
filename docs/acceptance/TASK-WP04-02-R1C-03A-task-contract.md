# TASK-WP04-02-R1C-03A — Trusted Correction Admission / No Implicit Inheritance

Status: `READY_FOR_USER_DISPATCH`，本合同不自动开始业务或授予Git/DB权限。

## A. Execution Core

- Task ID: `TASK-WP04-02-R1C-03A`。
- Objective: 禁止未授权的trusted rule字符串提升修正版本为VERIFIED；普通修正不继承prior rule，保持UNREVIEWED。
- Why Now: R1C-01读取资格、R1C-02四个status命令矩阵已验收；当前任意truthy字符串以及prior rule隐式继承仍可提升VERIFIED。
- Role / Type / Size: EXECUTOR / REPAIR / SMALL，单一correction准入边界，不同时实现完整trusted engine/import资格/R1D。
- Required Acceptance: L1_STATIC_REVIEWED、L2_BUILD_VERIFIED、L3_CONTRACT_VERIFIED、L4_DB_VERIFIED；Full matrix。

### Baseline / Investigation

主仓 `/Users/qianduoduo/Desktop/AI_app/ThesisGuard`：完整读AGENTS.md、本合同、R1C-01/02正式acceptance、R1C-02合同、原R1 repair program、冻结Evidence合同的current/lifecycle/correction/provenance/identity/audit与例25/26/41。治理文档从主仓读取。

候选 `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`；branch `codex/wp04-02-evidence-domain-service`；HEAD `bdd70edc153b6ed5def65ed99c41f325df45f066`；parent `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`。

起点恰好services.py和tests/test_evidence_services.py modified；保留全部已验收R1C-01/02内容，不要求clean、不commit/reset/checkout。开始核对：

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
5419448d3b73c0c0e2c1144d7615cdbe399266be5b9dd70281d91cf1a485d632  backend/evidence/services.py
b4a03614a02629efbfe46428778b54c2539c2ce897af7499cba439a99f7d7c59  tests/test_evidence_services.py
909f50bd902ecd9c0013121681b614fcbc302f718cc7c9d5dc96f6237d106786  /tmp/test_wp04_02_r1b_r1_wiring_20260915.py
0f7cea4d14735bd165b75d756444259a64483a97e6a338227bc09af806490cc9  /tmp/test_wp04_02_r1b_reverify.py
66be45f354d1df34370eedd9811b3bc68cf29852d45027ea576a67975b18ddfe  /tmp/test_wp04_02_r1a_verifier.py
857914f073c552be98f895a456d2f0ec486452e1c9aed06a87176c6e7fefd48a  /tmp/test_wp04_02_r1c_01_independent_20260915.py
64162c0aafc3ad620ee0cab5e4d8d0ed10e6d61ab8dc21322f4364144c442a05  /tmp/test_wp04_02_r1c_02_independent_20260915.py
```

检查create_evidence_series_version、revise_correct_evidence、create_replacement_evidence_series及private append/helpers的trusted输入与状态选择；查清 _UNSET/None、replacement route和idempotent replay的调用次序，不能仅在单一路径加检查。

### Explicit Policy / Preconditions

本切片**不启用任何生产trusted correction rule**。当前所读冻结合同规定必须命名并验证rule，但未给出可直接启用的具体rule谓词；`same-source-parser-v1`和`concurrent-test`仅为既有测试字符串，不是授权依据。

因此本次交付是显式、默认拒绝的correction准入策略：生产已批准rule集合为空，可以用services内不可变空allowlist表达，但不得把空集合写成完整trusted registry/validator已实现。未知规则，包括上述既有测试字符串，明确失败；不静默降级为ordinary来吞掉用户的trusted请求。

未来命名规则的正向启用、registry-specific semantic validator及initial import完整资格需要单独精确规则合同和验收，不得在本次自定规则或把注入测试rule算生产能力。普通review得到VERIFIED的已有合法路径不受这一correction规则禁用影响。

### Top Blocking AC

1. revise_correct_evidence（same-series及自动replacement route）、direct replacement和底层create入口的trusted correction参数不能成为绕过点。非None且未批准的rule拒绝，使用既有domain validation错误code/可追踪details；不得truthiness提升或静默接受。
2. ordinary correction：未提供rule或明确None都表示本命令无trusted授权；新版本UNREVIEWED、trusted_correction_rule=None，不继承prior row rule；身份改变仍按R1B新series v1 routing，审计四字段完整CORRECTION。
3. 非法trusted请求在新series/version/children/idempotency/audit持久化前拒绝，caller可以继续使用事务；失败后commit再用fresh session证明无残留，prior exact及children不变。
4. 真实PG RED→最小GREEN；保留ordinary correction/replacement、合法review、R1C-01/02资格/状态表、R1A/R1B及完整regression/static矩阵；不改旧verifier。
5. 仅授权两文件业务修改、errors/合同/schema/HEAD不变；清楚报告生产规则集合为空、正向trusted能力未交付，不自行宣布R1C或WP04-02完成。

### Scope / Key Examples

只允许candidate services.py、tests/test_evidence_services.py，必要private validation可最小添加，保留公开签名/现有错误code。errors原字节。

- Given prior VERIFIED，When unknown-rule correction，Then domain拒绝且新行/审计/幂等无残留。
- Given旧历史版本携带legacy rule，When新correction未传rule，Then新版本UNREVIEWED且rule=None；prior exact保持原rule/status，不能修改旧行清除历史。
- Given ordinary identity-changing correction，When rule omitted/None，Thenreplacement v1 UNREVIEWED、完整CORRECTION tuple；routing/children保留。
- Given blank/whitespace/非字符串/大小写变体rule，Then按未批准/非法输入拒绝；不可自动trim/casefold成未来合法ID。None为ordinary，空字符串不是None。

legacy prior可按真实fixture合法追加完整测试历史版本表示已存在的数据，不作为新生产trusted rule的许可；优先复用已有合法公开命令与约束合法seed。不得修改生产检查、constraint、全局fixture或历史行来制造测试。

保留既有同请求idempotent replay语义，不用该切片顺手实现R1D完整hash/concurrency/UNKNOWN_OUTCOME；历史已接受请求的replay不是新trusted授权，若当前旧replay逻辑与本scope产生无法安全收敛的冲突，BLOCKED并由dispatcher单独处理，不偷偷改变合同。

旧测试的truthy rule成功fixture需要明确按冻结合同更正：`test_revision_lifecycle_and_tombstone_are_append_only`中非本任务的parser修正改用ordinary并保留原version/children/history断言，增加UNREVIEWED正断言；`test_concurrent_revision_allows_only_one_next_version`移除concurrent-test的假trusted参数，保留一胜一冲突、单N+1和历史断言。新增独立unknown-rule拒绝反例，不通过删除测试或改为任意异常弱化回归。

不得改initial VERIFIED import的完整策略、ordinary correction合法from-status完整表、role/source-grade/F/freshness资格；它们明确仍未完成。底层create对提供trusted rule的输入准入校验可改，未提供rule的正常initial import不在本切片重构。

### Required Verification

先只加测试取得真实业务RED，再改services；不是permission/setup失败。覆盖三个公开入口与自动replacement route、prior legacy不继承、None ordinary、空/未知rule、fresh-session无残留、exact历史/children；未修起点意外全绿则BLOCKED。

从候选正常权限执行；既有本地127.0.0.1:15432 disposable fixture，TG_TEST_ADMIN_DATABASE_URL不能重定向；两个诊断变量TG_R1C_REPLAY_BASELINE、TG_R1C02_REPLAY_PRIOR均未设置。

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_services.py -k "r1c or trusted or current_valid or lifecycle or state_transition" -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1c_02_independent_20260915.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1c_01_independent_20260915.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_r1_wiring_20260915.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_reverify.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1a_verifier.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_persistence.py tests/test_migrations.py tests/test_evidence_migrations.py tests/test_research_api.py tests/test_research_persistence.py -rs
ruff check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
ruff format --check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
MYPYPATH=. mypy --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1c-03a-mypy backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
PYTHONPYCACHEPREFIX=/tmp/tg-r1c-03a-pycache python -m compileall -q backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
alembic -c migrations/alembic.ini heads
git diff --check
git status --short --branch --untracked-files=all
git rev-parse HEAD HEAD^
shasum -a 256 backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py /tmp/test_wp04_02_r1b_r1_wiring_20260915.py /tmp/test_wp04_02_r1b_reverify.py /tmp/test_wp04_02_r1a_verifier.py /tmp/test_wp04_02_r1c_01_independent_20260915.py /tmp/test_wp04_02_r1c_02_independent_20260915.py
```

现有fixture精确临时库创建/库内迁移/teardown属于测试步骤，不授权任意SQL、业务库migration或broad清理；迁移head保持000000000004。报告actual selected节点、red/green和完整矩阵，不只引用旧PASS。

### Must Not / Stop Conditions / Evidence

不修改error/model/repository/schema/migrations、旧合同/报告/verifier、API/主仓治理文档；不commit/merge/rebase/reset/checkout/push；不新增运行时可注册trusted rule的公共入口或配置绕过。

基线不符、权限拒绝、fixture异常、无法取得真实RED、必须越界/弱化标准时BLOCKED。已知临时库残留只报告精确目标，不自行broad cleanup。

只报告IMPLEMENTATION_COMPLETE或BLOCKED；提供all entry points→实现/测试、真实RED/GREEN、ordinary不继承、fresh-session无残留、prior历史保护、完整命令结果、最终两文件SHA/HEAD/status及本任务增量。明确生产approved rule集合为空，正向trusted registry/validator、initial import资格、ordinary完整状态表、R1D/原WP04-02 REVERIFY仍未完成。

## B. Governance Appendix

使用systematic-debugging、test-driven-development、verification-before-completion，遵守ai-task-governor core invariants/anti-drift/acceptance levels/evidence-based acceptance。不得改AC、伪造生产能力或自我验收。

此切片是修复不安全准入，不是完整trusted功能交付。完成后等待独立验收；正向命名规则须另行规则定义/授权/验证，其他WP、Sector Crowding和Capability Runtime不自动解锁。
