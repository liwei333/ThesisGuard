# 论衡 ThesisGuard V1 产品需求文档（PRD）

> 文档版本：V1.0 Draft  
> 日期：2026-09-12  
> 产品名称：论衡 ThesisGuard  
> 产品定位：个人交易研究与决策系统  
> 对应原型：ThesisGuard V3.4 Visual Interaction Review Prototype  
> 对应技术文档：ThesisGuard V1 Technical Architecture Design  
> 状态：Ready for Product Review

---

# 1. 文档目的

本文档用于统一 ThesisGuard V1 的产品目标、范围、交互边界、业务规则、核心对象、功能需求、验收标准与开发优先级。

ThesisGuard V1 不是：

- 股票资讯 App
- K 线软件
- 券商研报阅读器
- 股票评分器
- 财经新闻聚合器
- 聊天机器人套壳
- 自动交易机器人
- “预测明天涨跌”的 AI

ThesisGuard V1 要解决的是：

> 用户为什么买入一只股票？
>
> 这个理由现在是否仍然成立？
>
> 哪些新事实正在支持或破坏原来的判断？
>
> 市场已经提前交易了多少预期？
>
> 当前赔率是否仍然值得下注？
>
> 如果判断错误，应该在哪里认输？
>
> 交易结束以后，原判断究竟错在哪里？

ThesisGuard 的核心产品对象不是“股票”，而是：

# Thesis

也就是：

> 用户对一只标的建立的、可被证据持续验证或证伪的投资逻辑。

---

# 2. 产品愿景

## 2.1 产品愿景

帮助个人投资者建立一套：

```text
研究有证据
判断有版本
买入有计划
持仓有验证
错误有退出
交易有复盘
```

的个人交易决策体系。

---

## 2.2 核心品牌表达

中文：

> 建立逻辑。  
> 持续验证。  
> 发现变化。  
> 管理风险。

英文：

> Build the thesis.  
> Test the thesis.  
> Guard the downside.

---

## 2.3 产品长期方向

长期 ThesisGuard 应从：

```text
个人交易研究工具
```

发展为：

```text
个人投资决策操作系统
```

系统持续积累：

- 公司研究
- Thesis 历史
- Evidence 历史
- 机构预期历史
- 市场状态历史
- Trade Plan 历史
- 实际交易历史
- 纪律违约历史
- 用户行为模式

最终形成真正符合用户自身能力圈、风险偏好和交易习惯的个人交易模型。

---

# 3. 用户画像

## 3.1 核心用户

V1 核心用户：

> 有一定投资经验、会主动研究公司和行业，但缺乏稳定交易系统的个人投资者。

典型特征：

- 自己会研究产业逻辑
- 会看财报、订单、行业趋势
- 会使用 AI 辅助研究
- 同时做中短线 / 波段
- 容易被盘中波动干扰
- 买入后容易忘记原始逻辑
- 不容易持续维护公司研究
- 研究资料分散
- 交易计划经常只存在脑子里
- 容易出现止损不坚决、追高、亏损加仓等行为

---

## 3.2 非目标用户

V1 不重点服务：

- 高频量化交易者
- 纯指数定投用户
- 完全不研究基本面的被动投资者
- 需要专业机构投研终端的大型机构
- 完全依赖技术指标做超短线的人
- 希望 AI 自动下单的人

---

# 4. 用户核心痛点

## 4.1 研究重复

每次重新问 AI：

> “强瑞技术怎么样？”

都会重新查一遍。

问题：

- 浪费时间
- 数据口径容易变化
- 上一次结论丢失
- 无法看到“观点变化过程”

---

## 4.2 研究无法持续

很多投资者会在买入前认真研究。

但买入后：

> 不再持续验证。

最终变成：

> “我记得它以前逻辑挺好的。”

---

## 4.3 事实与观点混在一起

用户经常无法区分：

```text
公司事实
券商预测
市场传闻
自己的主观判断
AI 推断
```

导致：

> 把预测当事实。

---

## 4.4 市场已经 Price In

很多利好本身是真的。

但股票仍然会跌。

因为：

> 利好可能已经提前交易。

普通资讯工具通常只回答：

