# R1C-03B trusted correction 规则定义调查草案

Task: TASK-WP04-02-R1C-03B-RULE-CONTRACT-R1。Date: 2026-09-16，Asia/Shanghai。

Draft status: **PROPOSED / NOT_APPROVED**。Readiness: **NOT_READY**。

生产 approved trusted correction rule 集合保持为空。本草案只保留一个调查候选，不交付可启用的成功谓词。任务派发、文档独立验收、规则批准和实现派发是四个不同动作；本文件不能作为规则启用授权。

## 1. 结论与数据边界

暂不派发正向 trusted rule 实现。唯一调查候选为 `tg.tc.display-title-ascii-tail.v1`，含义为仅删除 `display_title` 尾部一个或多个 U+0020 ASCII 空格。此 ID 只用于审查追踪，未加入生产集合、数据库配置或运行时 registry。任何谓词、字段或支持路径扩大都必须形成另一个版本的规格并重新批准，不能沿用 v1 授权。

预期价值是假如用户确实需要维护标题标签，可避免纯标题整理导致再次 review；这只涉及表示整理，不能证明事实抽取正确。当前只读调查没有证明真实标题尾空格问题或 review 成本，也没有批准的标题语义等价契约。如此狭窄的收益是否足以承担直接生成 VERIFIED 的政策成本，仍待用户决定；不能因为技术上可 trim 而强行启用。

现有数据能证明“新旧已提交字段一致”和“引用同一个 exact source/locator”，但不足以独立证明“被引用的原文确实支持所提交事实”。普通 review 已有合法命令路径，但其中 reason/actor、VERIFIED 状态或 legacy rule 字符串不构成可机械重验的原文语义证明。冻结合同 §12、§13、例26 要求同事务完成 schema/source/locator/semantic/status/audit 检查，不能用字段相等替代缺失的语义前提。

### 实际依据

以下治理文件从主仓读取；以下实现位置均属于固定候选 HEAD0cef44fd2ffd929b40e849e607af0bd4c44d14d2，不能推定已集成 main。

| 依据 | 已观察事实 | 不能据此推定 |
| --- | --- | --- |
| [冻结 Evidence 合同](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md)，§8–15、17–23、例25/26/42 | exact lineage、普通 UNREVIEWED、命名 trusted 完整检查、不可覆盖历史 | 已批准某具体规则；冻结时 §4 的旧实现快照仍是当前代码状态 |
| [ORACLE-R1 独立验收](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-03A-ORACLE-R1-acceptance.md) | 该基线的空批准、未批准拒绝、不隐式继承已获独立验收；四路径 audit 映射有明确证据 | 正向 trusted、全部 import/from-status 资格或全 WP04-02 完成 |
| [services.py](/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/services.py:159)，:1530 | 不可变空 frozenset；新非 None 未批准 rule 拒绝，保留只读历史 replay | 完整 positive registry/semantic validator |
| 同文件 :565、:823、:1075、:1386 | create、revise、replacement、append 的实际参数和调用顺序；省略/None 的 correction 不继承 | revise 支持任意身份、source version 或 locator override；实际公开签名没有这些参数 |
| 同文件 :363、:1976、:2063、:2405 | 保存 source metadata/hash/object references；检查 lineage、source grade/type、locator 结构/可用 bounds、exact derivation 图 | 已读取对象字节、校验 hash 对应真实对象、验证 quote 或数值/单位/原文语义 |
| [models.py](/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/models.py:196)，:357、:608 | immutable source/version/children、值、locator、hash、parser 名称等列已存在 | 原文/对象字节/parser artifact 已实际可读；存在独立语义验证结果列 |
| [repositories.py](/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/repositories.py:142) | exact/current/history 加载持久化行与 children | 读取 MinIO 或认证事实语义 |
| [服务测试](/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/tests/test_evidence_services.py:169)，:248、:3404 | fixture 的 hash 由字符串填充，object key/quote hash 是声明；legacy 完整 append seed 和合法 review 用于边界测试 | fixture 已持有真实报告或 parser 输出；它们是生产规则批准/原文验证证据 |

本轮未查询 DB、读取 MinIO 或运行 parser。生产对象可用性、真实源内容、真实标题需求均为 UNKNOWN；“已存在”在本草案中指 ORM/服务支持持久化相应数据，不代表核验过生产记录内容。

调查首先排除了全空白折叠、raw numeric 表示规范化和 child display-order 整理作为本次成功规则：空白可能分隔数值/否定或语法；raw numeric 与原文一致性及单位缩放无独立依据；order/role/weight/metadata 可能表达关系语义。只留下标题尾 U+0020 删除这一候选，仍不能绕过下列前置。

## 2. 唯一调查候选的边界与未满足前置

设 P 为服务读取并锁定的当前 exact EvidenceVersion，S 为其 series，C 为明确命令输入，N 为待创建的完整新版本。T(s) 只删除 s 尾部连续 U+0020；不 strip 其他字符，不 casefold，不 Unicode normalize，不更改内部/前导空白。要求 C 明确提供新标题；`N.display_title = T(P.display_title)`，且 T(P.display_title) 非空、与原字符串不同。标题含控制字符、换行、tab、不可见格式字符或需要特殊渲染的语法时，先拒绝调查候选，不把它们解释成等价格式。

