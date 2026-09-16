# zcode 工程能力基准：一次受控返修 R1

执行者：zcode。验收者：Codex。目标：修复已复现的基准契约、键盘和证据问题，判断能否开始常规 S 代码任务。原首验 FAIL 保留，返修自报不等于授权升级。

先读主项目 AGENTS.md 和 `docs/ZCODE_CAPABILITY_EVALUATION_2026-09-16.md` 的 Stage 2 Independent Review；重新取 main/candidate HEAD/status，保留其他人在途修改。项目和所有已有 worktree 只读，本轮不执行项目测试、DB、Docker、worker，不改 AGENTS.md 或历史验收材料。

原目录：`/private/tmp/thesisguard-zcode-eval-20260916181453-77706/`。
独立首验：`/private/tmp/thesisguard-zcode-independent-20260916/test_independent.py`、`browser_review.py`、`browser-results.json`、桌面/移动截图。独立脚本/首验输出不得修改。

用户授权继续本轮隔离评估。创建新的唯一 `/private/tmp/thesisguard-zcode-eval-r1-<ID>/`，复制原基准必要源文件作为基线，记录原 13 个哈希；只在新目录修改。保留原目录及失败证据，不安装依赖、不改变共享 node_modules/虚拟环境。临时证据/缓存/构建/截图落新目录。可复用现有依赖，无法验证标 BLOCKED_VALIDATION，继续可执行项。

## 指定修复

1. B1 JSON value：用结构化递归验证或合理标准库协议拒绝 object、set、嵌套非法值、非字符串 JSON object key、非有限数值及循环引用；统一 ValueError。支持正常 JSON scalar/list/object。不依靠 default=str 将非法值伪装成合法值。
2. B1 不可变性：构造时与调用者嵌套数据脱离，Snapshot.value 对外不可原地污染持久快照，可采用内部不可变表示或返回深拷贝的公开 value。明确表示/序列化兼容 API。独立测试中修改原 dict/list 后快照必须保持原值；再增加修改读取出的 value 不改变快照的检查。这是 immutable Snapshot 的显式澄清，不是更改生产金融合同。
3. B1/B2 latest snapshot：MISSING/CONFLICT 仍 null；唯一最新为 FUTURE/DISPUTED/RETRACTED/UNREVIEWED/STALE 时返回该快照，eligible 仍 false，原判定优先级保持。B1 原提示允许 exact 为空有歧义，B2 的 latest snapshot 约定在本 R1 明确如上。允许修改原自测 exact=None 的错误期望，但保留 reason/no-fallback 断言并记录理由；不能删除失败用例。
4. B2 请求验证：严格正整数 version，拒绝 bool/float/string。expires_at <= observed_at 在 Pydantic 请求验证阶段返回 422，路由不得抛 ValueError 成 500；不以捕获所有异常伪装验证错误。
5. 用主项目 pyproject.toml 实际配置验证 Ruff（不 --fix 项目）及 mypy --explicit-package-bases；修复源码类型错误、导入/未使用变量等。说明实际 interpreter/config/命令。不使用 ignore/Any/unknown 强转绕过本可修正的错误；合理受限 JSON 类型请解释。
6. B3 标签键盘：Left/Right 改变选中实体并移动实际焦点；验证切回、Tab 顺序和草稿/引用保留。清理未使用且错误的 createState 强转。把每个基准源/测试/配置限定在 2-6 文件；B3 可将空 style.css/env.d.ts 需求合并进既有文件与 tsconfig，而不是漏计文件。
7. 修正报告与 evidence：身份/模型版本 UNKNOWN，真实 before/after HEAD/status；B2 bool-validator失败不能写进 B1。记录新命令原始 stdout/stderr/exit/cwd、首次失败、修正、可见成本（不可见 UNKNOWN）。不用 Git 元数据猜是谁执行提交，不把自测 PASS 当独立验收。
8. 路由中 ORM/迁移/真实 DB/worker/storage/Agent 维持 UNPROVEN；只有明确延后项才写 DEFERRED。不要新增候选 grade helper，已有 `_ensure_source_grade_allowed`；下一真实任务建议先确认既有实现与实际缺口。

## 验证与交付

先在新目录加回归并重现 RED，再实现修复；保留初始输出。跑原自测（允许上述明确契约期望修正）、新增回归、实际 Ruff/mypy、Vue 类型/build、可用浏览器的草稿/引用隔离、方向键、320/1440 截图。若启动临时服务只绑定 127.0.0.1 空闲端口，结束停自己进程。

首验独立脚本固定旧 ROOT，你不能修改它；在新目录写自己的等价回归。Codex 后续会单独设置新目标复跑原断言，继续保留首验 RED。OpenAPI 从实际新 app.openapi() 导出，检查全部 ref、operationId、请求/响应/422 并记录哈希；测试不要静默覆写基线 OpenAPI 掩盖漂移。

本轮教学协议不是生产 Evidence 实现。本任务不允许新业务功能/新依赖/迁移/产品规则变化。超出修复范围先记录缺口，不扩大项目操作。

新根目录保存 report-r1.md 和 evidence-r1.json；报告包含逐 R-ID 已修/未修/验证阻塞、diff（与原源文件比较）、文件数及 SHA256、实际检查与失败、前后状态、剩余限制。最终给用户新目录与源码/报告/证据绝对路径，控制在 80 行内。不得自行更新评级；用户转发后 Codex 决定逐域 L2/S 是否成立，失败则接管或收窄该域。