> “这个消息是利好。”

而不回答：

> “市场已经交易了多少？”

---

## 4.5 交易计划容易被事后修改

典型：

```text
原止损 96

跌到 96：

再等等。

改成 93。

跌到 93：

再等等。

改成 90。
```

最终：

> 原来的风险控制失效。

---

## 4.6 持仓过多

投资者容易：

> 这个不错买一点，那个也不错买一点。

最后变成：

> 持仓开超市。

无法真正跟踪。

---

## 4.7 市场情绪影响个股操作

即使选股逻辑正确：

> 市场处于高位退潮 / 恐慌杀跌

也可能导致短期巨大回撤。

所以：

> 公司逻辑 ≠ 当前允许的风险预算。

---

## 4.8 AI 容易迎合用户

如果用户说：

> “我觉得这只股票明天会涨。”

普通 AI 很容易顺着解释。

ThesisGuard 必须做到：

> 用户观点只是“用户假设”，不能自动成为事实。

---

# 5. 产品核心方法论

ThesisGuard V1 采用以下闭环：

```text
发现标的
↓
加入自选
↓
标的分类
↓
首次研究建档
↓
建立 Thesis
↓
Evidence 持续进入
↓
Thesis Validation
↓
机构预期变化
↓
Expectation Gap
↓
Price-In
↓
Bull / Base / Bear
↓
Market Regime
↓
技术买点
↓
冻结 Trade Plan
↓
执行
↓
Catalyst Validation
↓
持有 / 加仓 / 减仓 / 退出
↓
复盘
↓
Discipline
↓
个人模型更新
```

---

# 6. V1 产品范围

## 6.1 P0

V1 必须完成：

1. 自选池
2. 标的自动分类
3. Research Package
4. Evidence
5. Thesis
6. Thesis Validation
7. Thesis Health Ledger
8. Research 版本管理
9. Agent Read-Only 查询 / 解释 / 反驳
10. 增量研究更新

---

## 6.2 P1

V1 增强：

1. 机构研报 / 盈利预期
2. 一致预期历史
3. Bull / Base / Bear
4. Expectation Gap
5. Price-In
6. Trade Plan Freeze
7. Catalyst Validation
8. Bull vs Bear Agent

---

## 6.3 P2

后续增强：

1. Market Regime
2. 实时市场情绪
3. Portfolio
4. Discipline
5. 实时提醒
6. 同花顺 MCP
7. 券商账户同步

---

# 7. 核心业务对象

## 7.1 Instrument

表示：

- 股票
- ETF
- 指数
- 行业
- 事件篮子

---

## 7.2 Research Package

一个标的的完整研究档案。

首次加入自选：

> 全量生成。

后续：

> 增量维护。

---

## 7.3 Evidence

任何进入研究系统的信息都必须先成为 Evidence。

Evidence 必须包含：

- 内容
- 来源
- 日期
- 来源等级
- 信息类型
- 关联标的
- 验证状态

---

## 7.4 Thesis

一条可以被持续验证的投资判断。

例如：

> AI服务器液冷订单正在进入持续放量阶段。

Thesis 不是：

> “强瑞技术很好。”

---

## 7.5 Expectation

市场机构对公司未来经营数据的预测。

例如：

```text
2027E 净利润 6.1 亿
```

---

## 7.6 Valuation Scenario

```text
BEAR
BASE
BULL
```

每个场景包含：

- 盈利假设
- 估值假设
- 市值
- 股价空间
- 前提条件

---

## 7.7 Trade Plan

交易发生前建立的计划。

必须支持 Freeze。

---

## 7.8 Catalyst

未来需要验证 Thesis 的事件。

例如：

- Q3
- 年报
- 重大合同
- Rubin 发布
- FOMC
- 政策

---

# 8. 标的分类系统

加入自选以后，第一步不是生成长报告。

而是：

> 判断这只股票应该用什么模型研究。

分类：

## 8.1 INSTITUTIONAL_TREND

核心：

```text
产业
订单
收入
利润
现金流
一致预期
估值
机构资金
趋势
```

---

## 8.2 HOT_MONEY

核心：