这些只是可检查的表示约束，**不是完整 admission 成功谓词**。当前 readiness gate 不满足，故候选的新 trusted 请求仍按现有 unapproved_rule 拒绝。不得在实现中用“证据以后再补”“人工说没问题”或调用方传 true 来满足 gate。

| 前置 | 精确需要的规格/证据 | 当前情况与失败行为 |
| --- | --- | --- |
| G1 标题语义与价值 | 用户确认标题为纯展示标签，定义允许字符/渲染语义及尾 U+0020 等价关系；给出确实需要这种持久化修正的例子和价值 | 未定义/未证实；NOT_READY。若仍无有意义收益，关闭候选，保留 ordinary correction |
| G2 prior/source/locator/semantic 的独立验证 | 为被批准的窄 claim/metric/source 类型给出 exact 原文/对象字节或等效权威证据、来源与字节绑定、locator 到原文的确定性对应、原文命题到全部语义字段的明确谓词；规定同事务可用的验证证据所有权、完整性与失效条件 | metadata/hash/reason 存在，证据链和谓词不存在；NOT_READY。不得新造通用“semantic_ok”输入或以 grade/extractor/actor/hash 判真 |
| G3 source-state 与冲突资格 | 明确是否只允许当前 source exact、ACTIVE；如何处理最新撤回/替代/降级/CONFLICTS_WITH、证据失效和事务内状态一致性；缺失/歧义拒绝 | 提议采用下面的最窄候选集合，未经批准；不是 ordinary 全资格表或跨源冲突裁决 |
| G4 rule policy 批准 | 批准 ID/version、价值、字段/路径/prior 范围、完整 G2 谓词、audit 与启用时间；dispatcher 再派发精确实现合同 | 未批准；生产集合为空。文档验收不能代替政策批准 |

待批准的最窄 prior 范围建议：当前 highest exact P 为 VERIFIED、FACT、SOURCE_BACKED、单 INSTRUMENT；只考虑 COMPANY_ANNOUNCEMENT/FINANCIAL_REPORT 与 S grade；source exact 属于同一 primary lineage 且为当前 source version、ACTIVE，source lifecycle tuple 合法；时间窗口在明确的 command timestamp 下未失效；恰有一个匹配 scope 的 PRIMARY_SCOPE instrument child，无 derivation/corroboration/incoming support 关系。此范围用于缩小后续讨论，所有扩展均需用户决定，不能将其泛化到 ESTIMATE、MANUAL、DERIVED 或 CROSS_INSTRUMENT。

P 的 VERIFIED 只是必要条件；G2 仍须独立验证 P 的语义和 source/locator，legacy rule 和 review reason 不能满足它。不合格 P、current 更高版本不合格、过期、撤回、source latest 不一致、冲突关系或证据缺失均 fail closed。此建议不改变 R1C-01/02 的已验收读取/状态命令行为，也不制定所有 ordinary correction from-status 资格。

## 3. 四路径支持矩阵

| 路径与实际入口 | 当前新 trusted 请求 | 若前置完整并另获批准，可讨论的 v1 范围 | 其他行为/拒绝原因 |
| --- | --- | --- | --- |
| same-series：revise → private append | 候选 ID 未批准，拒绝 | 唯一可能支持路径；P/S identity 全相同，仅标题 T，new exact N+1 | 无 G1/G2/G3/G4 则无正向；字段/child 差异拒绝 |
| automatic replacement：revise → replacement → create | 未批准，拒绝 | 不支持 | exact support/member set 改变 identity，不能是标题尾空格整理；ordinary 继续 R1B routing |
| direct replacement：create_replacement_evidence_series | 未批准，拒绝 | 不支持 | 该命令要求至少一个 identity 变化，与 v1 identity 不变矛盾；不能换路保留 VERIFIED |
| underlying create：create_evidence_series_version，有/无 supersedes | 未批准，拒绝 | 不支持 | 不能用底层 create/调用 private helper/携带同一个 ID 伪装 same-series；有 predecessor 不代表授权。无 predecessor 是 initial import，另有资格合同 |

拒绝的是非 None 的新 trusted 请求。省略或显式 None 继续 ordinary：新 correction 为 UNREVIEWED、rule=None，旧规则不继承、不清除；身份改变产生 replacement v1、exact supersedes 与完整 CORRECTION tuple。空/空白/未知/大小写变体/非字符串不转换为 None，不 trim/casefold 成合法 ID。历史同请求 replay 只返回已提交 exact response，不是新准入；保留现有语义，不在本规格闭合 R1D 全 hash/concurrency/UNKNOWN_OUTCOME。

## 4. 逐字段证据与约束矩阵

下面是 NOT_READY 候选应满足的检查清单，不是已经批准的 validator。E 表示与 P/S 的权威持久化值逐字段类型明确相等，null 必须仍为 null；字符串按 exact Unicode 序列比较，Decimal 不能 float 转换，timestamp 比较同一 UTC instant。JSON 按完整、类型敏感结构比较，不仅比较 ID set 或 canonical hash；旧历史行另外全列逐字值比较。未来实现须显式枚举检查，新增未知字段 fail closed，不能利用 canonical_json 中 URL/Decimal 归一化吞掉变化。

