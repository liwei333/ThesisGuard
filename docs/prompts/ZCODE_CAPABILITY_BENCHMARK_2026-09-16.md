# 转发给 zcode：ThesisGuard 工程能力评估

你是被评估的 zcode coding agent。目标是判断你能否承担 ThesisGuard 大部分常规代码实现，以减少 Codex 开发用量；Codex 将独立检查源码、执行验证并决定逐能力域评级。自评不等于验收。

本轮分为只读返修和隔离开发基准。用户授权执行下述临时目录中的三个小基准；主项目及已有 worktree 全部只读。工程 coding agent 可以按此范围写码，产品内 read-only Agent 规则仍然成立。

## 1. 身份、基线与环境

主项目：`/Users/qianduoduo/Desktop/AI_app/ThesisGuard`。
候选：`/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`。

读主项目 AGENTS.md、`docs/ZCODE_CAPABILITY_EVALUATION_2026-09-16.md`；重新记录双方 HEAD/status、相关 diff --stat 和 git worktree list。先前 main 为 d3acc1c6，候选为 af4f2cbb，但当前存在在途 fixture 修改；以本轮实际读取为准。不要切换/合并/提交分支，不改候选代码，不清理 untracked。

记录 model/tool/version、权限、上下文方法、实际解释器/依赖/工具版本；未知写 UNKNOWN。AGENTS.md 是仓库指令，不声称它等于全部系统提示词。不输出密钥、连接串口令、私有思维链。

可用 Bash 不代表依赖齐备；本轮限制也不代表工具永久缺失。通过版本查询/import 等无副作用探测区分 AVAILABLE / ENV_MISSING / PERMISSION_BLOCKED / NOT_TESTED。不要安装依赖或修改锁文件。运行项目测试前先检查 fixture；本轮不运行项目 pytest、migration、Docker、worker、DB 查询或写入。

## 2. 只读返修：控制在必要文件范围

读取冻结合同第 27 节及涉及版本、幂等、查询的必要条款，当前候选 fixture 和新增 helper（存在则读），相关最新验收记录；历史缺陷不自动当作当前缺陷。

交付不超过 120 行的返修报告：

- 区分 main 已集成、候选存在、未提交修改、尚未独立验收；给实际路径和行号。
- 明确 WP-04-02 服务与 WP-04-03 API/schema 边界。
- 对当前 fixture 的创建前后失败、迁移失败、yield 期间异常、取消、清理归属说明代码路径和风险。找到不了的写 UNKNOWN；不要声称新代码运行通过。
- 修正上一轮“高度适合开发”“无法运行测试/DB”的过度结论。
- 列已读文件和关键命令，说明什么没读/没执行。

即使返修有未知项，仍可继续下面独立基准；不得据此修改项目或展开主线修复。

## 3. 临时隔离开发测试

建立新的唯一目录 `/private/tmp/thesisguard-zcode-eval-<本轮唯一ID>/`，不得复用已有目录或覆盖文件。只在该目录创建源、测试、配置和证据；最多三个任务，每个 2-6 个源/测试/配置文件，日志不计。临时目录中的最小配置属于本轮允许范围，项目配置不允许修改。保留目录供 Codex 复核，不删除。

可使用已存在的 Python/Node/依赖，通过绝对解释器或临时目录内依赖解析方式复用；运行缓存/构建产物/截图只落临时目录。不要更改共享虚拟环境/node_modules；若工具必需写共享目录，停止该项并记录。依赖不可用就交付可检查源码与明确阻塞，继续其余可执行任务。不得启动连接真实项目 DB 的应用。

三个基准采用下面的教学协议，**不是 ThesisGuard 生产合同，不证明金融风险或 Evidence 业务实现完成**。

### B1：Python 版本化快照纯函数

文件：`b1/snapshot.py`、`b1/test_snapshot.py`（必要时第三个配置文件）。公开函数完整类型标注，使用标准库 datetime/dataclass/enum 等结构化类型。

设计不可变 Snapshot，至少包含 series_id、version、status、observed_at、expires_at、value。输入/返回不要修改已有对象。状态只允许 UNREVIEWED / VERIFIED / DISPUTED / RETRACTED；version 是正整数，bool 不算整数。series_id 是非空去首尾空白字符串；value 是 JSON 兼容值。datetime 都必须带有效时区。

函数 `select_current(snapshots, series_id, now)` 返回结构化结果：exact snapshot（可以为空）、eligible、reason。

- 先按 series_id 精确匹配，再选最大 version；不按列表顺序或日期选“最新”。不回退旧 VERIFIED。
- 目标 series 无快照：MISSING，无 snapshot。
- 最大 version 有两条或更多快照：CONFLICT，无 snapshot，即使内容相同。
- 最大版本观察时间晚于 now：FUTURE；expires_at 必须晚于 observed_at，否则输入验证报 ValueError。
- 状态 DISPUTED / RETRACTED / UNREVIEWED 分别返回同名 reason。
- VERIFIED 且 now >= expires_at：STALE；其余 VERIFIED：ELIGIBLE。
- 判定优先级：MISSING、CONFLICT、FUTURE、状态、STALE、ELIGIBLE。
- 非法 Snapshot 字段、naive datetime、非法 now：明确 ValueError；不要读取系统当前时间或外部 I/O。

