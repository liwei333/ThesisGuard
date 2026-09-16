# TASK-WP04-02-R1C-01 Independent Acceptance

**OVERALL: PASS**

## Metadata / Classification

- Date: 2026-09-15，Asia/Shanghai。
- Task ID: `TASK-WP04-02-R1C-01`。
- Verifier: 本轮 Codex；独立于附件中的业务实现执行者。
- Source execution report: 用户附件 `9e934a1a-90d3-4078-b586-b1d92657d1b6/pasted-text.txt`，执行状态 IMPLEMENTATION_COMPLETE。
- Contract: `TASK-WP04-02-R1C-01-task-contract.md` 和 `TASK-WP04-02-R1C-01-dispatch-prompt.md`。
- Required / Achieved Acceptance: L1_STATIC_REVIEWED、L2_BUILD_VERIFIED、L3_CONTRACT_VERIFIED、L4_DB_VERIFIED。
- Missing Acceptance: 无本切片必需缺口；完整状态表、trusted registry、角色/source-grade/freshness 资格及 R1D 不在此次通过范围。
- Task Type / Size / Risk: REPAIR / SMALL / versioned PostgreSQL read eligibility and immutable history。
- Evidence Matrix: Full；G0–G6 与 DB Persistence Gate适用。
- Report Path: `docs/acceptance/TASK-WP04-02-R1C-01-acceptance.md`，遵循 AGENTS.md 治理约定。

## Baseline / Attribution / Scope

主仓开始 HEAD 为 `7d3734bc8346c16f9bbf7f7d9806309949c996de`，原有四个未跟踪治理文档保留不修改：R1C-01 task-contract/dispatch-prompt 和 baseline-confirm 来源/独立报告。未 fetch，不声明远端实时状态。

候选 branch：`codex/wp04-02-evidence-domain-service`。

候选 HEAD：`bdd70edc153b6ed5def65ed99c41f325df45f066`；parent：`f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`。