失败标记：V = 现有 EVIDENCE_VALIDATION_ERROR，trace 包含 field/validation_path、exact prior/source ID、requested rule/type、稳定 reason；L = 现有 EVIDENCE_INVALID_SOURCE_LOCATOR 与 locator_path；P = 现有 provenance/grade/source-not-found 错误；C = 现有 version conflict。候选语义缺口的 reason/具体 path 尚须后续合同冻结，当前所有新候选 ID 的实际错误仍为 trusted_correction_rule/unapproved_rule。所有失败均须发生在本命令的新行/children/idempotency/audit 入 session/flush 前；不得为拒绝记录数据库 audit 留残。错误 details 可追踪不代表本轮新增了错误字段实现。

### Series identity 与所有旧行

| 字段 | 权威数据来源 | 候选约束 | 失败 | 具体测试例 |
| --- | --- | --- | --- | --- |
| S.id | exact P 的 series FK/持久化 S | E；不得创建替代 series | V | 改成另一 series ID |
| scope_type | S | INSTRUMENT 且 E | V | 改为 MARKET |
| scope_key | S + exact Instrument | 同一真实 instrument ID，E | V | A→B |
| information_type | S、P | 均 FACT 且 E | V/P | FACT→ESTIMATE |
| claim_key | S、P + G2 原文命题对应 | 非空、E；语义对应需 G2 | V/NOT_READY | revenue→profit |
| metric_key | S、P + G2 metric 定义 | E，null 不填造；G2 必须覆盖其含义 | V/NOT_READY | yoy→qoq |
| period_start | S、P + G2 原文期间 | E、与 end 顺序合法 | V | 2026-01-01→2026-07-01 |
| period_end | S、P + G2 原文期间 | E、与 start 顺序合法 | V | H1→全年 |
| provenance_kind | S、P | SOURCE_BACKED，E | V/P | 改 DERIVED |
| primary_source_document_id | S、source exact FK | E，exact source version 属于该 lineage | P/V | 交易所报告→媒体复述 |
| origin_key | S | null，E | P/V | 添加 derived:... |
| series_identity_hash | S + 全部十维字段 | 重算十维一致，不只信 hash 字符串 | V | 保留旧 hash 同时改 metric |
| S.created_at | 旧 S 持久化行 | 旧行 E、不写 S | V/history | 用新 command 时间覆盖旧行 |
| S.created_by_actor | 旧 S 持久化行 | 旧行 E；不是语义证明 | V/history | USER 标签授权变值 |

### EvidenceVersion 全部列

| 字段 | 权威数据来源 | 候选约束 | 失败 | 具体测试例 |
| --- | --- | --- | --- | --- |
| id | 服务生成的新 UUID、旧 P exact | N 新 ID，不能与 P/children/support 相同；P 原 ID 不变 | V/history | N.id=P.id |
| evidence_series_id | S/P | N=P 的 series；不接受调用方漂移 | V | 指向 replacement series |
| version | 锁定 current、C.expected_version | P highest、expected=P.version；N=P.version+1 | C | stale expected_version |
| source_document_version_id | P + exact SourceDocumentVersion | E、非 null，同 source lineage；不能换新 source exact | P/V | 同 bytes 不同 source version |
| information_type | P/S | FACT、E | V/P | 改 ESTIMATE |
| provenance_kind | P/S | SOURCE_BACKED、E | V/P | 改 MANUAL |
| source_grade_snapshot | P + exact source grade | E 且等于 source 的 S；grade 本身不证明值 | P/V | snapshot S、source 已为较新 D |
| verification_status | P/current + 完整 admission | P VERIFIED 必要；N VERIFIED 只有完整批准检查成立，目前无正向 | V/NOT_READY | P PENDING_REVIEW 直接 trusted |
| status_changed_at | C 明确 aware command time | N=C，非 null；用于资格判断；P 原值不变 | V | None/naive time |
| status_changed_by_actor | C、既有 ACTORS | 明确合法 actor，非 null，N=C；actor 不证明语义 | V | LLM 标签申请改值 |
| status_change_kind | correction 命令所有权 | N=CORRECTION；P 原值不变 | V | 使用 INITIAL_VERIFICATION |
| status_reason | C | 明确非空理由，N=C；不是 G2 证据 | V | partial tuple/reason=None |
| display_title | P + C + G1 | 唯一内容变更：明确 C=T(P)，仅尾 U+0020 非空删除；完整语义等价待 G1 | V/NOT_READY | 删除内部空格/换“毛利率”为“净利率” |
| display_text | P + G2 source 命题 | E、非空；G2 验证其与其他语义字段对应 | V/NOT_READY | “增长”→“下降” |
| claim_key | P/S + G2 | E 且匹配 S；不接受 title 整理夹带 claim 变化 | V | gross_margin→net_margin |
| metric_key | P/S + G2 | E 且匹配 S | V | 改 metric/将 null 填值 |
| raw_value | P + G2 原文 bounded span | exact E，不 trim 或数字重写；原文对应目前缺 | V/NOT_READY | 32.5%→325% |
| raw_unit | P + G2 原文单位 | E；单位不是任意标签 | V/NOT_READY | 万元→元 |
| normalized_value | P + G2 明确转换关系 | Decimal E，不 round/float/缩放；原文和转换证明目前缺 | V/NOT_READY | 32.5→0.325 |
| normalized_text_value | P + G2 命题 | E，包括 null；不改变否定、范围或限定 | V/NOT_READY | 未获批准→已获批准 |
| normalized_unit | P + G2 单位规范 | E；不扩张单位规则 | V/NOT_READY | percent→ratio |
| currency | P + G2 原文币种 | E，null 不猜 CNY | V/NOT_READY | CNY→USD |
| period_start | P/S + G2 | E，顺序合法 | V | H1→H2 |
| period_end | P/S + G2 | E，顺序合法 | V | 6月30日→12月31日 |
| as_of | P + G2 原文事实时点 | E、non-null；不得以新观察时间刷新事实 | V/NOT_READY | 8月31日→9月16日 |
| effective_from | P + G2 有效窗口 | E；C 时间下满足经批准的窗口资格 | V/NOT_READY | 起点提前一天 |
| effective_to | P + G2 有效窗口 | E；不通过清空延长有效性 | V/NOT_READY | 到期日→None |
| supersedes_evidence_version_id | 服务读取的 P exact | N=P.id；不是 P 的 predecessor/浮动 current；P 原 supersedes 不变 | V/history | N 链到更早版本/自己 |
| created_at | same-series command time C | N=C.status_changed_at；P 原值不变 | V/history | audit/row 时间来自不同输入 |
| created_by_actor | same-series actor C | N=C.status_changed_by_actor；P 原值不变 | V/history | 用 prior IMPORTER 掩盖 USER command |
| extractor_name | P | E；只证明来源记录，不证明语义 | V | 更新 parser 标签同时改值 |
| extractor_version | P | E；不得把新版本号当批准 | V | 1.0→2.0 |
| prompt_template_version | P | E，包括 null；LLM 不判可信 | V | 新 prompt 替代原文证据 |
| manual_entry_reason | P | 窄 SOURCE_BACKED 候选不引入 manual；内容 E | P/V | 添加人工理由绕 G2 |
| manual_observed_at | P | E；不填造 source-less资格 | P/V | 新 manual time |
| trusted_correction_rule | C + 将来批准的 immutable definition | N 仅等于该命令明确请求的批准 ID；不取 P.rule。当前候选 ID 未批准 | V | omitted/None 继承 legacy ID |

