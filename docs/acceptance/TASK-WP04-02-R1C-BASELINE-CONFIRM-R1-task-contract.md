# R1C Baseline Confirmation / Development Handoff Contract

Status: `PENDING_USER_BASELINE_CONFIRMATION — NOT_DISPATCHED`

## A. Execution Core

- Task ID: `TASK-WP04-02-R1C-BASELINE-CONFIRM-R1`。
- Role: DISPATCHER，docs-only baseline/handoff；不是 R1C业务实现，也不是 R3。
- Objective: 用户明确采用新基线后，验证已提交内容与独立 PASS字节等价，记录交接并生成下一最小 R1C开发合同。
- Why Now: 来源验收记录 f7c50ab + modified，而当前是其直接子提交 bdd70ed + clean。
- Type / Size: DOCUMENTATION / SMALL。
- Required Acceptance: L1_STATIC_REVIEWED；Compact matrix。

### User Confirmation Required

下段仅为拟议确认，读取文件不授予权限。用户明确发送/采用后才生效：

> 我确认采用 `bdd70edc153b6ed5def65ed99c41f325df45f066` 作为下一 R1C修复的候选基线。保留既有独立 PASS与历史记录，不回退、不变更任何Git历史，不合并main或push。请核对字节等价、记录基线交接，并生成最小 R1C开发合同；本次只做文档交接，不实现业务。

### Investigation / Baseline

主仓 `/Users/qianduoduo/Desktop/AI_app/ThesisGuard`。读取 main AGENTS、原 WP04-02 acceptance/repair program、R1B/R1/R2合同、独立 reverify PASS与本次反馈复核、冻结 Evidence合同相关章节和 current-valid/lifecycle/trusted代码及测试。

候选 `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`，branch `codex/wp04-02-evidence-domain-service`，HEAD `bdd70edc153b6ed5def65ed99c41f325df45f066`，parent `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`，初始状态 clean。

Expected source SHA：errors `3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec`；services `2f90167c131cf91c715fc7fb19ead5af9745fab3259c7af0c875474bb0ce444f`；tests `a8b5e8e814230b21d732f2e973a62cdd0b69d00455ea29130b1750994d8bed2a`。

### Top Blocking AC

1. 确认用户已明确采用新基线；fresh parent/两文件commit diff/clean status与三业务SHA正确，三verifier保持独立报告哈希。
2. 新交接报告明确“历史业务 PASS + 当前静态字节等价”，不宣称本轮又跑100/35测试，不改写原报告或追认未知历史Git操作授权。
3. 生成一项 `TASK-WP04-02-R1C-01` latest-first lifecycle eligibility修复合同，锁定bdd70ed，明确剩余状态表/trusted registry/R1D不在本切片完成范围。不得把三个独立风险边界一次性派成大任务。

### Scope / Must / Must Not

只允许新增主仓 docs/acceptance 中的 baseline-confirm acceptance及 R1C-01 task-contract。候选read-only，不能执行业务修复、pytest/DB连接或迁移、任意SQL、Git commit/merge/rebase/reset/checkout/push、修改source/verifier/原合同、修改canonical WP编号。

新 R1C-01 合同应仅允许 candidate services.py 与 tests/test_evidence_services.py 的后续授权修改，errors原样。先修当前函数把 UNREVIEWED/PENDING_REVIEW/DISPUTED当eligible的错误；读最高版本后按生命周期判断，不向前回退，保留exact历史查询/current查询语义。不得把改成 VERIFIED-only 等同全部 decision-use eligibility、source-grade/F restriction、freshness、trusted或 R1C整体完成。

合同必须包含：先复现red再最小修复；七个verification statuses、历史VERIFIED+最新不eligible、正常latest VERIFIED、missing series、exact历史可读、ordinary correction最新UNREVIEWED不能回退的真实PostgreSQL反例；无需状态迁移时可在真实fixture构造合法不可变版本，不能改生命周期写命令迁就测试。

下一业务合同 Required Acceptance为 L1/L2/L3/L4_DB，Full matrix，明确原 R1A/R1B/wiring verifiers、完整service与persistence/migration/research回归和静态命令、冻结 head 0004。数据库和 out-of-root worktree权限必须走正常机制；本次baseline确认不自动授予后续DB或Git权限。旧测试若与冻结eligibility矛盾，列出精确更正并证明red-to-green，不删/skip/弱化。

### Required Verification (This Docs-only Task)

```bash
git status --short --branch --untracked-files=all
git rev-parse HEAD HEAD^
git diff-tree --no-commit-id --name-status -r HEAD
git diff --check HEAD^ HEAD
shasum -a 256 backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py /tmp/test_wp04_02_r1b_r1_wiring_20260915.py /tmp/test_wp04_02_r1b_reverify.py /tmp/test_wp04_02_r1a_verifier.py
```

以上从候选运行，另核对主仓状态与新增文档内容/链接/whitespace。本任务不重跑历史业务套件，不要求撤回已提交内容来重建red。

### Stop Conditions / Evidence

未获明确新基线确认、任何HEAD/SHA/status不符、verifier缺失、合同无法明确最小范围或必须越界则 BLOCKED；不 silently rebaseline，不自改旧合同。记录实际用户确认来源、before/final状态、SHA、parent/file范围证据、历史与新证据区别、生成合同路径和prompt-quality检查。

## B. Governance Appendix

遵守 ai-task-governor：No Evidence No PASS，FAIL修复优先，task-size/prompt-quality gates、历史范围与权限不漂移。正式文档验收报告写 docs/acceptance；执行交接者仅报告 IMPLEMENTATION_COMPLETE/BLOCKED，不自行认定未来 R1C业务 PASS。

候选下一业务开发提示词是本任务产物，不在本任务开始实现；其后通过用户派发才进入业务执行。R1C-01通过不等于整个R1C或WP04-02通过。Sector Crowding仍为APPROVED — DEFERRED。
