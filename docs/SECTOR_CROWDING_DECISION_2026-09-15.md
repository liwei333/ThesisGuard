# Sector Crowding 阶段与后续任务决策

Decision ID: `ADR-2026-09-15-SECTOR-01`

Date: 2026-09-15

Status: `APPROVED — DEFERRED`

Authority: 用户在专项只读评估后明确要求“记录一下，把这个作为后续的开发任务”。本记录批准的是需求入库、延后时点和派发约束，不批准现在实现、数据采购或修改冻结策略。

## 1. 决策

主推荐采用方案 C：暂缓正式实现 Sector Crowding Score，优先完成现有 Evidence / Thesis 和最小确定性风险闭环。

产品价值高，但增量交易效果仍为 `UNPROVEN`。截至本次静态评估，Market / Intelligence / Agent 仅有占位入口；没有正式 Market Provider、行情时间序列、Sector 模型、历史成员、板块聚合或计算快照。Instrument 的 sector / industry 字符串不能替代上述能力。

评估快照：local main `7d4e395d949d8cd050548347f31dd6b492f65834`；WP04-02 候选分支 `codex/wp04-02-evidence-domain-service`，HEAD `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`。这是 2026-09-15 的静态快照，不是未来实时状态或生产证明。

## 2. 后续需求登记

- Backlog key: `BACKLOG-SECTOR-CROWDING-01`，仅用于需求追踪，不是新增 canonical WP。
- Candidate task label: `Market Sector Crowding Shadow MVP`，后续派发时再确定非冲突 Task ID。
- State: `PLANNED / DEFERRED / NOT_DISPATCHED`。
- Owner boundary: Market Domain 确定性计算；Intelligence 组织提示；Agent 只读解释；Trade Plan / Risk Gate 只使用获批规则和确切快照。
- Target user: 个人 A 股科技产业趋势波段交易，典型持有期 2 周—3 个月。
- Job: 辅助识别趋势有效但参与热度、交易一致性或价格延伸已经偏高的入场环境。
- Non-goal: 预测顶部、证明资金净流入或真实持仓集中度、保证盈利、自动买卖、低拥挤自动买入。

## 3. 重审与实施前置门

按依赖顺序：

1. 关闭 WP04-02 有序修复及原任务独立复验，完成 WP04-03 API/OpenAPI、WP04-04 Research exact Evidence references 并验收集成。
2. WP-05 核心 Evidence-linked Thesis 落地。
3. WP-RISK-01 首个最小风险闭环具备可验证的账户、订单、计划/退出与 Market 读取边界；Market 数据链和冻结双指数门通过验证。不要求所有后续风险增强功能完成。
4. 明确行情 Provider 的合法使用范围、配额、字段、时效、交易日历、单位、复权及错误合同；日频历史可补数、修订和追溯。
5. Sector 稳定身份、分类体系/版本和供应商映射；成分具有当时有效及当时可知语义，或不可变观察快照。
6. 板块日频聚合、可解释 Strength、有效样本/覆盖率和历史窗口具备确定性验证证据。
7. 单独发布 Crowding 影子 MVP 合同；不因重审门满足而自动派发或启用策略。

最合理时点：WP-04 / WP-05 核心验收后，在 WP-RISK-01 最小闭环与 Market 数据基础成熟时重审；Sector 历史数据门通过后才实现影子指标。不等待完整 Agent、Macro 或所有 WP-08 功能，也不以两个指数已有行情替代成分级数据就绪。

## 4. 后续 MVP 候选（未冻结算法）

收盘后日频；优先四个观察量，前三个进入实验候选分数，第四个独立显示持续性：

1. 板块成交额 / 同口径全市场成交额的自身历史分位。
2. 有效成分股换手率中位数的自身历史分位。
3. 明确定义的板块价格序列相对 MA20 的正向延伸及历史位置。
4. 热度持续性、近数日变化与趋势，不重复加入权重。

前三类等权只可作为透明实验基线；不是获批生产权重。窗口、并列值处理、正向贡献映射、样本门、公式和展示分段需要后续合同及验证。

不直接接受 25/20/20/15/10/10 权重。5/10 日涨幅与 MA20 偏离、成交额与换手可能重复；广度首先解释趋势参与，不自动加成拥挤；涨停比例、Top-K 集中度与榜单持续性先做辅助解释并验证噪声。

## 5. 关键数据与治理约束

- Strength 与 Crowding 分开；低强度低拥挤不是自动潜伏机会，高强度高拥挤不是卖出命令。
- 优先历史分位和固定版本的滚动窗口；不硬编码金额、换手或 Crowding > 85 的买卖门。
- 当天/未来数据不进入历史参考窗口；MA20 等输入有预热要求。数据不足显示 UNKNOWN，不补零或暗中重分配缺失因子权重。
- 申万、同花顺、东财及概念分类不能仅按名称互换；一股多概念、成员变更、退市、停牌、ST、新股、涨跌幅制度、股本与复权口径必须版本化。
- 不用当前成员伪造历史；历史成员不可得时从观察日起前瞻积累，明确回测限制。
- 每个结果可拆回原始指标、数据/成员版本、as_of、获取/计算时间、质量、窗口、分位、贡献、公式版本与输入引用。
- 分数不是下跌概率；高成交不证明净流入，高/低成交不直接证明可成交性。
- Market 结构化历史存 PostgreSQL；必要原始对象按已有对象存储边界保存。无需为分数新建 Kafka、通用 Factor Engine、Feature Store、向量库或微服务。
- Provider/MCP 返回值必须经确定性标准化；MCP 是访问机制，不是许可证、SLA 或数据质量证明。
- 影子指标不修改冻结个人模型 v1.3 / 系统 v1.1。未来作为硬准入/退出规则必须另立策略版本、重演、前瞻验证并获用户批准。
- Agent 只解释结构化快照，不“感觉”或写入评分；已有持仓仍按冻结计划和退出规则管理。

## 6. 现在允许与不允许的行动

现在仅登记需求，并要求未来本来就要建设的 Market 数据合同考虑上述时点和追溯字段。不得据本记录创建空表、crowding_score 字段、Sector API、Agent Tool、Provider Router 或因子引擎骨架，不采购数据、不改变当前派发顺序。

重审证据应包括：数据质量与故障测试、同输入/版本确定性重算、当时可知数据重演、影子提示与无提示对照、追涨行为/回撤/错失趋势/扣费结果与维护负担。示例分数和一次漂亮回测不构成增量有效性的证明。

## 7. 参考与来源边界

- 项目产品和优先级依据：PRODUCT_GOAL_REALIGNMENT、canonical PRD/TAD；本记录不替代它们。
- [AKShare 官方文档](https://akshare.akfamily.xyz/data/stock/stock.html)提供行情和板块接口候选；项目接线、历史成员及许可仍需独立验证。
- [同花顺官方接口介绍](https://quantapi.51ifind.com/gwstatic/static/ds_web/quantapi-web/)与[官方 FAQ](https://quantapi.51ifind.com/gwstatic/static/ds_web/quantapi-web/help-center/faq.html)说明接口能力及账号/配额/时效边界；不构成本项目账号授权或可靠性验收。

## 8. 变更记录

2026-09-15：用户批准记录阶段评估，将 Sector Crowding 纳入延后需求；未实现业务代码，未授权当前开发。
