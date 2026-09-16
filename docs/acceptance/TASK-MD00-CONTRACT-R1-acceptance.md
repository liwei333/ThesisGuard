# TASK-MD00-CONTRACT-R1 — 独立静态验收

**OVERALL: PASS**

本 PASS 只表示 MD-00 docs-only 合同收敛任务达到 `L1_STATIC_REVIEWED`。领域合同仍是 `CONTRACT_DRAFT / PROPOSED`，不是生产合同冻结、APPROVED ADR、业务实现、账号授权、策略验证或实施派发。Market Data 仍 `DESIGN_ONLY / NOT_IMPLEMENTED`，WP-04 仍 `PARTIALLY_IMPLEMENTED`，策略仍 `UNPROVEN`。

## Metadata

- Task ID: `TASK-MD00-CONTRACT-R1`
- Date / evidence cutoff: 2026-09-15，本次最终文件静态核对时点。
- Verifier: 独立 Reviewer `/root/review_md00_contract`；与领域合同执行者分离。
- Report path: `docs/acceptance/TASK-MD00-CONTRACT-R1-acceptance.md`，由不可变 task-contract 明确指定，沿用项目 `docs/acceptance/` 约定。
- Required Acceptance: `L1_STATIC_REVIEWED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`
- Missing Acceptance: 本任务 required tags 无缺失。`L2_BUILD_VERIFIED / L3_CONTRACT_VERIFIED / L4_RUNTIME_VERIFIED / L4_DB_VERIFIED / L4_BROWSER_VERIFIED` 均未取得，也不属本次要求，不能从本文继承。
- Repair Required: `NO`；首轮两项阻断发现已由执行者修订，Reviewer 复审最终文件后关闭。
- Implementation status: 文档已交付；业务实现未授权、未执行。

## Classification and gates

- Task Type: `DOCUMENTATION / ARCHITECTURE_CONTRACT_REVIEW`
- Risk Type: 决策关键时间、价格尺度、历史可见性、冻结规则和审计语义；本轮无 runtime change。
- Touched Layers: docs only。
- Task Size: `MEDIUM`
- Evidence Matrix Type: Compact，按 task-contract；至少三项高风险反例均作静态语义审查。
- Applicable Gates: G0 Baseline、G1 Scope、G2 Contract、G3 Architecture static、G6 Evidence、Independent Review。
- Not Applicable Gates: G4 业务测试、DB Persistence、G5 runtime regression、真实 Provider / API / UI / enqueue / 账号验证。未执行这些不构成本次文档任务缺项，后续实现合同必须重新要求相应证据。

## Final source identities

Reviewer 独立读取并计算 SHA-256；以下身份用于限定本次结论，不以执行者自述替代。

| Source | SHA-256 |
|---|---|
| `docs/MARKET_DATA_DOMAIN_CONTRACT.md`，最终211行 | `5bde4e1d6977a2d9dc13f43525fc9cb7a4320601e03cadd2ea6cdb4d1961708c` |
| `docs/acceptance/TASK-MD00-CONTRACT-R1-task-contract.md` | `43ee1ad80df413cd81595b4e1d97d9f76e57d9c3e85be2051dea6601fb472d00` |
| `docs/MARKET_DATA_TECHNICAL_PLAN.md` | `a5ec4873dc01e9a9e0c0053b4c2f51aba8477bfa75e9e7705fc94dcdc776a4e9` |
| `AGENTS.md` | `5244bc97ebe7939cc8fe15a49f060b8046b6d32b896c27dc631b7b59594bf476` |
| `/Users/qianduoduo/Desktop/AI_app/tradingModel/last/ThesisGuard_个人交易模型_v1.3_个人适配草案.md` | `6d8b6ca1307df0aece4a00b5d85716a9cbf1cf05d06b938e3d4efcc39e5a8905` |
| `/Users/qianduoduo/Desktop/AI_app/tradingModel/IterationRecord/个人交易系统_v1.1_基于ThesisGuard_v1.3.md` | `b80878a6e01777864a928440fb909e487c066917396a79dd7b78b28f5f4eb64b` |

同时核对了 `docs/ARCHITECTURE_REFERENCES.md`、产品目标决策、Capability Runtime 延后决策、Sector 延后决策及 WP-04 Evidence 合同相关生命周期原文。相邻 tradingModel 源只读，未切换到新的系统候选版本。

## Baseline and scope