### Source 与原文证据

SourceDocument 全行及 SourceDocumentVersion 全行保持原样；标题 correction 不创建、修改或重观察 source。以下逐字段说明资格来源。表内 E 指 exact source 原行不变，原文有效性仍依赖 G2/G3。

| 字段 | 权威来源 | 候选约束/缺口 | 失败 | 测试例 |
| --- | --- | --- | --- | --- |
| source.id / source_document_id | PostgreSQL exact FK | 同 S primary lineage，E | P | 来源 A→B |
| publisher_key | SourceDocument + G2 权威采集出处 | E；字符串不认证出处 | P/NOT_READY | 冒充 szse |
| publisher_name | SourceDocument | E，不授权 semantic | V | 改显示名称并声称可信 |
| issuer_key | SourceDocument + G2 issuer 对应 | E；核对命题主体的证据缺 | P/NOT_READY | 甲公司事实挂乙公司 |
| issuer_name | SourceDocument | E，名称本身不认证 | V | 同名 issuer |
| source_type | SourceDocument、冻结 §11 | 窄建议两个 S 类型，合法 grade pair；未经政策批准 | P | WEB_PAGE 改称报告 |
| external_document_id | SourceDocument + G2 发行依据 | E；独立发行对应目前缺 | P/NOT_READY | 复制另一公告 ID |
| canonical_url | SourceDocument + G2 captured bytes | E；不访问浮动 URL 判真 | V/NOT_READY | URL 同、内容变 |
| source.title | SourceDocument | E，不与 Evidence 标题自动合并 | V | 改源标题 |
| document_language | SourceDocument + G2 artifact | E；翻译不属于本候选 | V | zh-CN→en |
| source.created_at | 旧 source 行 | E | history | 改旧创建时间 |
| source.created_by_actor | 旧 source 行 | E；actor 非授权 | history | IMPORTER 标签即授权 |
| source version.id | exact source row/P FK | E，建议等于 latest exact | P/V | 相同 content_hash 的另一版本 |
| source version.version | exact/current source query | E，不退回旧 ACTIVE | P/V | latest 撤回而引用旧 v1 |
| version_reason | immutable source version | E；reason 非 semantic 证明 | V | METADATA_CORRECTION 当事实正确 |
| source_grade | exact version、完整 grade/type matrix | E、合法 pair、窄建议 S；不单独判真 | P | S 文件抽错一行 |
| version_fingerprint | exact row + 冻结 §8 字段 | E，重算一致仅验证 metadata 绑定，不证明真实 bytes | V/NOT_READY | hash 正确但 metadata 来自伪造输入 |
| published_at | exact metadata + G2 发行时点 | E，不能拿 fetched_at 替代 | V/NOT_READY | 发布时间→采集时间 |
| observed_at | exact row | E，不刷新 Evidence as_of | V | 重观察延长事实有效性 |
| fetched_at | exact row + G2 byte acquisition | E；声称 fetched 不等于对象可读 | V/NOT_READY | key 无对象 |
| content_hash | exact row + G2 canonical object bytes | E、合法 SHA256 并重验实际 bytes；当前服务只接受声明 | V/NOT_READY | 相同 hash 字符串、对象缺失 |
| source_version_label | exact metadata + G2 发行版本 | E；标签本身不认证 | V | H1 标签但内容全年 |
| source_revision_id | exact metadata + G2 provider 记录 | E，包括 null | V | 同 bytes 新 revision ID |
| media_type | exact metadata + G2 对象类型 | E；parser 对应需 G2 | V/NOT_READY | PDF key 实际是 HTML |
| object_key | exact row + G2 immutable object | E、实际 bytes 可读且绑定 hash；可用性未调查 | V/NOT_READY | 改指另一对象 |
| text_object_key | exact row + G2 parser artifact | E，包括 null；不能 null→猜测文本 | V/NOT_READY | 缺文本仍判通过 |
| text_object_hash | exact row + G2 artifact bytes | E，有 artifact 才能重验，不能只比较 hash | V/NOT_READY | 同 hash 不同正文 |
| parser_name | exact metadata + G2 artifact 来源 | E；名称不是依据 | V/NOT_READY | tg-pdf 即“正确” |
| parser_version | exact metadata + G2 reproducible artifact | E；版本不是依据 | V/NOT_READY | 升版本声称修正成功 |
| versioned_metadata | exact row + G2 byte-bound parser output | E、完整类型敏感结构；page/table bounds 声明需独立出处 | L/NOT_READY | 宣称有20页实际只有2页 |
| source_status | exact/latest source + G3 | 窄建议 latest same exact ACTIVE；不从旧状态继承 | P/V | latest RETRACTED/SUPERSEDED |
| source_status_changed_at | exact/latest source | ACTIVE 要求 null；非 ACTIVE 不允许本候选 | P/V | partial lifecycle tuple |
| source_status_actor | exact/latest source | 同上，E；不代替 source-state 检查 | P/V | 非法 actor |
| source_status_reason | exact/latest source | 同上，E | P/V | 撤回 reason 缺失 |
| source version.created_at | 旧 exact source row | E，不创建新 source | history | 标题整理新增 source version |