```text
题材强度
板块梯队
龙头地位
换手
封板质量
连板基因
市场记忆
情绪周期
```

禁止强行套：

```text
2027 PE
```

---

## 8.3 HYBRID

同时存在：

- 真实产业逻辑
- 热点情绪资金

需要分别分析。

---

## 8.4 EVENT_DRIVEN

例如：

- 重组
- 涨价
- 大合同
- 政策
- 大客户认证
- 突发事件

---

# 9. 自选池

## 9.1 加入自选

入口：

```text
输入股票代码 / 名称
```

系统执行：

```text
证券识别
↓
分类
↓
判断是否已有 Research Package
↓
无 → 首次全量建档
有 → 读取当前 Research State
```

---

## 9.2 自选列表字段

机构趋势型：

```text
标的
分类
研究分
Expectation Trend
Thesis Health
Price-In
Risk / Reward
最后更新时间
Agent Action
```

游资型：

```text
标的
题材
梯队
情绪分
市场记忆
换手
主动性
Agent Action
```

---

## 9.3 ACTIVE / STALE

Research 必须有状态：

```text
ACTIVE
STALE
UPDATING
FAILED
```

STALE 不允许静默显示旧结论为最新结论。

---

# 10. Research Package

建议包含：

```text
公司基本信息
主营业务
收入结构
客户结构
竞争格局
产业链
行业景气
订单
合同负债
存货
应收
现金流
扩产
重大项目
管理层
机构预期
估值
风险
催化
Thesis
```

---

# 11. Evidence 体系

## 11.1 信息类型

所有重要内容必须明确属于：

```text
【事实】

【机构预测】

【论衡推断】

【用户假设】
```

---

## 11.2 来源等级

```text
S
公司公告 / 财报

A
交易所 / 监管 / 官方数据

B
公司投资者交流 / 机构调研

C
券商研报

D
权威财经媒体

E
雪球 / 微博 / 公众号 / 社交媒体

F
传闻 / 未验证消息
```

---

## 11.3 F 级限制

F 级：

> 不得直接支持核心 Thesis。

只能进入：

```text
待验证情报池
```

---

## 11.4 Evidence UI

示例：

```text
【事实】【S】

2026H1 AI服务器业务收入同比增长160%

来源：
2026半年报

日期：
2026-08-XX
```

---

# 12. Thesis 系统

## 12.1 Thesis 创建

Thesis 可以来源于：

- 用户创建
- Agent 建议
- Research Package 自动生成候选

Agent 生成必须由用户确认后进入正式 Thesis。

---

## 12.2 Thesis 示例

```text
AI服务器液冷订单持续增长

订单开始向收入兑现

收入开始向利润兑现

利润增长可以转化为现金流

2027E盈利存在进一步上修空间
```

---

## 12.3 Thesis 状态

```text
SUPPORTED
NEUTRAL
WEAKENING
INVALIDATED
PENDING
```

---

## 12.4 Thesis Detail

点击后必须看到：

```text
Thesis

建立日期

当前状态

支持证据

反对证据

待验证

失效条件

最近一次变化

历史版本
```

---

# 13. Thesis Health

## 13.1 禁止黑盒

禁止：

```text
AI：我觉得 84 分。
```

---

## 13.2 Score Ledger

UI：

```text
Thesis Health

78 → 84 ↑

本次变化 +6

+3 Q3订单证据增强
+2 两家券商上调盈利预测
+2 收入增长加速
-1 经营现金流仍偏弱
```

---

## 13.3 Health 作用

Health 不是：

> 买卖信号。

而是：

> 当前 Thesis 相对建立时发生了什么变化。

---

# 14. 机构预期系统

## 14.1 一致预期

至少展示：

```text
2026E Revenue
2026E Profit

2027E Revenue
2027E Profit

2028E Profit
```

---

## 14.2 预期历史

例如：

```text
5月 4.2
6月 4.5
7月 5.0
8月 5.6
9月 6.1
```

必须可以看到趋势。

---

## 14.3 机构变化

```text
90天变化
30天变化

新增覆盖机构

上调
维持
下调
```

---

## 14.4 机构分歧

不要只展示：

```text
买入评级
```

而应该展示：