基线 `/tmp/thesisguard-md00-baseline-20260915.json` 捕获时点为 `2026-09-15T10:40:39.611665+00:00`，包含214个既有 Git tracked / untracked 普通文件 SHA-256。Reviewer 逐文件重算，214个均存在且内容相同，未发现既有文件修改或删除。临时 JSON 是本次比对输入，永久核验结果记录于本文。

- local `HEAD` / cached `origin/main` 均保持 `7d3734bc8346c16f9bbf7f7d9806309949c996de`；本次没有 fetch / ls-remote 成功新证据，真实远程 live HEAD 为 `UNKNOWN`。
- 基线 tracked diff 空；验收时 `git diff --stat` 仍空，`git diff --check` exit 0。该 tracked 检查不能单独证明 untracked 新文档内容，故另做 hash / 文本 / 链接检查。
- 基线七份 untracked 文档全部保留且 hash 相同：技术预案及六份既有 Evidence 治理文件。本任务新增领域合同、task-contract、本文，共三份 docs。
- Reviewer 唯一写入为本文；未修改 task-contract、领域合同、AGENTS、权威索引、业务代码、测试、依赖、迁移或其他治理材料。未 commit / push / 创建 APPROVED ADR。

Evidence candidate 属其他并发任务，不能声称其内容完全未变。Reviewer 只读观察到：candidate HEAD 保持 `bdd70edc153b6ed5def65ed99c41f325df45f066`；根目录为 `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`。

| Candidate file | Baseline SHA-256 | Reviewer observed SHA-256 |
|---|---|---|
| `backend/evidence/services.py` | `cecffcd52371baf6bb6e85e733e565f4720e78d3d50fb65503b5d74998517df3` | `5419448d3b73c0c0e2c1144d7615cdbe399266be5b9dd70281d91cf1a485d632` |
| `tests/test_evidence_services.py` | `e6e59f9db6152c254592805bbbaf5f5dc3821a1bd3ab610cea2786869e4cae5a` | `fd2b4af2a06f23becb544ee30e676949d6ffc3f8c1a2380c44d4bc0c9637145a` |

这些是外部并发漂移观察，未由 MD-00 执行者或 Reviewer 写入；不将差异归因为本任务，也不在本文验收其业务正确性。AC-01 的标准是“不被本任务修改”，并非要求其他获授权任务停止工作。

## Top Blocking AC results

| AC | Result | Independent evidence / boundary |
|---|---|---|
| AC-01 Scope & baseline | PASS | 214既有文件独立hash比对无差异；Git refs/空tracked diff；新增仅三份约定docs；candidate漂移单独披露且不归因MD-00；真实远程UNKNOWN。 |
| AC-02 Contract precision | PASS | 最终合同§4第45–51行身份、日历与品种单位；§5 Quote/Bar/errors；§6第77–93行四类时间、knowledge发布与bar_start半开查询；§7 exact raw/adjusted转换；§8质量/覆盖/动作资格分轴；§10引用与留存。无silent fallback。 |
| AC-03 Frozen inputs | PASS | 模型v1.3 §4–6、系统v1.1 §3–5/§7–10原文对照最终合同§7–9第97–143行。双指数严格Close>MA60；Setup B极值择最近、边界包含、t+1、S0严格下方、Pmax≤1.01、20日金额0.5%、盘中触及、退出与保护窗口未改变。 |
| AC-04 Honest readiness | PASS | 第5/9/19行草案与证据边界；§12 OD-01…08列账号、覆盖、质量/冲突、finality、知识发布、PIT/换算、留存、正式批准关闭证据；§13/14不授权实施且限定官方资料局限。 |
| AC-05 Independent review | PASS | Reviewer独立读取完整合同与原文、Git/hash证据，首轮报告Issues Found，执行者修订后复审最终变更并固定合同hash，持久化本文；没有业务测试或自签执行者PASS。 |

## Semantic evidence and static counterexamples

下表均为**文档静态语义核对**，不是已经执行的业务测试，也不证明 Provider / DB / API 具备该行为。合同§11的 MD-T01…16 是未来实施验收要求。