冻结词汇中的 `source_quote` 不是候选 EvidenceVersion 的持久化列；`quote_hash` 不是原文。缺少 bounded 原文内容及其 exact 定位验证时，不能将原文存在写成 IMPLEMENTED。

### Locator、instrument、support 与历史 children

| 字段 | 权威来源 | 候选约束 | 失败 | 测试例 |
| --- | --- | --- | --- | --- |
| locator.id | 旧 L / 服务新 child UUID | 旧行不变；N child 新 ID | history | 复用旧 child 改 owner |
| locator.evidence_version_id | P/N exact ownership | 新 child=N.id；旧 owner=P.id 不变 | history | post-hoc 改旧 FK |
| locator.source_document_version_id | exact L/P/source FK | 每个 L 都等于 P source exact，N 保留 | L | locator source A、P source B |
| locator_type | exact L + 冻结枚举 | E；窄调查优先 PAGE，其他类型需另决 | L | PAGE→WEB_ANCHOR |
| raw_locator | exact L + G2 raw location | E、非空；raw string 不证明坐标 | L/NOT_READY | p.12→p.13 |
| short_citation | exact L | E；引用显示不代替源验证 | L | “p.12”→“p.2” |
| locator_payload | exact L + byte-bound G2 parser | E、完整结构、正整型/bounds 合法；实际原文位置需 G2 | L/NOT_READY | 合法页号但指向另一指标 |
| quote_hash | exact L + G2 bounded quote bytes | E，包括 null；有 hash 仍必须重验 quote 对应，缺证据拒绝 | L/NOT_READY | unchanged hash、quote 内容不支持值 |
| locator.created_at | 旧 L / 新 command time | 旧 E，新 child=C time | history | 覆盖旧 child 时间 |
| instrument child.id | exact I / 服务新 UUID | 旧 E，新 ID 不复用 | history | 借旧 child |
| instrument child.evidence_version_id | exact I/P/N | 新=N.id，旧不变 | history | post-hoc 改 FK |
| instrument_id | exact I、真实 Instrument/S scope | E，窄建议恰一 PRIMARY_SCOPE 匹配 S | V | A→C |
| instrument role | exact I、角色枚举 | E | V | PRIMARY_SCOPE→PEER |
| link_order | exact I | E，即便 identity 不变也不授权重排 | V | 1→2 |
| link_metadata | exact I | E；null/{} 不默认为等价 | V | 新增 currency/issuer 元数据 |
| instrument child.created_at | 旧 I / 新 command time | 旧 E，新=C time | history | 改旧行 |
| derivation child.id | exact 关系行 | 窄 SOURCE_BACKED P/N 无该行；旧数据不修改 | V | 增一条 derivation |
| derived_evidence_version_id | exact 关系 owner | 同上；不能关联自身绕路径 | V | 新 version 自支持 |
| supporting_evidence_version_id | exact support row | 窄候选无支持；任何变更/支持图资格不泛化 | V | V1+V2→V1+V3 |
| derivation role | exact link | 窄候选无支持；角色非真值 | V | INPUT_FACT→INPUT_ESTIMATE |
| support_order | exact link | 窄候选无支持，不接受顺序整理 | V | 1→2 |
| support_weight | exact link | 窄候选无支持；weight 不证明语义 | V | 0.5→1 |
| derivation created_at | 旧 link 行 | 旧行不变；不新增 | history | 修改历史 support |
| corroboration.id | exact relation row | 窄候选无 left/right 关系；旧关系全保留 | V/history | 整理时删除冲突 |
| left_evidence_version_id | exact relation FK | 任何现存关联均排除窄候选，不偷偷复制/改绑 | V | 改绑 N |
| right_evidence_version_id | exact relation FK | 同上；不从 ID 排序推断信任 | V | 关联到另一版本 |
| relation_type | exact relation enum | CONFLICTS_WITH 明确拒绝；其他关系也在窄范围外 | V | 冲突→CORROBORATES |
| corroboration created_at | 旧 relation 行 | 旧 E | history | 覆盖创建时间 |
| corroboration created_by_actor | 旧 relation 行 | 旧 E，actor 不证明语义 | history | 用 USER 清除冲突 |