```text
机构
利润预测
核心假设
主要风险
```

最终 Agent 总结：

> 主要分歧来自哪里？

---

# 15. Expectation Gap

## 15.1 定义

比较：

```text
盈利预期变化
股价变化
估值变化
```

---

## 15.2 状态

```text
巨大正预期差
正预期差
基本匹配
预期已充分
负预期差
```

---

## 15.3 必须解释

例如：

```text
过去 30 天

盈利预期 +13%
股价 +27%
估值 +11%

结论：

股价上涨速度高于盈利预期上修，
短期正预期差正在收敛。
```

---

# 16. Price-In

## 16.1 核心问题

不是：

> 这是利好吗？

而是：

> 市场已经交易了多少？

---

## 16.2 UI

```text
Price-In

78%

已计价

Rubin需求
AI服务器资本开支
Q3订单增长

尚未充分计价

毛利率持续改善
2027利润进一步上修
```

---

## 16.3 输出

```text
产业逻辑：强

基本面：改善

市场预期：高

短期赔率：下降
```

---

# 17. Bull / Base / Bear

机构趋势型必须支持。

---

## 17.1 BEAR

包含：

- 利润
- PE
- 市值
- 空间
- 前提

---

## 17.2 BASE

同上。

---

## 17.3 BULL

同上。

---

## 17.4 Risk / Reward

必须展示：

```text
Downside
Base
Bull

Bull / Bear
```

---

## 17.5 禁止表达

禁止：

> “目标价一定到 213。”

正确：

> “在 Bull 假设成立、盈利达到 X、市场给予 Y PE 的情况下，对应市值 Z。”

---

# 18. Market Regime

## 18.1 状态

```text
恐慌杀跌
情绪冰点
修复反弹
正常活跃
加速活跃
亢奋极值
高位退潮
```

---

## 18.2 Market Regime 的作用

Market Regime：

> 决定风险预算。

不决定：

> 买哪只股票。

---

## 18.3 核心原则

```text
情绪冰点 ≠ 自动底部
```

以及：

```text
亢奋 ≠ 立刻卖空
```

---

# 19. 技术买点

V1 不做复杂技术分析系统。

机构趋势型默认：

```text
日线 = 判断能否参与

60分钟 = 判断买入时机

30分钟 = 辅助确认

分时 = 执行
```

---

## 19.1 V1 支持两类买点

```text
趋势回踩

突破回踩
```

---

# 20. Trade Plan

## 20.1 必填字段

开仓前：

```text
标的

买入理由

买入区

初始仓位

加仓条件

止损

失效条件

Base Target

Bull Target
```

---

## 20.2 Freeze

按钮：

```text
冻结计划
```

Freeze 后：

```text
PLAN-v1
```

不可直接覆盖。

---

## 20.3 修改止损

例如：

```text
96 → 90
```

系统必须提示：

```text
风险扩大

你正在扩大原始交易风险。
```

要求：

```text
填写修改原因
```

然后生成：

```text
PLAN-v2
```

---

# 21. Catalyst Validation

## 21.1 Catalyst 不是日历

每个 Catalyst 必须回答：

> 这次事件要验证什么？

---

## 21.2 示例

```text
强瑞 Q3

需要验证：

□ 单季度收入 ≥ X
□ 净利润 ≥0.8亿
□ 毛利率 ≥ X
□ 经营现金流改善
□ 应收增速 < 收入增速
```

---

## 21.3 财报发布

系统自动：

```text
完成 4 / 5
```

然后重新评估：

```text
Thesis Health
```

并输出：

```text
动作：
继续持有
暂不加仓
```

---

# 22. Bull vs Bear

## 22.1 快捷入口

```text
反驳我的逻辑
```

---

## 22.2 输出结构

左：

```text
Bull
```

右：

```text
Bear
```

底部：

```text
论衡裁决
```

---

## 22.3 论衡裁决

必须区分：

```text
确定事实

合理推断

证据不足

主要争议
```

---

# 23. Portfolio

## 23.1 最大持仓

默认：

```text
4
```

---

## 23.2 第 5 只

必须：

```text
Position Replacement PK
```

问题：

> 新股票比当前哪一只更值得占据仓位？

