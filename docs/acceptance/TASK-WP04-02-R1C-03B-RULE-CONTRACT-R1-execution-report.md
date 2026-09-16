# TASK-WP04-02-R1C-03B-RULE-CONTRACT-R1 execution report

STATUS: **IMPLEMENTATION_COMPLETE**。

Role: 规则规格编排 EXECUTOR。Date: 2026-09-16，Asia/Shanghai。此状态只表示获准的只读调查及两文档交付完成，不是独立验收或规则批准。

## 交付结论

[规则调查草案](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-03B-rule-definition-draft.md) 状态为 PROPOSED / NOT_APPROVED，readiness 为 **NOT_READY**。仅保留一个调查 ID `tg.tc.display-title-ascii-tail.v1`，考虑删除 display_title 尾 U+0020 空格；没有可执行的生产正向谓词。四路径当前新 trusted 请求均拒绝；未来只可能讨论 same-series，automatic/direct/underlying create 不泛化授权。

已有 ORM/服务可保存字段和 exact provenance/locator/source metadata，但不持有经此次调查认证的原文、对象字节或 parser artifact 语义证明。服务没有读取对象并独立验证事实语义的步骤；fixture 的声明 hash/object key/VERIFIED 与 legacy seed 不能补足证据。逐字段一致只能证明复制了同一已提交命题，不能证明旧命题正确。因此暂不派发正向实现，不以 LLM、actor、extractor/version、hash 或 SourceGrade 判断可信。

草案包含所有 EvidenceVersion 列、十维 series identity、source/locator/instrument/support/关系字段的权威来源、约束、失败行为和例子，列出9个具体反例。后续计划提供 ordinary/review 正向对照、附条件的 trusted positive、malformed/field/title/source/prior/四路径 negative、caller commit/fresh-session 全行无残留、legacy exact/history/immutable children/replay 和完整既有验证矩阵。当前不存在可运行 trusted positive；计划没有被当成真实 PostgreSQL 执行证据。

## 固定基线与 scope 快照

开始与最终要求的固定位置：

```text
candidate: /Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service
branch: codex/wp04-02-evidence-domain-service
HEAD: 0cef44fd2ffd929b40e849e607af0bd4c44d14d2
parent: bdd70edc153b6ed5def65ed99c41f325df45f066
status: clean
main: /Users/qianduoduo/Desktop/AI_app/ThesisGuard
branch: main
HEAD: 438738c543e4cae3e805d31324b068c1cd5c7059
parent: 7d3734bc8346c16f9bbf7f7d9806309949c996de
tracked/index diff: empty
```