无 derivation/corroboration/incoming support 是窄范围的明确拒绝策略，不是删除已有历史链接。若后续批准需要支持这些 prior，必须单独定义 exact 图与关系语义证明、不可变 children 的新版本所有权，不把 same-ID-set 视为 role/weight/order 等价。

## 5. 语义证明与 audit/status 所有权

设 Q 为除展示标题及新版本身份/生命周期元数据外的完整语义快照：claim/type/value/unit/currency/period/as_of/effective/provenance/source exact/locators/instrument/support/relations/extractor/manual 字段。仅在完整 E 比较成立时能推出 Q(N)=Q(P)。如果 G1 给出获批的表示语义函数 R，使 R(T(title))=R(title)，则可以证明本次表示变换不改变既有命题。

这个等式不证明 Q(P) 为真；错误 prior 会把错误原样复制。冻结合同要求的完整验证仍需 G2 明确的权威证据与确定性原文→命题关系，并在同事务核验 source/locator、current/status 与有效性。当前 G1/G2 未满足，所以不能把上述条件证明转化为 VERIFIED。普通 correction 不提供 rule 时仍 UNREVIEWED；合法 review 与 initial VERIFIED import 的完整资格保持独立。

将来若批准窄 same-series：N 必须是新 exact N+1，supersedes=P.id，完整四字段为 (known command time, known actor, CORRECTION, known reason)，rule 来自本命令明确输入。exact aggregate 的 event_type 必须 EVIDENCE_CORRECTION；aggregate_type=EvidenceVersion、aggregate_id=N.id，恰一事件，actor/time 与已知命令输入相同，payload 逐项验证 target series、expected_version、明确 overrides/rule、新旧标题及校验依据应有的绑定信息。当前 append payload 尚无独立语义证明记录，后续 audit 证据字段及如何在现有 JSON 中绑定 G2 须在实现合同冻结；不声称已实现，也不要求本任务改 schema。

现基线 automatic/direct/underlying replacement 的 exact-version 事件为 EVIDENCE_VERSION_CREATED，另有新 series 的 EVIDENCE_SERIES_CREATED；这是 ORACLE-R1 明确的现有路径映射，不是通用新冻结 taxonomy。row CORRECTION tuple 不因 event_type 改变而省略。保留 regression 中 exact aggregate/count/actor/time/payload/creation ownership 的断言，不能接受任意事件名。v1 候选不支持 replacement，不能据此增加其正向授权。

idempotency.scope、idempotency_key、request_hash、status、response_ref_type、response_ref_id、created_at 的权威来源分别是实际 command operation/target、原请求 key、服务 hash、提交结果状态、实际结果类型/ID、command time；失败均不能占 key，成功与新版本同 caller transaction，replay 读原 response、不新增任何行。audit.id 由服务生成；aggregate_type/aggregate_id/event_type/payload/occurred_at/actor 由上述明确命令所有权确定，不能由调用方任意指定。测试分别使用变 key/变 payload、partial status tuple、错误 aggregate、重复事件、不同 actor/time 和错 response ID 反例。现 hash 尚未包含所有未来 admission 语义字段，不能直接扩充空 allowlist；若窄规则必须改变现 replay/hash 合同，须 dispatcher 另定边界，不能顺手闭合 R1D。

概念所有权为“用户批准的 immutable versioned definition → 服务私有固定 validator → 全字段/证据 admission → append/status/audit”。registry 只能承载已批准的固化版本，不提供运行时 caller registration、配置开关、环境注入、可替换 validator、rule string 即可信或公共底层 create 绕过。缺字段、新未知字段、类型错误、source 不可用、语义证据不可重验等均拒绝。后续 policy 变更仍遵守 AGENTS 的版本化、replay/前瞻验证和用户批准要求。

## 6. 具体反例