---

## 23.3 相关性

不能只看：

```text
4只股票
```

需要看：

```text
共同风险因子
```

例如：

```text
AI算力 55%
PCB 18%
存储 14%
现金 13%
```

---

# 24. Discipline

记录：

```text
追高
止损延迟
亏损补仓
计划外交易
仓位违规
```

---

## 24.1 结果与纪律分离

即使：

> 一次违规交易最后赚钱。

依然：

```text
纪律违规
```

不能因为结果好就奖励错误流程。

---

# 25. Agent

## 25.1 Agent 定位

Agent 不是股票预测器。

Agent 是：

> ThesisGuard 的自然语言操作层和推理层。

---

## 25.2 Agent 默认上下文

自动加载：

```text
Market Regime

Portfolio

Instrument Research

Current Thesis

Trade Plan

Catalyst

Discipline
```

---

## 25.3 快捷操作

```text
解释 Thesis

反驳我的逻辑

最近发生了什么变化？

机构为什么上调？

现在 Price-In 多少？

重新计算 Bull/Base/Bear

检查交易计划

执行买入前五问
```

---

## 25.4 Agent 独立性

用户说：

> 我觉得强瑞一定会涨。

系统记录：

```text
【用户假设】
```

Agent 不得：

> 自动提高 Thesis Health。

---

# 26. 买入前五问

每笔交易必须能够回答：

```text
1. 我为什么买？

2. 市场现在低估什么？

3. 为什么是今天买？

4. 错了在哪里认输？

5. 对了准备赚多少？
```

任何一项答不上：

> 建议不交易。

---

# 27. 首页驾驶舱

首页目标：

> 用户打开 ThesisGuard 后 30 秒内知道今天该做什么、不该做什么。

---

## 27.1 第一层

```text
市场风险
仓位闸门
组合风险
纪律风险
```

---

## 27.2 第二层

```text
当前持仓 Thesis
Agent 今日优先级
```

---

## 27.3 第三层

```text
机会池
热点 / 新闻 / 政策
```

---

## 27.4 第四层

```text
Catalyst
模型状态
知识库状态
```

---

## 27.5 Agent Priority

优先显示：

```text
Thesis 发生变化

Price-In 明显变化

Frozen Plan 状态

机构预期变化

Catalyst 临近

纪律风险
```

而不是普通资讯。

---

# 28. Research Knowledge Base

## 28.1 数据类型

```text
FACT
ESTIMATE
THESIS
EVENT
REPORT
PRICE_SIGNAL
TRADE_PLAN
```

---

## 28.2 版本

必须可以查看：

```text
v1
v2
v3
```

---

## 28.3 原则

```text
新数据不会修改过去历史
```

而是：

```text
生成新版本
```

---

# 29. 页面结构

V1 一级导航继续保持克制：

```text
总览

自选池

持仓

研究库

新闻 / 政策

市场情绪

Agent

纪律

设置
```

不因为新增功能继续增加一级菜单。

---

# 30. 主要页面

## 30.1 Dashboard

目标：

> 决策驾驶舱。

---

## 30.2 Watchlist

目标：

> 发现哪些标的正在发生变化。

---

## 30.3 Stock Workspace

这是产品最核心页面。

必须集中展示：

```text
价格 / 基本状态

Thesis Health

Thesis Validation

Evidence

Expectation

Expectation Gap

Price-In

Valuation

Trade Plan

Catalyst

Bull vs Bear
```

---

## 30.4 Portfolio

目标：

> 风险与容量管理。

---

## 30.5 Research Knowledge

目标：

> 研究资产管理。

---

## 30.6 Market Regime

目标：

> 风险预算。

---

## 30.7 Agent

目标：

> 查询、解释、反驳、复盘。

---

# 31. 关键状态机

## 31.1 Research

```text
CREATED
↓
BUILDING
↓
ACTIVE
↓
STALE
↓
UPDATING
↓
ACTIVE
```

失败：

```text
FAILED
```

---

## 31.2 Thesis

```text
PENDING
SUPPORTED
NEUTRAL
WEAKENING
INVALIDATED
```

---

## 31.3 Trade Plan