候选三个固定 SHA-256 已在开始检查中匹配：

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
43b548232df4267f377c5e144222c9278c3cc478f6800720240c4618b689ebe3  backend/evidence/services.py
47ff645c0f782af67e9f6ee64520105febdb28c6547a43bf89b435bead6c5108  tests/test_evidence_services.py
```

main 起点实际16条未跟踪路径全部保留，精确如下；ignored 的旧日志也纳入保护文件枚举，不能仅靠 status 断言它们未变：

```text
docs/acceptance/TASK-WP04-02-R1C-03A-ORACLE-R1-acceptance.md
docs/acceptance/TASK-WP04-02-R1C-03A-ORACLE-R1-execution-report.md
docs/acceptance/TASK-WP04-02-R1C-03A-ORACLE-R1-repair-contract.md
docs/acceptance/TASK-WP04-02-R1C-03A-VERIFY-PREREQUISITES-R1-acceptance.md
docs/acceptance/TASK-WP04-02-R1C-03B-RULE-CONTRACT-R1-task-contract.md
docs/acceptance/verifiers/TASK-WP04-02-R1C-03A-ORACLE-R1-evidence/after-manifest.json
docs/acceptance/verifiers/TASK-WP04-02-R1C-03A-ORACLE-R1-evidence/before-manifest.json
docs/acceptance/verifiers/TASK-WP04-02-R1C-03A-ORACLE-R1-evidence/commands-manifest.json
docs/acceptance/verifiers/TASK-WP04-02-R1C-03A-ORACLE-R1-evidence/evidence-manifest.json
docs/acceptance/verifiers/TASK-WP04-02-R1C-03A-ORACLE-R1-evidence/execution-source-manifest.json
docs/acceptance/verifiers/TASK-WP04-02-R1C-03A-ORACLE-R1-evidence/oracle-reasoning-manifest.json
docs/acceptance/verifiers/TASK-WP04-02-R1C-03A-ORACLE-R1-evidence/persistence-proof-manifest.json
docs/acceptance/verifiers/TASK-WP04-02-R1C-03A-ORACLE-R1-evidence/results-manifest.json
docs/acceptance/verifiers/TASK-WP04-02-R1C-03A-ORACLE-R1-evidence/scenario-preservation-manifest.json
docs/acceptance/verifiers/TASK-WP04-02-R1C-03A-ORACLE-R1-evidence/whitespace-manifest.json
docs/acceptance/verifiers/test_wp04_02_r1c03a_boundary_oracle_r1_20260916.py
```

新建文件只有本 execution report 和 rule-definition-draft。没有生成第三份日志/manifest/测试文件；检查结果嵌入本报告，起点完整文件 hash map 在本次会话工具存储中。main 最终应为上述16条加两条授权新文档，共18条 untracked；候选仍0条改变，两个工作树的 HEAD/parent/branch 与 tracked/index diff 不变。下方最终实测块记录写入后实际核验结果。

## 已读资料与保护 hash

完整阅读 AGENTS、新派发合同、ORACLE-R1 acceptance/execution report、原 R1C-03A 合同及原实现执行反馈、R1 repair program、冻结 Evidence 合同；另读原 acceptance/prerequisite execution report，调查 candidate models/repositories/errors、create/revise/replacement/private append/provenance/locator/support/current/review helpers 和 correction/review/legacy/replay tests。实际代码依据来自 candidate，治理依据来自 main。

原 R1C-03A 执行报告不是仓内命名的 `TASK-WP04-02-R1C-03A-execution-report.md`。原 acceptance 给出输入附件路径；据此完整读取权威原反馈 [pasted-text.txt](/Users/qianduoduo/.codex/attachments/5f39c044-4806-4bfe-8c98-02fec3f384e2/pasted-text.txt)，SHA256=d5450b8cee6ececb83a043a12b840aaaae1f2847b29a24866230716b24a4b8e2。未重写或复制它。其原业务 RED/GREEN 属于 source-reported 历史，不重新宣称本轮取得业务 RED/GREEN。

| 保护文件（main，除注明 candidate） | 开始 SHA-256 |
| --- | --- |
| AGENTS.md | 5244bc97ebe7939cc8fe15a49f060b8046b6d32b896c27dc631b7b59594bf476 |
| docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md | b179ecc6ea60ffed75f7179a2d36e47ad2b55153f6d4fa62b8be7e4926fd1288 |
| docs/acceptance/TASK-WP04-02-R1-repair-contract.md | ada1a14bc4f6def541c530e82e5431b011bf954abbd1012d81fcbeaf5f35dd3f |
| docs/acceptance/TASK-WP04-02-R1C-03A-task-contract.md | 8beae6b565e6f932ed29554ea97ab232863be12fe57e24a198d0d141451e753a |
| docs/acceptance/TASK-WP04-02-R1C-03A-acceptance.md | dada1892a0198f2a8698e0dee65b8c89f958b0350bdd482384831fab2d3bbc55 |
| docs/acceptance/TASK-WP04-02-R1C-03A-ORACLE-R1-acceptance.md | b761f6643f6070597007a7ff52277583e589566ce10b31723d7269240c3acade |
| docs/acceptance/TASK-WP04-02-R1C-03A-ORACLE-R1-execution-report.md | 54370888f03498b073d6df8835c9260e1c88fdc60b1b18e66ad83fbc14d401f1 |
| docs/acceptance/TASK-WP04-02-R1C-03A-VERIFY-PREREQUISITES-R1-execution-report.md | 70da4ccee05df6e050013a829e8aef012d374691a884997a2d42d5fafab4503e |
| docs/acceptance/TASK-WP04-02-R1C-03B-RULE-CONTRACT-R1-task-contract.md | 004593dd3cebc0197aa056e32c983fa4785cc5633953fb1e087091aa56a31e1a |
| candidate backend/evidence/models.py | 95b20c15ca2ff60059165b76ba8a93eae3e5e3dd631b03a57dea1a2507278597 |
| candidate backend/evidence/repositories.py | c043abb0b8c0f4872b7802558bc3815ad40d951206ef3a448ffd19afaad39f01 |

此外按旧 ORACLE before-manifest 的 `immutable_sha256` 逐一重新读取82个 protected 路径并匹配，未只相信 manifest 自报结果。五份原 verifier 的 /tmp 原件及 durable copies、旧补充 verifier、旧失败日志和 recovery/evidence manifests 均包含其中。整个 main 保护集合为341个文件，candidate 为184个文件：`git ls-files` 与 `git ls-files --others --exclude-standard` 的并集，再加入 docs/acceptance 递归全部文件（含 ignored logs）。已有对象保护哈希不得变化；两份新增文档单独核验。

| 特别保护的历史对象 | 开始 SHA-256 |
| --- | --- |
| /tmp/test_wp04_02_r1b_r1_wiring_20260915.py | 909f50bd902ecd9c0013121681b614fcbc302f718cc7c9d5dc96f6237d106786 |
| /tmp/test_wp04_02_r1b_reverify.py | 0f7cea4d14735bd165b75d756444259a64483a97e6a338227bc09af806490cc9 |
| /tmp/test_wp04_02_r1a_verifier.py | 66be45f354d1df34370eedd9811b3bc68cf29852d45027ea576a67975b18ddfe |
| /tmp/test_wp04_02_r1c_01_independent_20260915.py | 857914f073c552be98f895a456d2f0ec486452e1c9aed06a87176c6e7fefd48a |
| /tmp/test_wp04_02_r1c_02_independent_20260915.py | 64162c0aafc3ad620ee0cab5e4d8d0ed10e6d61ab8dc21322f4364144c442a05 |
| old supplemental verifier | 6d3592f86d13ca5e66988a5522542d52cf630ab3ebc0a51121bd786e401b0b89 |
| old owned-boundary.log | 030b6fba4e6e7d12ddbaee183f45f5be108c1effe333e05b9f2acb93ac9e95d0 |
| old evidence-file-manifest.json | 15e57d836f05cfefaf59508f50d79db7aaa8cee591d138d28ce2062c66e033e2 |
| old recovery-manifest.json | 964fd4047704839aa20fc45a9a7911c3712e61f4f723a22aa17f6c08369d9769 |
| ORACLE before-manifest.json | a843c3c988ee05a6dba01d98a2056b5300b3f9b15c2af2434b455989fd270881 |
| ORACLE evidence-manifest.json | 976d1fa24a92fe40180fd7ff7582a29ebb5450bced74c1127c93c82fed9370d5 |
| ORACLE verifier | 0ae19f9103b328afc3f7b5b017390569ead2a5239f18765d8c82f369d8818b0b |

## 实际只读命令与静态证据

两个 cwd 分别为上述 main/candidate。首轮实际执行以下命令；最终重新逐命令获取 exit/output，见最终实测块。没有调用会启动 DB fixture 的 Python 模块。

```bash
git status --short --branch --untracked-files=all
git rev-parse HEAD HEAD^
git diff --name-only
git diff --cached --name-only
git diff --check
```

candidate 另外执行 `shasum -a 256 backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py`。保护枚举另用 `git branch --show-current`、`git ls-files`、`git ls-files --others --exclude-standard` 与 Python pathlib/hashlib/json/AST；不 import 生产 service/fixture。

| 实际操作 | 实际结果 / exit |
| --- | --- |
| 首轮 candidate Git + 三文件 shasum | 固定 branch/HEAD/parent/clean/hash 匹配，diff/cached/check 无输出；0 |
| 首轮 main Git | 固定 main/parent，16个已有 untracked；tracked/index/check 无输出；0 |
| Python 起点文件枚举与 SHA256 | 341 main +184 candidate，两个目标不存在；JSON snapshot 存会话内；0 |
| `cat AGENTS.md`、派发合同、acceptance、repair program、原合同、ORACLE execution report；冻结全文用 cat/sed 分段读取 | 权威文件已读；不运行历史命令。部分合并输出截断后对缺失段再次读取；0（下述路径定位诊断另列） |
| candidate 的 nl/sed/rg models/repositories/errors/services/tests | 实际参数、字段、helpers/fixtures/边界断言已调查；0 |
| Python 读取 ORACLE before-manifest 并重验82 protected SHA，AST 枚举 ORM 字段 | 82项匹配，完整 EvidenceVersion/Source/child 列与草案矩阵核对；0 |
| 原报告附件 cat | 完整原执行反馈可读，原报告出处/hash 已解析；0 |
| 仅 draft 写入后再次 Python 枚举 hash/scope | 所有525既有文件不变；仅 draft 新增，candidate clean；0 |
| Python draft UTF8/whitespace/必需段落存在检查 | 39992 bytes、272 lines，无行尾 space/tab，无 CR，LF final newline；0 |

两次只读路径定位诊断如实披露：尝试一个并不存在的仓内原执行报告名，cat 提示 No such file（同批其他读取成功，shell 最终0），随后按原 acceptance 中明确的附件出处读取完整原件；一次从 main 对 services.py 做 rg 时该文件不存在，rg exit2，原 acceptance 路径检索无匹配的批次最终 exit1。实际服务调查前后均在 candidate 正确路径完成；这些不是 governing 原件不可访问、代码漂移或测试 RED，不以它们作为业务验证结果。

本任务没有运行 pytest/DB/SQL/migration/Alembic/Docker/MinIO/parser/LLM、Ruff/mypy/compileall 或安装升级命令。L2/L3/L4 和正向 trusted 验证均非本轮成果；后续矩阵仅是计划。未执行 commit/merge/rebase/reset/checkout/push/Git integration，未变更 registry/API。

## Compact AC evidence / 规格自检

| AC | 交付证据 | 边界与未完成项 |
| --- | --- | --- |
| AC1 默认拒绝/保护范围 | 开始固定 baseline/SHA、旧82 hash匹配、525文件保护、两文档 scope、最终实测 | production approved set 仍空；独立 verifier 尚未验收本规格 |
| AC2 至多一个规则候选及完整边界 | draft §§2–5 的唯一调查 ID、exact 字段/四路径/状态/audit/semantic proof | G1–G4 未完整，不能生成可启用成功谓词；结论 NOT_READY |
| AC3 字段来源/约束/失败/例子 | draft §4 全字段矩阵与缺失原文/object/parser evidence 列示 | ORM 存在与真实原文可读/认证明确区分；source_quote 不是模型列 |
| AC4 反例与未来PG计划 | draft §§6–7，9反例、P0/P1/P2/N1–N6/H1/R1、caller commit/fresh reader | 无本轮DB执行；trusted positive 严格附条件，ordinary/import/R1D 分离 |
| AC5 两产物、scope/whitespace/hash/审批提示 | draft §8 的用户决策与条件提示词、本报告最终实测 | docs approval 不等于 policy/activation 或实现派发 |

采用 ai-task-governor 控制 EXECUTOR / docs-only SMALL / L1 compact 范围，未自行改变 AC/DoD。采用 ai-task-prompt-architect 检查后续提示词：单一目标、明确证据输入与未来固定基线、狭窄路径/文件边界、真实 RED/GREEN/独立验证、G2 缺失或越界就 BLOCKED。后续提示词嵌入 draft，不生成第三份合同。规格自检是执行者检查，不是独立验收 PASS。

## 待审批与剩余边界

用户需决定标题整理是否有价值，以及 G1 标题语义、窄 scope/prior/路径/G3 拒绝资格；G2 须提供可独立重验的原文/对象/locator/语义对应谓词和证据所有权。完整定稿后才审批规则版本及何时启用，并由 dispatcher 另发小切片实现合同。推荐当前保持 NOT_READY 和空生产批准集合；若无价值，不制造成功路径。

生产 approved rule 集合为空。正向 trusted registry/validator、initial import 资格、ordinary correction 完整资格表、R1D、最终 WP04-02 独立全量验收仍未完成。此交付不宣布全 R1C/WP04-02 完成、不进入 R1D/API/Agent、不授权 Git integration；完成后等待独立规格验收和单独用户政策审批。

## 最终实测结果

下列嵌入结果由两文档写入后的只读检查追加；不生成独立日志/manifest。execution report 自身最终 SHA 在最终回复提供，避免把自身 hash 写入自身形成循环。

两份文档写入后，实际独立逐命令 subprocess 返回如下；stdout/stderr 实际取值已检查，非仅观察组合 shell 的最后退出码：

| cwd | 实际命令 | Exit | 实际输出 |
| --- | --- | --- | --- |
| main | git status --short --branch --untracked-files=all | 0 | main...origin/main，起点16条原路径加两份新文档，共18条 untracked |
| main | git rev-parse HEAD HEAD^ | 0 | 438738c543e4cae3e805d31324b068c1cd5c7059 / 7d3734bc8346c16f9bbf7f7d9806309949c996de |
| main | git diff --name-only | 0 | 空 |
| main | git diff --cached --name-only | 0 | 空 |
| main | git diff --check | 0 | 空 |
| candidate | git status --short --branch --untracked-files=all | 0 | codex/wp04-02-evidence-domain-service...origin/codex/wp04-02-evidence-domain-service，仅 branch header、clean |
| candidate | git rev-parse HEAD HEAD^ | 0 | 0cef44fd2ffd929b40e849e607af0bd4c44d14d2 / bdd70edc153b6ed5def65ed99c41f325df45f066 |
| candidate | git diff --name-only | 0 | 空 |
| candidate | git diff --cached --name-only | 0 | 空 |
| candidate | git diff --check | 0 | 空 |
| candidate | shasum -a 256 backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py | 0 | 三个 SHA 与本报告开始固定值逐一相同 |

Python 只读核验 exit0：起点 main 的341个文件与 candidate 的184个文件逐路径 SHA 全相同，没有丢失或改变；main 新增恰好两份允许文档，最终枚举343个，candidate 仍184个且无新增；branch/HEAD/parent 相同。再次重验旧 manifest 的82 protected 路径和原报告附件 SHA 全匹配。旧 frozen/contracts/reports/verifiers/logs/manifests 未变。

两个新文档均从实际 bytes 检查 UTF8、无 CR、无行尾 space/tab、final LF，并核验本地文件链接目标存在。draft 为39992 bytes、272 lines、SHA256=546db6d21ff450186d5bdf206a158141f81aa9e6ac394c7aca522a113156d193。report 追加此结果后再执行同样的 whitespace/hash 与 protection/scope 检查，其最终 bytes/lines/SHA 在工具结果及最终回复提供。本报告不会把自身写入前的 hash 冒充最终 hash。
