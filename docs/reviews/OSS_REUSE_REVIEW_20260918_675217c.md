# ThesisGuard 开源复用与开发减负专项评审

评审日期：2026-09-18；执行者：Codex；模式：AUDIT ONLY / QUESTION_DIRECTED。以下选型和任务删减均为 PROPOSED，不修改当前有效规则或工作包授权。

## A. 一页结论

**需要调整后续开发实现方式：通用解析、PDF 渲染和基础 UI 优先复用；已经采用的基础设施保留；Evidence/Thesis/Risk 的确定性领域语义继续自主实现。当前不建议立即更换技术栈或安装新组件。**

当前编码减负的第一步是使用已有候选实现和已有验证工具继续收口 Evidence，避免因旧状态文档重复开发。开源组件不能代替当前事务、不可变版本、审计与状态准入问题的独立验证。

三项最高价值的后续复用方向：

| 顺序 | 方向 | 结论 | 具体减少的工作 | 进入条件 |
|---|---|---|---|---|
| 1 | Naive UI 基础组件 | ADOPT_LATER | 新页面的表单控件、校验展示、表格排序/分页、弹窗、交互状态等通用实现；不翻修现有整站 | WP-06/风险 UI 的一个真实切片开始时，先验证局部组件、主题、键盘与移动布局 |
| 2 | Docling 的最小 PDF 解析配置，与轻量方案比较 | SPIKE_REQUIRED | PDF 字符/页码/布局底层读取；表格识别通过代表性样本后再缩小对应自研范围 | 解析成为真实任务且 Evidence source/version/locator 边界稳定；先隔离样本验证 |
| 3 | PDF.js 原文查看 | ADOPT_LATER | PDF 页面绘制、字体/缩放/旋转/文本层的底层实现 | 真实文件读取/权限接口及 source version/locator 可用；明确解决 Node 与浏览器兼容 |

这是工程净收益判断，不是已证明的节省工时。UI 的长期净收益有较强任务匹配；复杂中文表格解析的净收益和精度尚待实测；PDF 查看应先比较浏览器内置预览，仅跳页足够时不提前实现精确高亮。

现在保留 Compose、SQLAlchemy/Alembic、Dramatiq、boto3/MinIO 及已存在的 API 生成链路。Testcontainers、Schemathesis、Hey API 不用来替换当前 Evidence 验收。PydanticAI、LlamaIndex、Langfuse、完整交易 Agent/RAG 系统维持延期或仅参考。

唯一下一步建议：**在执行者固定完整最终交付后，独立审查已有 R4 verifier harness，保留 Evidence candidate，不从零重写 runner，不在本轮运行真实 DB。** R4 目前有在途未提交变化，不能把执行报告当作独立验收 PASS。

## B. 基线与真实能力地图

### B1. Git 快照

- 主仓：`/Users/qianduoduo/Desktop/AI_app/ThesisGuard`；remote 为 `https://github.com/liwei333/ThesisGuard.git`。
- 主线：`main@675217c3a15c0f416aa4462ca6edc491bf99f9f6`；本轮入口 status clean。
- `git ls-remote --symref origin HEAD` 实际成功：默认分支 `main`，远程 HEAD 与上述主线相同。本轮未 fetch/pull/rebase。
- 报告分支：`codex/review-oss-reuse-20260918-675217c`，从上述主线创建。
- 报告 worktree：`/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-review-oss-reuse-20260918-675217c`。
- Evidence candidate：`codex/wp04-02-evidence-domain-service@e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4`，本轮只读观察为 clean。该观察不是新的用户验收基线批准。
- R4 verifier：`codex/wp04-02-verifier-harness-r4@df836cb`，工作区存在原 `tests/` tracked 删除、`tg_verifier_tests/` 副本及 `evidence/` 等未跟踪内容。这里只记录在途状态，不清理、不搬运、不判断操作作者或授权。
- 其他已列出 worktree：WP04-01 readiness、Evidence contract、Evidence persistence；本轮未深入其业务内容。