BASELINE_CHANGED_FILES（候选）和最终候选状态均仅有 services.py、tests/test_evidence_services.py modified。相对 HEAD diff 为273 insertions、2 deletions；生产代码仅一行集合替换。附件最终 hash、当前 hash 和实际 diff 一致，候选变更可归于所审查的交付内容；不把已有 dirty 文件归于 verifier 本轮。

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
cecffcd52371baf6bb6e85e733e565f4720e78d3d50fb65503b5d74998517df3  backend/evidence/services.py
aabe09b394fa4d23a13f245c512afc11d8c2100e3c85ab7b2569f89133d4e7e4  tests/test_evidence_services.py
909f50bd902ecd9c0013121681b614fcbc302f718cc7c9d5dc96f6237d106786  /tmp/test_wp04_02_r1b_r1_wiring_20260915.py
0f7cea4d14735bd165b75d756444259a64483a97e6a338227bc09af806490cc9  /tmp/test_wp04_02_r1b_reverify.py
66be45f354d1df34370eedd9811b3bc68cf29852d45027ea576a67975b18ddfe  /tmp/test_wp04_02_r1a_verifier.py
```

## Full Evidence Matrix

| AC | Requirement | Implementation evidence | Independent verification | Boundary / negative evidence | Verdict |
|---|---|---|---|---|---|
| AC-01 | highest version first、VERIFIED-only lifecycle、source RETRACTED 排除、missing None | services.py:83/1262；repositories.py:151 的 version.desc/limit1 | focused 11 passed；独立七状态、version/time逆序和读前后table counts；source-retracted正例 | 不按 created_at 取最新、不 fallback；不宣布所有角色/grade/freshness资格完整 | PASS |
| AC-02 | ordinary correction/replacement UNREVIEWED不继承；exact/history保留 | candidate R1C correction/replacement/history tests；生产 append 路径无变更 | focused / full suite；独立 pending/rejected 由 VERIFIED→ordinary correction→review构造，fresh reader保留 prior VERIFIED | 旧测试纠正只改其错误current-valid断言；children/link/audit断言保留 | PASS |
| AC-03 | 真实RED→最小修复GREEN | git diff证明生产唯一变化是允许集合；附件列出4个历史RED节点 | 独立进程临时恢复该唯一旧常量，在真实PG与公开命令上取得3 failed/4 passed；正常常量同一verifier8 passed | 不修改candidate/Git；不是原执行者历史顺序的工具审计，不冒充重新运行原4节点RED；对照仍使用真实DB，非Fake生产证明 | PASS |
| AC-04 | 完整验证矩阵、R1A/R1B及immutable/no-residue保护 | candidate全部测试、三个旧固定verifier | 本轮逐命令全绿：109/35、3/4/12、focused11、额外8；静态矩阵通过 | fixture均正常权限执行；无setup/cleanup异常输出；未做全实例残留扫描，不声称全局零残留 | PASS |
| AC-05 | 两文件边界、errors/verifiers/HEAD不变、可追踪证据 | 实际diff/status/SHA；附件scope/结果 | before/final status/HEAD/hash；本轮未改业务 | 无Git write、schema/API/contract修改；执行者未自行输出PASS结论 | PASS |

## Commands Actually Executed / Results

所有DB pytest均通过正常 require_escalated，工作目录为候选；公共前缀为 `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q`。

| Target / command suffix | Actual result |
|---|---|
| `tests/test_evidence_services.py -k "r1c or current_valid or lifecycle" -rs` | exit0；11 passed、98 deselected、2 warnings、11.75s |
| `/tmp/test_wp04_02_r1b_r1_wiring_20260915.py -rs` | exit0；3 passed、11.71s |
| `/tmp/test_wp04_02_r1b_reverify.py -rs` | exit0；4 passed、6.18s |
| `/tmp/test_wp04_02_r1a_verifier.py -rs` | exit0；12 passed、31.55s |
| `tests/test_evidence_services.py -rs` | exit0；109 passed、2 warnings、91.99s |
| `tests/test_evidence_persistence.py tests/test_migrations.py tests/test_evidence_migrations.py tests/test_research_api.py tests/test_research_persistence.py -rs` | exit0；35 passed、4 warnings、59.86s |
| `/tmp/test_wp04_02_r1c_01_independent_20260915.py -rs` | 初次8 passed/10.41s；补充baseline开关后最终8 passed/7.37s、exit0 |
| `TG_R1C_REPLAY_BASELINE=1` + same prefix + `/tmp/test_wp04_02_r1c_01_independent_20260915.py -k latest_version -rs` | 预期exit1；UNREVIEWED/PENDING_REVIEW/DISPUTED三个真实资格断言失败；3 failed、4 passed、1 deselected、6.67s |

独立 verifier 最终 SHA：`857914f073c552be98f895a456d2f0ec486452e1c9aed06a87176c6e7fefd48a`。该文件为本轮新增临时证据，不改写三个旧 verifier。baseline对照开关只作用于该命令的进程内允许集合，不更改DB route、fixture或candidate文件。

本轮 ruff check --no-cache、ruff format --check --no-cache均exit0（3 files already formatted）；mypy `MYPYPATH=. --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1c-01-independent-mypy` exit0，无三文件类型问题，仅既有unused section note；compileall使用`PYTHONPYCACHEPREFIX=/tmp/tg-r1c-01-independent-pycache` exit0；Alembic heads exit0为000000000004；candidate git diff --check exit0。其他实际命令为Git status/rev-parse/diff/stat/numstat、六文件SHA、相关source/model/repository/contract的cat/sed/rg。

## DB / Architecture / Regression Boundaries

TG_TEST_ADMIN_DATABASE_URL本轮未设置（printenv无输出exit1）。已读取fixture，现有本地127.0.0.1:15432按UUID创建临时库、库内迁移并精确teardown；无任意SQL或broad cleanup。独立七状态通过真实公开命令、真实PG和新reader session验证，不依赖仅同一session对象缓存。

历史与children不覆盖，服务仍不commit，schema/repository/迁移无变更。最高version而非created_at的选择、prior VERIFIED保留和读前后无写入已单独证明。无setup/cleanup exception输出，无已知残留；未扫描所有PG库。

G0 Baseline、G1 Scope、G2 Contract、G3 Architecture、G4 Test、G5 Regression、G6 Evidence、DB Persistence全部PASS。Blocking Findings：无。Repair Required：NO。

## Remaining Work / Next Action

仅关闭 R1C-01 生命周期读取资格切片，不关闭整个R1C、原WP04-02或其所有AC。已知剩余：verify_or_reject允许源状态/审计kind、mark_disputed过宽、invalidate/retract过宽、trusted任意字符串提升VERIFIED等；这些未被本次读取切片修复，也不逆向推翻本次范围内PASS。

下一最小任务 `TASK-WP04-02-R1C-02`：review/dispute/invalidation/retraction命令状态表与audit映射。以当前dirty且已验收的两文件hash为起点，不要求clean、不commit。trusted/correction/import完整资格另行后续处理，随后R1D、TASK-WP04-02-REVERIFY；API/Research refs、Sector Crowding/Capability Runtime不自动解锁。

本轮仅新增此报告、R1C-02 task-contract和/private/tmp独立verifier；主仓原四份未跟踪治理文件不修改；candidate业务文件/HEAD保留不变。新Markdown有针对实际文件的trailing-whitespace检查，不以git diff忽略untracked文件的无输出冒充验证。

最终主仓另出现未跟踪 `docs/MARKET_DATA_TECHNICAL_PLAN.md`，不在开始快照中；不是本轮创建或修改，归因 UNKNOWN，未读取/清理/提交。最终主仓共七个未跟踪文件，其中本轮可归因新增仅上述两份acceptance治理文件。该无关文档变化不改变候选业务基线或本切片结论。