| Risk / counterexample | Static result and evidence |
|---|---|
| 旧报价现在收到，伪新鲜 | §6保留source_time与kind；observed/received/commit不重置行情时点，source缺失或偏差不可解释为UNKNOWN；feed时点与last_trade_time分开。 |
| 未来补录因子/来源选择用于历史决策 | §6要求facts/revisions/factors/calendar/mapping/selection policy均knowledge_valid_from≤K且commit后发布；§7 PIT_UNSUPPORTED；摄取前历史只属事后replay，OD-05机制未关闭不承诺精确operational as-known。 |
| 查询09:30–10:00误截60m条 | §6谓词start≤bar_start<end，完整条覆盖(bar_start,bar_end]、显示end；不齐范围披露完整条或严格用途拒绝，K/finality另滤；三例与分页一致。 |
| 15秒间曾触及S0后反弹 | §8 coverage独立：采样点不能证明未触及；可靠range要完整覆盖所需区间且同尺度；已知触及交冻结域永久失效，延迟回补不覆盖旧快照。 |
| 今日QFQ直接作为委托 | §7须exact执行日raw转换，不能假设通用比例；固定tick严格下方公式与50.00→49.99 / 50.004→50.00原文一致。 |
| 新鲜行情被视为Evidence VERIFIED / ALLOW | §8独立时间、验证、结构/finality、coverage与用途资格；不扩充WP-04生命周期或从FRESH映射动作批准。 |
| 最后60有效行跳过停牌/缺日 | §9第141行登记日历连续60日；MA60(t)覆盖t−59…t，MA20(t−5)起点t−24，最早p=t−20参照量起点t−39，最早d=t−19的MA20起点t−38，均包含；不误需MA60(t−5)，不补零/跳日。 |
| 盈利保护启动日排除导致一日错位 | 修订后§9第138行区分启动日j与生效日k；首次k=j+1的窗j−4…j含启动日，之后k−5…k−1，生效日开盘前同尺度换算并保存；MD-T14登记该未来反例。 |
| 引用结果保留但因子/原始材料被清理 | §10直接/传递依赖均pin；不能仅留hash或会失效的第三方链接；授权不允许必要持久化则用途不得启用，30/180候选未批准不自动删除。 |
| SDK/官方手册证明账号可用 | §3/14与技术预案§7一致：iFind manual/FAQ上轮搜索索引可见但direct timeout，权限通用资料不证账号；AKShare MIT不证数据用途；没有本轮连源/账号调用，也未宣称coverage/finality/SLA实测。 |

## Gate verdicts

| Gate | Result | Reason |
|---|---|---|
| G0 Baseline | PASS | Git与214文件比对；远程UNKNOWN、candidate并发差异均明确。 |
| G1 Scope | PASS | 仅约定新docs；既有文件未改，Reviewer仅写本文。 |
| G2 Contract | PASS | 两项初审阻断已关闭，最终语义与冻结原文一致。 |
| G3 Architecture static | PASS | Provider/Gateway/确定性消费者/Agent/真相存储职责及状态轴独立；无自动交易、Agent提交事实或Evidence绕过。 |
| G6 Evidence | PASS | 精确文件与hash、独立静态推导、局限/OD登记，未将反例要求或官方资料当运行证据。 |
| Independent Review | PASS | 独立Reviewer实施读取、发现、复审与持久化。 |
| Runtime Test / DB / API / UI / Provider / business regression | NOT_APPLICABLE | 本任务无业务变更，未执行；不提供相应能力结论。 |

## Commands actually executed

实际执行范围：`cat` / `nl -ba` / `sed -n` / `rg -n`读取合同、规则、权威及相关skill；`git rev-parse HEAD origin/main`、`git status --short`、`git diff --stat`、`git diff --check`；candidate只读`git -C ... rev-parse HEAD`；Python标准库读取基线、逐文件SHA-256及候选文件hash、文档内相对链接存在性检查。最后通过`apply_patch`仅新增本文，并重读/核对最终hash与scope。

相对链接初检唯一不存在目标是待Reviewer创建的本验收文件；创建后应存在。没有重新浏览外部来源、调用账号、运行pytest/迁移/API/worker/前端测试，也没有提交或推送。

## Findings and next action

初审发现两项阻断：§4统一CNY/share误覆盖指数points；§9盈利保护共用k存在窗口错位解释。执行者修订§4/§9/MD-T14后，Reviewer复审关闭；**最终 Blocking Findings: NONE**。不附带新的生产参数或实现授权。

**Next Action:** 可交付用户审阅文档，并按OD登记继续明确拟实施用途、证据与正式批准。业务主线仍Evidence修复/独立复验→WP-04服务/API/exact references→WP-05→最小WP-RISK-01。不能仅凭本文PASS派发Provider、表、API、Agent、Sector或改变冻结交易政策；后续每个实现切片另立bounded task-contract并独立验收。