AGENTS.md/架构文档中的 2026-09-14 状态是历史定位信息；本次报告按上述分支分别分析，不能据旧快照再实现已有 candidate 服务。

### B2. 能力与证据

| 能力 | 主线静态实现状态 | 候选/验证边界 | 减负含义 |
|---|---|---|---|
| Instrument/Watchlist | PARTIALLY_IMPLEMENTED：服务/API、内置目录及 Watchlist 页面存在 | 本轮没有运行相应业务测试；内置目录不是全市场主数据 | 保留既有实现，不换整站模板 |
| Research Package | IMPLEMENTED，限版本化服务/API/持久化容器 | 内容摄取/生成不因容器存在而完成；本轮未复验领域行为 | 沿用版本与错误契约，不让框架接管 |
| Evidence 来源/版本/locator | PARTIALLY_IMPLEMENTED：ORM/repository/migration 0004 在主线 | candidate 有 domain service；状态/回放逻辑存在，不等于已验收或已集成 | 不重写 candidate，不另建证据库 |
| Evidence 真实导入/解析/提取 | PLANNED；没有主线 parser/extractor pipeline | 合同有 manual/automatic provenance、parser metadata、locator 要求 | 手动结构化录入和原文件绑定可作为既有合同支持的先行路径；自动化解析另拆最小任务 |
| 原文查看/高亮 | PLANNED；没有 PDF viewer | ORM 已有 locator payload，业务查看链路尚缺 | 复用渲染；跳页先行，坐标映射自己控制 |
| Thesis/Risk | DESIGN_ONLY/PLANNED；相关目录主要为占位 | 本轮未评估冻结策略盈利能力，策略仍 UNPROVEN | 不能套外部交易 Agent 的策略替代 |
| UI 基础组件 | PARTIALLY_IMPLEMENTED：页面用原生控件与 scoped CSS | 无已引入的通用 UI 库；StockDetail 使用 Mock 价格/健康度 | 新切片可用一个组件库，现有简单页面不批量迁移 |
| API 客户端 | IMPLEMENTED：固定 codegen、Axios adapter、生成补丁、漂移检查 | 本轮 typecheck PASS；drift check FAIL，原因仅三个 schema description 差异 | 当前同步产物是小修；长期迁移要单独比较成本 |
| PostgreSQL 测试 | IMPLEMENTED，限测试代码与隔离库机制 | 主线 Research/Evidence/migration fixtures 有重复生命周期逻辑；candidate 有更严格 helper。历史 fixture 独立 PASS 只限其 scope | 后续新测试优先复用适用且已验收 helper；不在本次推广或改旧 fixtures |
| Worker/对象存储 | PARTIALLY_IMPLEMENTED：RedisBroker、health/echo actors；同步 boto3 storage wrapper | 不证明 Evidence enqueue/consume、immutable object writes 或安全失败处理已完成 | 复用封装和队列，补领域 actor/错误处理；不另起 Celery/新存储系统 |
| 检索/Agent | PLANNED/DESIGN_ONLY；无完整调用/索引服务 | Capability Runtime 明确延期，pgvector extension 不等于检索实现 | 不提前上框架、平台与多模型路由 |
| 行情/图表 | CONTRACT_ONLY/PLANNED；Market Data 有静态合同和待关闭项，无生产 provider/K 线 | iFind/AKShare 候选、账号/覆盖/PIT/授权未因此通过 | 完整图表不是最小风险闭环前置；不让 AKShare 自动获准生产用途 |

证据级别：源码与配置为 L1；本轮 typecheck 为 L2，生成漂移比较为实际工程检查。历史报告是带分支/时点/scope 的记录，本轮没有独立复跑其 DB 或业务断言。未审计完整账号鉴权、多租户、生产部署与数据源运行，不能推断它们不存在或已就绪。

当前主线所保留的 R3 focused DB 报告为 BLOCKED：收集解析失败，真实业务测试运行 0。R4 报告虽然路径含 acceptance，正文身份是 zcode 执行报告，状态 READY_FOR_INDEPENDENT_REVIEW；其 21 自测与 41 collection 是交付声明，本轮未独立复验。