| 反例 | 明确输入 | 为什么不能可信修正 |
| --- | --- | --- |
| 数值空格 | raw_value 从 `1 000` 改 `1000`，标题同时 trim | 字符串相似不证明分组/千位含义，超出唯一字段；需 exact 原文及数值文法证据 |
| 单位缩放 | raw_unit 从 万元改 元，normalized_value 仍100 | Q 已变化且可能差10000倍；S grade、content_hash、parser-v2 不提供转换证明 |
| 否定/标题语义 | 标题“未获批准”改“已获批准”，display_text 不变 | 改变可见命题；原 text 一致不能授权 title 改义 |
| 特殊空白 | 标题 `营业收入` 后 U+00A0 或 tab 被 strip；或正文内部换行被折叠 | 不属于尾 U+0020；渲染语义未批准，不能用宽泛 strip |
| 来源/locator | P 引用 source A/v1/p.12；N 同 hash 字符串但改 A/v2/p.13 | exact source/locator 变更，旧 bytes hash 不证明新位置支持同一命题 |
| 期间/时效 | period_end 从2026-06-30改12-31，或 effective_to 清空 | identity/有效性变化；ordinary replacement 不等于 trusted 许可 |
| exact support | DERIVED 的支持 V1+V2 改 V1+V3，所有来源均 S/VERIFIED | identity/origin 与依赖命题变化；窄候选排除该 provenance/path |
| 错误旧版本 | P VERIFIED、rule=legacy-historical-rule，但 locator 实际页不含32.5% | Q(N)=Q(P) 只能复制错误；无 G2 仍必须拒绝，不能从历史标签提升 |
| 撤回/冲突 | source latest RETRACTED，P 旧 exact source ACTIVE；或有关联 CONFLICTS_WITH | 旧 grade/status 不覆盖新失效证据；窄资格 fail closed，不裁决冲突 |

## 7. 后续真实 PostgreSQL 小切片测试计划（本轮未执行）

只在 G1–G4 全部具体化、用户另行批准并派发实现后才允许下面 trusted positive。G2 不能以 fixture string/hash/人工 seed/monkeypatch 的 semantic=true 满足。假如 G2 需要尚未实现的原文/artifact 验证设施，应先另行只读规格任务，不把它塞入服务小切片或制造成功路径。

基础向量：以明确的 source-backed FACT/INSTRUMENT、S 合法 source 类型、PAGE exact locator，raw_value=`32.5%`、raw_unit/normalized_unit=`percent`、normalized_value=Decimal('32.5')、display_text=`2026H1 毛利率为32.5%`、period=2026H1、as_of=2026-08-31、command time=2026-09-16 UTC、actor=USER。源原文必须独立支持该命题并满足获批 G2；当前 synthetic fixture 不满足此要求。标题用转义表达为 `强瑞技术 2026H1 毛利率\u0020\u0020`，不能在文档中保留实际行尾空格。

| 向量 | 命令与输入 | 预期/前置 |
| --- | --- | --- |
| P0 ordinary/review control | 无 rule correction 后 request_review → verify_or_reject，保留服务返回的全部 exact IDs | UNREVIEWED→PENDING_REVIEW→VERIFIED；rule=None；是现有合法路径，不证明 G2/positive trusted |
| P1 conditional trusted positive | 全部 G1–G4 成立，same-series 明确 ID 和只改变尾两 U+0020 的标题 | 新 exact N+1、VERIFIED、完整 CORRECTION、唯一严格 audit；Q 全一致。当前同请求只能 unapproved_rule 拒绝 |
| P2 exact preserved optional values | 与 P1 相同，但采用获批 G2 覆盖的 null currency/normalized_text_value/effective_to，命令省略这些字段 | null 原样保留；不得猜 currency/时间。若 G2 不覆盖，明确拒绝；不从 P1 泛化 |
| N1 malformed/unknown rule | omitted、None 为 ordinary 对照；`''`、空白、未知、ID uppercase、int/bool/bytes/list/mapping/set/object 为 negative | 非 None 精确 stable domain error/type/path/raw value/reason；不是任意 Exception |
| N2 field contamination | P1 的标题变换加 raw32.5→33、unit变更、normalized缩放、currency变更、as_of刷新、effective清空，逐个参数化 | 每个单字段差异拒绝；numeric/时间不以 canonical hash 相同通过 |
| N3 title boundary | 删除内部/前导空格、NBSP/tab/换行、空标题、原标题无尾 ASCII space 的 no-op、换词 | 不属于窄变换，拒绝；合法 fixture setup 必须在 baseline 前完成 |
| N4 source/locator/semantic | exact source 缺失/变化，对象缺失或错 bytes、quote不支持值、parser bounds与对象不对应、latest撤回/替代、冲突 | 命中具体已冻结检查和 reason；不能把证据装配失败当业务拒绝 |
| N5 prior qualification | UNREVIEWED/PENDING_REVIEW/DISPUTED/REJECTED/INVALIDATED/RETRACTED、old exact 非 highest、F grade、MANUAL/DERIVED/CROSS_INSTRUMENT、有关系 prior | 窄 trusted 不准入；ordinary 全 from-status 表保持另外任务 |
| N6 unsupported routes | automatic 更换真实不同 VERIFIED exact support；direct 改 metric；underlying 有 predecessor 改 identity；underlying 无 predecessor initial | 全部不受 v1授权；实际生产命令拒绝，ordinary R1B routing 对照保留 |
| H1 legacy/history | constraint-legal 完整 append-only legacy seed，仅历史保护用途，先 commit；ordinary omitted/None 与 trusted negative 分开 | P legacy rule/status/全部列与 children 永不改变；新 ordinary rule=None，不清旧 rule |
| R1 replay | 成功请求 caller commit，另 session 以同 key/同 payload 重放；ordinary key 加新 trusted请求；变 payload 同 key | 同 exact response 无新行/audit；新请求不能被吞；冲突按实际 stable code，保留现 replay 合同 |