测试至少覆盖乱序、旧 VERIFIED 加最新 DISPUTED、重复最大版本、另一 series 不干扰、到期等于边界、未来观察、非法输入、不同 UTC offset 的等价时刻、输入不变。运行 focused tests、可用 Ruff/类型检查，报告实际命令/退出码。缺失工具写 NOT_RUN，不编造。

### B2：FastAPI/Pydantic 请求与 OpenAPI 契约

文件：`b2/app.py`、`b2/test_api.py`、`b2/openapi.json`（必要最小配置另计）。复用 B1 的纯逻辑，可合理做导入配置；不要复制整份逻辑形成漂移。使用现有 FastAPI、Pydantic v2，测试采用可用 TestClient 或 ASGI transport；测试期间不启动 TCP 服务或数据库。

实现独立演示 endpoint `POST /probe/eligibility`，显式 operationId `probeEligibility`。请求有 series_id、now、snapshots；拒绝未知字段。沿用 B1 的严格版本、时区、状态、时间顺序验证。合法领域判定（包括 MISSING/CONFLICT）返回 HTTP 200；非法请求返回 422。业务失败不得转换成 500 或静默修正。

响应显式 schema：series_id、eligible、reason、snapshot（B1 最大版本或 null）。reason 为 B1 列出的 enum；snapshot 严格字段，不泄露额外数据。响应序列化保留时间语义。导出实际 app.openapi()，不要手写伪造 OpenAPI。

测试覆盖正常请求、最新 DISPUTED、重复版本、422 非法 enum/bool-version/naive 时间/未知字段/空 series_id、响应 schema、operationId 唯一和引用可解析。证明 HTTP 判定与 B1 一致；OpenAPI 存在不算 runtime 通过。

### B3：Vue/TypeScript 双实体审阅列表

文件：`b3/App.vue`、`b3/main.ts`、`b3/index.html`、`b3/package.json`、`b3/tsconfig.json`、`b3/vite.config.ts`（六个；浏览器证据另计）。不改主前端，不下载/安装依赖。先调查已存在构建工具的解析方式；复用现有依赖只能在本临时目录接入。

构建一个可用的审阅工具首屏，Vue Composition API + strict TypeScript，不写生产 endpoint URL，不创建业务 API，不展示教学说明或营销页。两个 fixture entity，使用稳定 ID，包含名称、version、status、截止日期和多条证据引用。提供实体选择、每个实体独立的选中引用、审阅草稿、仅未审阅筛选和草稿重置操作。

- 状态按实体 ID 保存；切 A/B 保留各自选中引用与草稿，重置 A 不影响 B。
- 筛选只控制显示，不能误删另一实体数据；无匹配时有可识别空状态。
- 两个 entity/引用列表都可键盘操作；输入有 label，按钮正确 disabled 状态。
- 紧凑工作工具布局，320px/1440px 无横向溢出或文本遮挡，长中文名称不撑坏控件。
- 不需插画或外部图片；展示真实引用内容和状态即可。图标采用已有库；没有库可用原生清晰命令，不新增依赖。

执行可用 vue-tsc/build；能用浏览器则验证两实体切换、筛选、重置及桌面/移动截图；记录 URL/工具和截图绝对路径。若需 dev server，绑定 127.0.0.1 的空闲端口并仅服务此目录，结束时停止自己启动的进程。不能浏览器验证就标 NOT_TESTED，不拿 build 成功冒充交互验收。

## 4. 证据与最终反馈

保存临时根目录的 `report.md` 和 `evidence.json`；不向主项目写报告、不修改 AGENTS.md、不更新自己授权。

证据逐任务包含：实际读取/改动文件和 SHA256、命令及 cwd、解释器、exit code、关键 stdout/stderr（脱敏）、首次失败和修复过程、未执行项、总时间和重试次数、可见 token/费用（不可见 UNKNOWN）。自己创建的文件可以自行修正至通过，保留修正前失败记录；不得删除失败测试或降低要求来通过。

记录主项目和候选测试前后 git status/diff --stat；相关既有修改必须保留。状态前后变化若来自在途工作，仅披露，不能武断归因于自己或别人。不要要求或提供私有思维链。

最后输出逐能力域 YAML（文档/架构、后端、API、schema/ORM/迁移、前端、调试/重构、测试、worker/存储、agent workflow）：observed_evidence、NOT_TESTED 项、建议 L1/L2/L3、最大 XS/S/M、独立验收要求、风险。后三类无真实环境测试须为 UNPROVEN，不能由本轮模拟基准推导。建议不是最终授权，不给没有证据的高分。

推荐一个已测能力域的下一真实 S 任务，仅给指定文件/验收方案，不执行。修复能力要由后续 Codex 的一次受控反馈验证，当前自主修正只能证明本轮行为。

发给用户的最终消息控制在 100 行以内：Stage 1 补正摘要、B1/B2/B3 实际 PASS/FAIL/BLOCKED（候选自报）、临时根目录及 report/evidence/源码绝对路径、实际验证和缺失项、能力路由 YAML。用户将转发给 Codex；Codex 必须独立复核后才能更新项目路由。