## C. 开源组件决策矩阵

官方身份在 2026-09-18 核验。非深入候选不强行锁版本。ADOPT_LATER 不表示许可、兼容和运行均已验收。

| 候选 | 核验版本/状态 | 结论 | 避免工作与增量成本 | 主要条件/置信度 |
|---|---|---|---|---|
| Naive UI | npm 发布 `2.45.3`；MIT 元数据；Node>=20、Vue ^3.0.0 | ADOPT_LATER | 少写通用交互；主题/业务状态/组件测试仍需写；无需后台新服务 | 包级条件与声明版本匹配，完整锁文件/发布包 NOTICE 与实际构建未验证；中高 |
| Docling | release `v2.128.0`；`docling` 默认引用 `docling-slim[standard]` | SPIKE_REQUIRED | 少写 PDF 底层与候选表格算法；映射、质量、安全、模型资源增加工作 | 不直接装全功能包；中文复杂表格/传递依赖/模型许可未知；中 |
| PDF.js | release/npm `6.3.289`；发布包 Node>=22.13.0或>=24；Apache-2.0 | ADOPT_LATER | 少写渲染/文字层；文件获取、版本/坐标、权限自己写 | 项目 Docker Node20不满足该发布包 engines；不能把上游源码构建 engines 当成消费包要求；中 |
| Trafilatura | 官方仓库已核验，未锁版本；现行 Apache-2.0，1.8.0前为GPLv3+ | ADOPT_LATER | 网页正文/元数据规则；保留抓取、SSRF、原始HTML、真实时间核验 | 网页导入尚非当前主线任务；不能把其下载功能当安全抓取边界；中 |
| Testcontainers Python | 官方仓库已核验，未深查版本 | KEEP_EXISTING | 可管理 Docker 生命周期；当前已有 Compose/隔离库/helper，加入后仍需迁移与领域断言 | 新 CI 拓扑/不可重复环境出现时再比较；中高 |
| Schemathesis | 官方仓库已核验，未锁版本 | ADOPT_LATER | 可扩展非法输入/契约测试；不能替代不可变、事务、并发、权限断言 | WP04-03 API稳定后，隔离且无外部副作用的小测试集；中 |
| Hey API | 实际仓库 `hey-api/hey-api`；npm `@hey-api/openapi-ts@0.99.0`；MIT | SPIKE_REQUIRED | 可能去掉生成后字符串补丁及部分手写 error glue；同时迁移调用/类型/测试 | Node>=22.18.0、TS>=5.5.3；当前 Docker20、TS声明^5.4.0，实际锁定版需检查；不保证补丁全部可取消；中 |
| KLineChart | 官方仓库已核验，未锁版本 | ADOPT_LATER | 坐标轴、缩放、交互绘图；行情质量/PIT/权威指标仍自控 | Market Data批准与可靠输入先行；中 |
| PydanticAI | 官方仓库已核验，未深查版本 | ADOPT_LATER | 将来可能减少模型调用/结构化返回/工具循环胶水 | 服从 Runtime延期，先比较单SDK；低至中 |
| LlamaIndex | 官方仓库已核验，未深查版本 | ADOPT_LATER | 将来可能减少索引/检索胶水；引用、时点、过滤、权限不被替代 | SQL/pgvector最小路径不够时再选；低至中 |
| Langfuse | 官方仓库已核验，未深查版本 | ADOPT_LATER | 模型追踪/评估UI；新服务、日志敏感性与运维增加 | 无真实模型调用，当前结构化日志先行；低至中 |
| AKShare | 官方仓库已核验，未锁版本 | ADOPT_LATER | 研究行情接口适配；质量、账号/数据用途、coverage/PIT仍需做 | Market Data合同OD按实际用途关闭；中 |

整体项目对照：WyckoffTradingAgent、TradingAgents、RAGFlow 和 full-stack-fastapi-template 均为 REFERENCE_ONLY。本轮核验官方身份，没有全源码/许可传递审计。前者 README 显示 React/Supabase 和 AGPL-3.0 标识；FastAPI template 使用 React/SQLModel。与当前 Vue/SQLAlchemy 领域实现的整体迁移没有可证明净收益。交易 Agent 的分析/交易流程与冻结规则不等价，RAG 系统不能替代 Evidence 域。