每个 negative 都在 **fixture/G2 合法装配及 setup commit 完成后**取 baseline。通过正常权限使用现有127.0.0.1:15432 disposable fixture；不得重定向或新建替代实例。命令调用后断言指定 domain validation，检查本命令没有 pending new/dirty；caller 仍 commit，关闭 caller，再用独立 fresh session 读取九表全部行和全部列比较：source_document、source_document_version、evidence_series、evidence_version、source_locator、instrument_link、derivation_link、idempotency、audit；另独立核对 corroboration 全历史行。不能只用 count/hash，不能以 rollback 隐藏写入。

Positive caller commit 后 fresh reader 必须验证完整 Q、exact supersedes/N+1、new child IDs 与旧 ID 分离、所有旧版本/children/关系保持原样、new audit 与已知 actor/time/payload 精确一致、current/latest-first 无 fallback。Negative fresh reader 要证明无 series/version/children/idempotency/audit 新残留且 current/exact 仍原样；每一被拒路径都独立覆盖。Replay fresh reader 验证全 durable rows 与第一次提交后相同。使用服务实际返回的 exact IDs，不假设 initial FACT 的 predecessor；automatic setup 可用 ordinary correction→request_review→verify_or_reject 构造另一个真实 VERIFIED support，必须在 negative baseline 前提交。

后续实现先 focused 真正业务 RED，后最小 GREEN；权限/fixture/G2 装配错误不是 RED。独立验收与实现执行者逻辑分离，不弱化旧 verifier。保留 focused、五份固定原 verifier、ORACLE-R1 58 场景、full Evidence service、persistence/migration/Research regression、Ruff/format/mypy/compileall/Alembic heads/diff/status/hash 全矩阵，另加独立 named-rule verifier。空 allowlist 环境检查在将来政策启用时如有矛盾，应先取得单独版本化 verifier 合同，旧文件不改；当前没有这种授权。本轮未运行任何矩阵，历史通过数不能作为本规则结果。

## 8. 待用户审批与后续实施提示词边界

待审批事项依次为：是否有足够价值继续此唯一标题候选；是否接受窄 same-series/FACT/SOURCE_BACKED/INSTRUMENT/S/PAGE、无关系 prior 和严格字符等价范围；明确 G1 展示语义；给出 G2 权威原文/对象/artifact 来源及逐字段验证谓词和证据所有权；批准 G3 当前 source/窗口/冲突拒绝范围；完整规则定稿后才决定是否及何时启用。任何 source-state 扩张、绕过 frozen 完整语义要求或启用未经验证事实的方案均不能由执行者默许。推荐当前保持空生产批准集合，批准下一步只读 readiness 调查，而非 activation。

采用 ai-task-prompt-architect 的最小提示词结构。下面是 **条件模板，不是派发、不具备可执行正向授权**；G2 缺口不得变成实现者自行决定的谓词。当前下一步应由用户/dispatcher 明确原文与标题语义资料后另派只读规格任务，仍不实现 registry。

> 仅当用户已经批准完整、版本化规则定义（含 G1–G4 的可重验全部证据及谓词）并由 dispatcher 另发 SMALL repair/implementation contract 时：实现唯一批准的 tg.tc.display-title-ascii-tail.v1 的私有确定性 validator/admission。先读冻结合同与独立验收并核对新合同规定的 HEAD/status/保护 SHA；本草案的 HEAD 不能自动当未来起点。只允许新合同列出的最小文件，先加 focused 真实 PostgreSQL tests 取得业务 RED，再最小修改达到 GREEN。支持仅 same-series；automatic/direct/underlying create 均须明确拒绝该新 trusted 请求，不能注入任意规则或公共绕过。逐字段验证 exact prior/source/locator、获批原文语义证据、完整 status/audit，任何证据缺失或未知字段 fail closed 且验证先于本命令持久化。普通 omitted/None 不继承，保护 legacy 历史、children、exact lineage 与既有 replay/状态表。使用既有本地15432 disposable fixture和正常权限，三个 admin/diagnostic变量未设置；caller commit/fresh-session positive/negative/no-residue/history/replay 与完整回归证据齐备后仅报告 IMPLEMENTATION_COMPLETE 或 BLOCKED，交独立验收。若必须新造原文设施、改 schema/API/frozen合同/旧verifier或合并 R1D，立即 BLOCKED，由 dispatcher 单独切片。禁止 Git integration，禁止自行扩展 policy 或宣布全 R1C/WP04-02 完成。

提示词自检：目标只有一条已批准窄规则；输入必须包含完整权威证据和固定新基线；范围由后续合同显式限定；验证有真实 RED/GREEN、独立/fresh-session 和全回归；前置不齐时停在规格而非假实现。因此本草案的交付结论为 NOT_READY，正向 trusted registry/validator、initial import 资格、ordinary correction 完整资格表、R1D 与最终 WP04-02 独立全量验收仍未完成。