```text
DRAFT
FROZEN
REVISED
CLOSED
```

---

## 31.4 Catalyst

```text
PENDING
ACTIVE
VALIDATING
COMPLETED
FAILED
```

---

# 32. 通知

## P0

```text
Thesis INVALIDATED

止损触发

持仓超限

重大公司风险
```

---

## P1

```text
一致预期明显下修

Price-In 快速上升

Catalyst Fail

Frozen Plan 即将失效
```

---

## P2

```text
新研报

新闻

研究模块 stale
```

---

# 33. 数据时间戳

所有结论必须显示：

```text
Source Date

Last Verified

Generated At
```

---

# 34. 搜索

统一搜索：

```text
股票
Research
Thesis
Evidence
新闻
政策
```

---

# 35. V1 产品成功指标

V1 不以：

> 赚钱多少

作为产品研发期 KPI。

优先指标：

## 35.1 Research Reuse Rate

用户查询一个已研究股票时：

> 多少次无需重新全量 Research。

---

## 35.2 Thesis Traceability

核心 Thesis：

> 100% 能追到证据。

---

## 35.3 Plan Freeze Rate

真实交易：

> 有多少笔在成交前 Freeze Plan。

---

## 35.4 Plan Violation Detection

系统能识别：

> 止损下移、计划外加仓等。

---

## 35.5 Catalyst Closure

创建的 Catalyst：

> 是否最终有验证结果。

---

## 35.6 Research Freshness

Research：

> 是否及时发现 stale。

---

# 36. 非功能要求

## 性能

普通页面：

```text
< 2 秒
```

普通 API：

```text
P95 < 500ms
```

复杂 Agent / Research：

> 异步 + 进度反馈。

---

## 可追溯

任何：

```text
Thesis
Estimate
Trade Plan
```

必须可追溯：

```text
来源
版本
时间
修改原因
```

---

## 安全

API Key：

> 加密。

---

## 可用性

V1：

> 桌面优先。

移动端：

> 可以后续独立适配。

---

# 37. 风险

## 37.1 数据授权

最大风险之一：

> 研报与行情的数据授权。

---

## 37.2 LLM 幻觉

解决：

> Evidence First。

---

## 37.3 黑盒评分

解决：

> Score Ledger。

---

## 37.4 过度产品化

风险：

> 一开始做太多功能。

解决：

> P0 只跑 Thesis 黄金链。

---

# 38. V1 明确不做

```text
自动下单

自动卖出

自动资金划转

高频策略

全市场选股 AI

收益承诺

自动跟单

复杂量化回测平台

社区
```

---

# 39. P0 黄金链

P0 开发只验证：

```text
加入自选
↓
自动分类
↓
首次建档
↓
Evidence
↓
Thesis
↓
Thesis Validation
↓
新 Evidence
↓
Score Ledger
↓
为什么发生变化
```

---

# 40. P0 用户故事

## US-001 加入标的

作为用户，

我希望：

> 输入强瑞技术并加入自选，

系统：

> 自动完成分类和建档。

---

## US-002 查看 Thesis

作为用户，

我希望：

> 查看为什么系统认为它值得研究。

---

## US-003 查看 Evidence

作为用户，

我希望：

> 知道每个判断来自什么来源。

---

## US-004 增量更新

作为用户，

我不希望：

> 每次重新研究。

系统应该：

> 基于新信息更新旧 Research。

---

## US-005 Thesis 变化

作为用户，

我希望：

> 系统告诉我“哪些新事实改变了判断”。

---

## US-006 查看历史

作为用户，

我希望：

> 查看 Thesis 的历史版本。

---

# 41. P1 用户故事

## US-101 机构预期

我希望知道：

> 机构最近是否在持续上调盈利预测。

---

## US-102 Price-In

我希望知道：

> 利好是不是已经被股价提前交易。

---

## US-103 Valuation

我希望：

> 同时看到 Bear/Base/Bull，而不是一个目标价。

---

## US-104 Trade Plan

我希望：

> 买入前冻结交易计划。

---

## US-105 风险修改

如果我事后下调止损，

系统：

> 必须警告我正在扩大风险。

---

## US-106 Catalyst