## D. 重点接入与任务删减

### D1. UI：新页面采用基础组件，现有页面保留

真实位置：`apps/web/src/views/WatchlistView.vue` 的输入/按钮/分类标签，Settings/Dashboard 的原生控件及各页 scoped CSS；依赖只有 Vue/Pinia/router/Axios，尚无通用组件库。新增 Research/Evidence/风险页面需要表单、版本表格和错误展示，因此存在未来重复劳动。

Naive UI 负责控件交互和样式机制；论衡负责 exact version 选择、expected_version、状态解释、API错误、不可提交条件与确认流程。不要把组件库表单校验当作领域验证，不制造统一万能业务表单平台。

- 可缩小：新页面控件、排序/分页、通用弹窗和基础校验提示的自研；只取消所选组件确实覆盖的工作。
- 保留：字段/状态映射、加载/冲突/失败处理、主题映射、可访问性和业务组件验证。
- 最小验证：一个真实新切片，组件数量受控；320/1440布局、Tab/方向键/Escape、双实体状态与错误隔离、no-emit/build检查、按需引入后的产物体积对比。合格阈值随任务固定，不凭库宣传宣布通过。
- 不纳入：整站重设计、导航重组、全页面迁移、另一套UI库、图标/字体随意打包。
- 退出：局部组件依赖可替换，数据契约不依赖Naive UI；未写业务数据库，回滚切片commit/依赖即可。预计避免工作中、适配低至中、运维增量低；试点净收益未知。

### D2. 解析：优先最小配置，不自研底层 PDF 算法

真实位置：`SourceDocumentVersion.parser_name/parser_version`、`EvidenceSourceLocator.locator_payload`，冻结合同§14 provenance、§15 locator、§19 storage、§27后续边界。主线没有解析管线；WP04-02只做领域服务，不能把parser塞入其修复。

