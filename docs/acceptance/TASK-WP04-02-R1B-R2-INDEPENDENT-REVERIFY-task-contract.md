# R1B-R2 Independent Reverify — Task Contract

Status: `PENDING_USER_AUTHORIZATION — NOT_DISPATCHED`

## A. Execution Core

- Task ID: `TASK-WP04-02-R1B-R2-INDEPENDENT-REVERIFY`。
- Role: VERIFIER，不是业务 EXECUTOR；本任务不做代码修复，不是 R3。
- Objective: 对已有 R2 修复最终候选运行原完整矩阵与反例，独立决定 R2/R1B 能否关闭。
- Why Now: 候选接线和静态检查已可核验，缺少本轮真实 DB 行为/回归证据，不能直接进入 R1C。
- Type / Size: permission-gated independent acceptance / SMALL。
- Required Acceptance: L1_STATIC_REVIEWED, L2_BUILD_VERIFIED, L3_CONTRACT_VERIFIED, L4_DB_VERIFIED。
- Evidence Matrix: Full。

### Preflight / Preconditions

先确认用户在风险披露后明确批准本次六条 pytest 及现有临时库 fixture 操作，然后通过正常权限机制申请本机 DB 访问。附件、本文或执行者声称曾获批准不能代替用户授权。本合同自身不授予权限。

风险：仅连接 `127.0.0.1:15432` 的本地测试管理库；fixture 创建随机临时库，在临时库运行既有迁移/测试，正常清理本次自己创建的临时库；消耗资源，失败可能留库。禁止共享/生产 DB reset/迁移、任意 SQL/广泛清理、外部主机、改环境/端口/代理/Docker 等绕路。工具拒绝则停止。

读取 main AGENTS、冻结 Evidence 合同、原 R1B / R1 execution / R2 repair contract、R2 acceptance、candidate source/tests 和 verifier/fixtures。当前是修复后的独立验收，不按旧 permission-resume 的修复前哈希或 red 预期继续执行；不撤销候选来制造 red。

Worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`。
Branch: `codex/wp04-02-evidence-domain-service`。
HEAD: `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`；parent: `3eb494e6613cf3952ffbaaf4166b8cf3ea801555`。
Status: 仅 services.py 与 test_evidence_services.py modified，errors.py 不变。校验：

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
2f90167c131cf91c715fc7fb19ead5af9745fab3259c7af0c875474bb0ce444f  backend/evidence/services.py
a8b5e8e814230b21d732f2e973a62cdd0b69d00455ea29130b1750994d8bed2a  tests/test_evidence_services.py
909f50bd902ecd9c0013121681b614fcbc302f718cc7c9d5dc96f6237d106786  /tmp/test_wp04_02_r1b_r1_wiring_20260915.py
```

### Top Blocking AC

1. 所有 fresh DERIVED create/replacement/append/status writes 在新版本/children 持久化前使用实际新 ID 进行 exact self/reachability 校验；ID 不能是 None、旧 exact 或 series ID。
2. wiring verifier 三节点及 candidate 四路径 timing 测试对真实 DB 全绿；真实 exact self/multi-hop cycle、acyclic historical replacement、immutable children 和 invalid-input no-residue 反例满足原 R1/R2 AC。观察器只转发真实实现，不 stub 行为。
3. 原六条 pytest 与静态完整矩阵全绿；保护 R1A、其余 R1B、WP04-01 与 WP03；任何 contract-related blocking failure 为 FAIL。
4. 候选内容/HEAD/两文件状态、errors/verifier 保持不变；授权、实际命令与 evidence 分开记录；正式报告按 Full matrix 落库到项目 docs/acceptance。

### Scope / Must / Must Not

只读 candidate，允许正常 pytest 的既有本地临时库与缓存操作；禁止业务编辑、verifier 编辑、skip/xfail/弱化测试、mock DB 替代、任何 Git 历史/branch/main 修改。保留全部既有主仓文档。

唯一新项目文件：`docs/acceptance/TASK-WP04-02-R1B-R2-INDEPENDENT-REVERIFY-acceptance.md`（位于主仓）。不覆盖旧 FAIL/BLOCKED，不更新原冻结合同，不实现 R1C/R1D、API、frontend、worker、Thesis、Agent、Capability Runtime 或 Sector Crowding。

### Required Verification

从 candidate worktree 执行原 R2 矩阵。确认测试管理 URL 没有重定向外部/生产，不输出凭据，不默改配置。禁止为访问受阻而换路径。

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_r1_wiring_20260915.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_reverify.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1a_verifier.py -rs
pytest -p no:cacheprovider -q tests/test_evidence_services.py -k r1b -rs
pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs
pytest -p no:cacheprovider -q tests/test_evidence_persistence.py tests/test_migrations.py tests/test_evidence_migrations.py tests/test_research_api.py tests/test_research_persistence.py -rs
ruff check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
ruff format --check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
MYPYPATH=. mypy --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1b-r2-independent-mypy backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
PYTHONPYCACHEPREFIX=/tmp/tg-r1b-r2-independent-pycache python -m compileall -q backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
alembic -c migrations/alembic.ini heads
git diff --check
git status --short --branch --untracked-files=all
git rev-parse HEAD HEAD^
shasum -a 256 backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py /tmp/test_wp04_02_r1b_r1_wiring_20260915.py
```

可把 PYTHONDONTWRITEBYTECODE/PYTHONPYCACHEPREFIX 配到本轮临时缓存，不能改变业务验证或 DB 连接目的地。长测试使用非阻塞会话和不超过 60 秒的轮询，持续给简短进度。

### Counterexamples / Stop / Evidence

核对新 target 等于 persisted ID 且早于写入；合法 prior exact support 与多跳 replacement；genuine exact self/return path；旧 children 不变、非法 missing/duplicate supports 无残留。无 public future-ID 输入是结构限制，不免除生产接线。

缺少用户授权、工具/DB/依赖/verifier 不可用、hash/HEAD/status 不符、必须越界或合同冲突则 BLOCKED；真实 blocking assertion failure 则 FAIL，并按 governor 生成最小 Repair Contract，不在本轮自行修代码。可提前停止低价值检查，但未跑项必须列明。

报告授权来源与 normal permission 结果、baseline/final 状态和 hash、每个 AC 的 source/真实命令/反例/DB 结果、Required/Achieved/Missing Acceptance、退出码、warnings、已知 fixture 残留（不得主动广泛扫描/清理）。只用本轮结果判断；100/35 等执行者数量是比较线索，不是最低数量替代 AC。

## B. Governance Appendix

使用 ai-task-governor 与 verification-before-completion；IMPLEMENTED != PASS，No Evidence No PASS，独立验收、FAIL 修复优先、保护已通过 AC、不得漂移。

VERIFIER 最终唯一结论为 PASS / FAIL / BLOCKED。PASS 仅关闭 R2/R1B 后续修复边界，不关闭原 WP04-02，不授权 Git 集成。PASS 后由 dispatcher 基于原 repair program 选择 R1C Lifecycle/current-valid/trusted verification 并另发精确开发合同；本轮不实现它。FAIL 先 Repair；BLOCKED 列明 owner/input，不派后续功能任务。