我希望：

> 财报发布以后自动验证之前设定的条件。

---

# 42. 验收标准

## AC-01

可以：

```text
加入 301128
```

---

## AC-02

可以看到：

```text
Research ACTIVE
```

---

## AC-03

至少生成：

```text
3–5 条 Thesis
```

---

## AC-04

每条 Thesis 至少有：

```text
支持证据
待验证
失效条件
```

---

## AC-05

每条 Evidence：

> 有来源等级。

---

## AC-06

模拟新 Evidence 后：

```text
Thesis 78 → 81
```

并显示原因。

---

## AC-07

旧版本仍然存在。

---

## AC-08

Agent 可以回答：

> 为什么看好？

---

## AC-09

Agent 可以回答：

> 哪些事实改变了判断？

---

## AC-10

Agent 可以：

> 反驳用户观点。

---

# 43. P1 验收

必须看到：

- 机构盈利预测趋势
- Broker Difference
- Expectation Gap
- Price-In
- Bull/Base/Bear
- Frozen Plan
- Plan Version
- Catalyst Validation
- Bull vs Bear

---

# 44. 设计原则

ThesisGuard 的 UI 固定遵守：

```text
高信息密度

高效率

强扫描性

不杂乱

不参差
```

---

## 44.1 栅格

使用稳定栅格。

禁止：

> 自由拼贴。

---

## 44.2 卡片

同层：

> 尽量等高。

---

## 44.3 表格

重复数据：

> 表格优先。

---

## 44.4 颜色

```text
紫色：
品牌 / 系统

绿色：
健康 / 支持

橙色：
风险 / 待验证

红色：
失效 / 警告
```

---

## 44.5 禁止

- 霓虹
- 大量渐变
- 游戏化
- 巨大数据卡
- Emoji 泛滥
- 深色 Bloomberg 风

---

# 45. 开发阶段

## Phase 1

```text
WP-01 工程骨架
```

---

## Phase 2

```text
WP-02 Instrument + Watchlist
```

---

## Phase 3

```text
WP-03 Research Package
```

---

## Phase 4

```text
WP-04 Evidence
```

---

## Phase 5

```text
WP-05 Thesis Engine
```

---

## Phase 6

```text
WP-06 Thesis Validation UI
```

---

## Phase 7

```text
WP-07 Read-Only Agent
```

---

## Phase 8

```text
WP-08 Incremental Update
```

P0 完成。

---

# 46. P1 开发阶段

```text
WP-09 Expectation Engine

WP-10 Valuation

WP-11 Expectation Gap / Price-In

WP-12 Trade Plan

WP-13 Catalyst

WP-14 Bull vs Bear
```

---

# 47. P2

```text
Market Regime

Portfolio

Discipline

Realtime

Tonghuashun MCP

Broker Sync
```

---

# 48. 开放问题

当前需要后续确认：

1. 首版证券基础数据源
2. 财报数据源
3. 研报授权与抓取方式
4. 一致预期来源
5. 实时市场情绪来源
6. 是否接同花顺 MCP
7. 券商账户同步方案
8. 用户是否需要多账户
9. 国内 / 海外资产支持边界
10. 是否支持桌面客户端

---

# 49. 产品最终验收问题

系统必须可以回答以下问题：

## Q1

> 我为什么买？

---

## Q2

> 这个理由现在还成立吗？

---

## Q3

> 哪些新事实让判断发生变化？

---

## Q4

> 机构预期是在上调还是下调？

---

## Q5

> 股价已经 Price In 多少？

---

## Q6

> Bear/Base/Bull 分别是什么？

---

## Q7

> 如果我错了，在哪里认输？

---

## Q8

> 我的交易计划有没有被我偷偷修改？

---

## Q9

> 这次 Catalyst 验证了什么？

---

## Q10

> 这笔交易最终错在哪里？

---

# 50. 一句话产品定义

> 论衡 ThesisGuard 是一个以投资 Thesis 为核心，通过结构化事实、可追溯 Evidence、机构预期变化、情景估值、不可变交易计划与持续事件验证，帮助个人投资者形成可解释、可复盘、可迭代交易决策体系的个人投资操作系统。