版本调查显示 Docling 已有 slim/extras 与 native 路径，不应按旧印象把全部 ML/OCR/VLM 依赖作为默认方案。拟验证 `2.128.0` 的最小 PDF 组合，先检查 extras及传递依赖；native只提供原生单元内容，不能据此声称已有完整阅读顺序或复杂表格理解。[版本化包配置](https://github.com/docling-project/docling/blob/v2.128.0/pyproject.toml)、[原生PDF与离线配置](https://docling-project.github.io/docling/usage/advanced_options/)。

可比较一个轻量替代 pdfplumber：它面向 machine-generated PDF，提供文本/表格与几何读取，不能证明扫描件OCR能力。只有对代表样本确有优势才采用，不默认同时维护两套。[pdfplumber官方说明](https://github.com/jsvine/pdfplumber)。

组件输出仍是派生解析产物。论衡将页码/坐标/表格映射到现有locator，固定原文件hash、解析器/配置和错误；金融值的单位、期间、语义及核验走domain service，不把Docling类型传入领域真相模型。复用既有boto3和Dramatiq，但须补不可变object写入及领域错误处理；同步wrapper存在不等于已有async、安全上传管线。

小规模后续spike建议：三份公开原生中文财报（常规表格/跨页与多级表头/单位脚注负数）及一份扫描件对照，手工标注约30个目标片段/单元。比较最小native/轻量路径，必要时才增加表格模型和OCR；不测试全格式。

拟验收：hash与版本绑定/页码越界拦截/错误不冒充成功均100%；逐片段披露文本一致率、页码和bbox成功率、表格结构/单位/负数正确率，任何关键金融字段未达标则不自动入事实。至少两次同配置重跑并记录产物差异、冷/热耗时和峰值内存；复杂表格不合格时保留人工核验，不能承诺替代对应工作。数值精度上线门槛由实际任务固定，本报告不批准门槛。

安全核验发现上游近期有ODF本地文件读取和EasyOCR模型下载解压公告，需按选定版本、格式与依赖逐项验证；本轮没有做完整漏洞清单。避免无需求的ODF/HTML render/远程模型能力，不把关闭外发等同于不下载模型。[ODF公告](https://github.com/docling-project/docling/security/advisories/GHSA-4xhp-xg4w-8ppm)、[EasyOCR公告](https://github.com/docling-project/docling/security/advisories/GHSA-cjqg-rq2h-2fvj)。

预计避免工作中至高（范围取决于真实解析需求）、适配/验收中至高；native资源增量须实测，模型路径还需许可/下载/缓存核验。失败可只撤销适配器和派生产物，保留原始文件及已提交不可变Evidence，不重写历史。当前SPIKE_REQUIRED，不能承诺中文准确率或主进程部署方式。

### D3. 原文：浏览器预览/跳页先行，PDF.js处理渲染

目前 StockDetail 是mock骨架，无Evidence原文查看。合同locator允许页码和可选bbox；因此精确高亮并非所有locator的默认能力。

最低成本选择：若用户只需打开原文并跳页，先确认目标浏览器预览是否足够；需要可控文字层、缩放旋转和定位时复用PDF.js，拒绝自研渲染器。[PDF.js官方说明](https://github.com/mozilla/pdf.js)、[6.3.289发行](https://github.com/mozilla/pdf.js/releases/tag/v6.3.289)。

论衡自己负责：按exact SourceDocumentVersion取文件，受控访问、不显示错误版本、page1-based与坐标口径转换、失效/缺文件报错、无bbox时明确只能跳页。先复用viewer能力，不做批注编辑/合并/签名系统。

拟验收：每个locator跳到正确版本和页，非法页码拒绝；有bbox时在0/90度及两种缩放下测试转换，误差指标在切片合同固定；无bbox不展示伪精确高亮；拒绝未获授权文件请求。当前npm发布包需要Node>=22.13.0或>=24，项目Docker20不满足；是否用自托管预构建viewer以减少Node迁移仍需浏览器/worker/构建实证，不能默认绕过engines即兼容。[发布包元数据](https://registry.npmjs.org/pdfjs-dist/6.3.289)、[版本LICENSE](https://github.com/mozilla/pdf.js/blob/v6.3.289/LICENSE)。

预计避免底层工作中，但不把未计划自研PDF引擎算成工时节省；跳页适配低至中，高亮中，部署增量取决于版本和worker资源。回滚UI适配不动Evidence事实，可保留原文下载/跳页路径。当前ADOPT_LATER。

## E. 当前开发实现建议与唯一下一任务

建议的实际开发取舍：

1. **当前：收口既有Evidence，不重建。** candidate已有状态/幂等/回放服务；R4已有结构化collection hook。先独立验收真实交付，再在专门授权任务内完成所缺验证。
2. **工程小修：按既有机制同步OpenAPI产物。** 本轮差异只有ResearchErrorCode/Freshness/ModuleType的description增加；不改变fields或enum值，不换generator解决本次差异。此项未执行，也不是本报告唯一推荐任务。
3. **后续API：把生成链路算入任务交付，而非手写client。** 新WP04-03接口继续以backend contract为权威。Hey API迁移单独spike，若确能去掉补丁且迁移代价合适再做，不和API开发/Node升级混成一个任务。[旧生成器停止维护声明](https://github.com/ferdikoomen/openapi-typescript-codegen)、[Hey API迁移](https://heyapi.dev/docs/openapi/typescript/migrating)。
4. **后续测试：复用适用且通过独立验收的生命周期helper。** 主线三个fixture存在重复与较宽清理逻辑；candidate helper具精确归属/ledger机制，但仍有工具路径等任务限定。跨模块推广要保留行为并单独验证，不抽成过度通用测试平台，不自动以Testcontainers替换。
5. **后续业务：手动结构化录入+不可变原文件引用先行；解析、查看、UI局部复用。** 这是现有Evidence合同支持路径的实现优先建议，不删掉自动导入要求、不绕过provenance或核验，不声称完成全风险闭环。
6. **不提前写：** Runtime/多Agent、多模型路由、完整RAG平台、完整K线/技术指标集合、Sector评分、全面UI迁移。解除延期需适用的新批准，不靠本报告扩权。

必须自主掌控的代码：Evidence身份/immutable版本/验证资格/最新优先、exact Research引用、Thesis版本与提案校验、Account/Portfolio/Order/Trade Plan/Discipline/Market gates、T+1/部分成交/迟到回报/暂停恢复、policy版本及append-only审计。框架最多减少胶水与底层算法，不能裁掉这些验收。

### 唯一草案：PROPOSED — NOT AUTHORIZED

执行者：Codex。任务：独立评审已有R4 verifier harness的固定最终交付，判断其是否可进入下一专门授权的focused DB验证任务。

依据：当前主线R3真实执行为0，瓶颈包含验证器collection/证据闭环；R4候选已经存在，当前dirty。最终独立验收及跨工具/测试证据审查按AGENTS由Codex承担，不重复委派zcode重做。

基线核验：重新检查主线、Evidence candidate及R4的branch/HEAD/status。使用执行者明确固定的最终交付commit/文件哈希，不把本报告时点SHA硬编码成未来授权，不静默重定业务candidate。R4在途改动未固定/范围不清时标BLOCKED_VALIDATION，保留工作区，不stash/reset/clean，不因README或执行报告视为已通过。

范围：完整相关diff；`tg_verifier_tools/verification`、对应专门测试、执行报告及其manifest/evidence只读。只在新的独立评审分支/worktree新增一份独立评审结果，代码和历史材料禁止修改；复验缓存/普通输出用独立临时目录，不新增框架、依赖或平台。

检查：核对任务授权及文件范围；验证manifest/source-hash一致；确认使用pytest公开hook、集合与分布校验、错误路径证据保存、敏感字段脱敏；在先确认没有DB/外部副作用后运行限定selftests及collect-only，检查工具实际行为与报告相符。禁止真实DB、CREATE/DROP、修candidate或断言、补写缺失历史执行证据。测试数以真实collection为准，不沿用执行者自称的21作为独立结果。

验收者：Codex独立于zcode执行者；结论只限verifier工具，不关闭focused业务断言、05C-01或WP04-02。范围、manifest、无副作用或必要检查无法确认则停止依赖步骤，明确欠缺证据，不直接推进DB。

失败接管：在适用且原任务尚有返修额度时，zcode对明确反馈最多一次受控返修，Codex复验；额度已用、超出已验证能力域或仍失败则Codex在另行授权修复任务接管。本独立评审不同时修复。

回滚/集成：评审不改事实；报告/评审分支可保留，无业务回滚。任何代码集成和真实DB运行另行派发，必须有完整固定范围、资源预算和独立验收，不自动commit/push/PR/merge。

## F. 证据、操作与限制

### F1. 仓库证据索引

以下主线路径基于`675217c3a15c0f416aa4462ca6edc491bf99f9f6`，级别L1，证明实现/契约存在，不证明业务运行通过：

- E01：`AGENTS.md`、`docs/ARCHITECTURE_REFERENCES.md`、`docs/PRODUCT_GOAL_REALIGNMENT_2026-09-14.md`；权威与主线依赖。
- E02：`docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md:2400`及§27；支持手动/自动来源、scope与后续边界，不授权本轮接入。
- E03：`backend/evidence/models.py:196` SourceDocumentVersion、`:267` parser_name、`:608` EvidenceSourceLocator、`:642` payload；版本/定位映射基础。
- E04：`backend/research/services.py`、`api.py`、`schemas.py:15/31/44`；版本容器/API及三个enum说明。
- E05：`apps/web/package.json`、`package-lock.json`、`infra/docker/Dockerfile.web:1`；声明与锁文件存在，Docker Node20；本轮未穷尽所有锁定依赖版本冲突。
- E06：`apps/web/scripts/openapi-tools.mjs:39/68/96`，export/generate/patchGeneratedClient；`check-api-drift.mjs:13`临时比较；`apps/web/src/api/client.ts`Axios/typed error adapter。
- E07：`apps/web/src/views/WatchlistView.vue:134`原生控件，`StockDetailView.vue:4/13/20`mock；页面存在不证明真实研究/风险展示。
- E08：`tests/test_research_persistence.py:53`、`test_evidence_persistence.py:73`、`test_evidence_migrations.py:33`；独立库/迁移与清理代码；没有本轮真实DB证据。
- E09：`backend/common/storage.py:16/46/61`、`apps/worker/main.py:18/22/42`；storage/broker/actors；没有Evidence pipeline运行证据。
- E10：`docs/MARKET_DATA_DOMAIN_CONTRACT.md:176/191`；OD与排序，静态合同不批准provider/图表或数据用途。
- E11：candidate `e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4`的`backend/evidence/services.py:245/565/858/1575`、`tests/evidence_pg_fixture.py:103`；已有服务/helper，不证明本轮验收。
- E12：主线R3 focused DB acceptance；candidate fixture lifecycle独立reverify历史记录，时点/scope分别限定。
- E13：R4 `df836cb`及当前dirty工作区的pytest_plugin/runner，hook`:162`；执行报告为READY_FOR_INDEPENDENT_REVIEW；本轮没有独立PASS。

### F2. 上游来源与核验

以下均在2026-09-18只读访问，不运行候选：

- U01：[Naive UI官方仓库](https://github.com/tusen-ai/naive-ui)、[源码package](https://github.com/tusen-ai/naive-ui/blob/main/package.json)、[发布元数据2.45.3](https://registry.npmjs.org/naive-ui/2.45.3)、[MIT文本](https://github.com/tusen-ai/naive-ui/blob/main/LICENSE)。发布tag直读失败；主线LICENSE不替代发布包完整NOTICE。Result图形资源上游注明CC-BY4.0，图标/字体需另查。
- U02：[Docling v2.128.0发布](https://github.com/docling-project/docling/releases/tag/v2.128.0)、[版本package](https://github.com/docling-project/docling/blob/v2.128.0/packages/docling/pyproject.toml)、[slim配置](https://github.com/docling-project/docling/blob/v2.128.0/pyproject.toml)、[统一文档模型](https://docling-project.github.io/docling/concepts/docling_document/)、[高级配置](https://docling-project.github.io/docling/usage/advanced_options/)、[安全公告](https://github.com/docling-project/docling/security/advisories)。代码MIT声明已核，tag下LICENSE直读失败；模型权重与全部传递许可未完成。中文table issue查询失败，不据此判断无缺陷。
- U03：[PDF.js release](https://github.com/mozilla/pdf.js/releases/tag/v6.3.289)、[tag LICENSE](https://github.com/mozilla/pdf.js/blob/v6.3.289/LICENSE)、[发布包元数据](https://registry.npmjs.org/pdfjs-dist/6.3.289)、[官方getting started](https://mozilla.github.io/pdf.js/getting_started/)、[安全页面](https://github.com/mozilla/pdf.js/security/advisories)。发布gitHead `1c8020a7d4e43668ac287a3ecf9a8dbea17e4c56`；旧pdfjs-dist GitHub master返回3.2.146，未把该旧镜像当当前包。完整依赖与viewer运行未审计。
- U04：[旧codegen维护声明](https://github.com/ferdikoomen/openapi-typescript-codegen)、[Hey API真实仓库](https://github.com/hey-api/hey-api)、[迁移说明](https://heyapi.dev/docs/openapi/typescript/migrating)、[0.99.0发布元数据](https://registry.npmjs.org/@hey-api%2fopenapi-ts/0.99.0)。Node/TS要求实查，未验证本项目迁移成功。
- U05：其余初筛官方仓库：[Trafilatura](https://github.com/adbar/trafilatura)、[Testcontainers Python](https://github.com/testcontainers/testcontainers-python)、[Schemathesis](https://github.com/schemathesis/schemathesis)、[KLineChart](https://github.com/klinecharts/KLineChart)、[PydanticAI](https://github.com/pydantic/pydantic-ai)、[LlamaIndex](https://github.com/run-llama/llama_index)、[Langfuse](https://github.com/langfuse/langfuse)、[AKShare](https://github.com/akfamily/akshare)。仅身份/用途初筛，未全部做版本化许可、安全、兼容审计。
- U06：整体参考：[WyckoffTradingAgent](https://github.com/YoungCan-Wang/WyckoffTradingAgent)、[TradingAgents](https://github.com/TauricResearch/TradingAgents)、[RAGFlow](https://github.com/infiniflow/ragflow)、[FastAPI template](https://github.com/fastapi/full-stack-fastapi-template)；只做对照，不做整套替换选型。

### F3. 本轮实际检查

| 实际操作 | cwd/范围 | 结果 |
|---|---|---|
| `git status --short --branch`、`rev-parse HEAD`、`remote -v`、`worktree list`、`log -5` | 主仓及相关candidate/R4只读 | 主线/candidate clean；R4dirty；不清理 |
| `git ls-remote --symref origin HEAD` | 主仓，远程只读 | exit0，main/675217c一致 |
| `rg/cat/sed`相关源码/合同/记录；官方web查询 | 问题限定范围 | 无业务写入；不存在的`.github`、root requirements.txt、worker/tasks.py已记录，实际依赖分为requirements-api/worker |
| Python urllib查询三份npm官方版本JSON | 主仓命令，仅读元数据 | exit0；没有下载tarball或安装包；web不能访问registry时采用该只读核验 |
| `PYTHONDONTWRITEBYTECODE=1 node scripts/check-api-drift.mjs` | 原主仓apps/web；新产物仅临时目录后删除 | exit1；OpenAPI与三个Research enum生成文件不同 |
| `./node_modules/.bin/vue-tsc --noEmit` | 原主仓apps/web | exit0，无输出；类型检查通过 |
| Node调用已有exportCurrentOpenApi到独立临时目录，递归比较JSON | 原主仓apps/web；临时目录后删除 | exit0；仅3处schema description不同，fields/enum值未出现差异 |
| `git worktree add -b codex/review-oss-reuse-20260918-675217c <报告worktree> 675217c...` | 主仓Git元数据 | exit0；隔离报告空间，不切换主线 |

未运行：候选安装、解析/OCR、浏览器viewer、Naive UI试点、Hey API迁移、任何pytest/真实DB/worker enqueue/MinIO写入、行情账号或付费路径。没有全量测试或生产兼容结论。测试实际业务数量0，不把历史48/68/21/41等数字列成本轮通过数。双方token/费用、端到端实际省时 UNKNOWN。

### F4. 交付状态与交接检查

报告是本评审worktree唯一新增文件；入口和交付主线HEAD均为675217c、主线status clean。报告branch无业务diff，无commit/push/PR/merge。本轮没有修改R4在途内容，不因其dirty推断其来源或工具能力评级。

交接摘要：项目是个人A股现金账户的证据/风险OS，非自动交易；当前聚焦Evidence主线，不调整冻结规则。能力地图给出实现、候选与验证边界；未覆盖生产/多租户/完整数据源。当前阻塞涉及R4最终交付固定及独立审查、后续focused DB与完整Evidence验证债务；当前新组件均未验收。最小下一步是既有R4独立审查，后续接入条件见D。不得假设目录/报告/历史PASS等于当前业务PASS，不得重做已有candidate，不得提前实现Runtime/Sector，不得复用旧DB预算。

按项目身份、目标、scope、milestone、Git快照、能力、实现/验证/低等级证据、未覆盖、blocker/risk/unknown、状态漂移、next action和禁假设16项做报告内一致性检查：这些信息在A/B/E/F均可回答；交接仅对本定向评审 HANDOFF_READY，不表示产品或开源接入READY。

后续使用规则：不得把unsupported claim当事实；尊重L0-L5证据级别、审计范围与UNKNOWN/NOT_AUDITED/NOT_APPLICABLE；PROPOSED/DERIVED/INFERRED不当CANONICAL；同级冲突采用更新且适用的证据；优先解除关键依赖；不绕过ACTIVE决策；Next Action是建议；报告与源码冲突时重新核验源码。
