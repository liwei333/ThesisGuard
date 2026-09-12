# ThesisGuard Structured Output Contracts

> 状态：Proposed；当前代码未实现 Structured Output Gateway  
> 日期：2026-09-12  
> 原则：Prompt 不是合同；LLM 输出永远是 Proposal，不是业务事实

## 1. 目标

ThesisGuard 需要把模型输出从“看起来像 JSON 的文本”提升为可版本化、可验证、可追踪、可修复但不可静默降级的协议。它必须跨模型供应商稳定，允许 provider-native strict schema，但不依赖某个供应商的成功承诺。

端到端流水线：

```text
Contract Registry
  → provider capability negotiation
  → model request with exact schema/version
  → syntax parse
  → Pydantic v2 structural validation
  → semantic validation
  → domain validation + current version checks
  → ACCEPTED / REPAIRABLE / NEEDS_REVIEW / REJECTED
  → Domain Service commit (if authorized)
```

## 2. Contract Registry

每个合同由代码和生成的 JSON Schema 管理：

```text
contract_name
contract_version              # semver or monotonic integer
pydantic_model
json_schema
schema_hash
semantic_validator_version
domain_validator_name
minimum_provider_capability
repair_policy
owner_module
introduced_at / retired_at
```

运行中的 Step 固定 `contract_name + version + schema_hash`；部署新 schema 不改变已开始 Run 的预期合同。合同升级规则：

- 添加 optional field：minor；
- 改字段语义/枚举/required：major；
- 修描述但不改验证：patch；
- 旧版本至少保留到所有 active/checkpointed Run 结束或迁移。

## 3. 标准 Envelope

```json
{
  "contract": {
    "name": "EvidenceExtractionResult",
    "version": "1.0.0",
    "schema_hash": "sha256:..."
  },
  "runtime": {
    "session_id": "uuid",
    "run_id": "uuid",
    "run_revision": 3,
    "turn_id": "uuid",
    "step_id": "uuid",
    "model_provider": "provider-name",
    "model": "model-name",
    "prompt_template_version": "evidence.extract@1.2.0"
  },
  "result": {},
  "provenance": {
    "input_snapshot_id": "uuid",
    "source_refs": ["evidence-source:uuid"],
    "generated_at": "..."
  }
}
```

Envelope 由 Runtime 填充，模型只负责 `result`。不能让模型自报 model、run revision、source access 或 schema hash。

## 4. 三层验证

### 4.1 Structural Validation

由 Pydantic v2 负责：类型、required、enum、范围、长度、额外字段策略、discriminated union、日期/货币/百分比格式。默认 `extra='forbid'`；金额采用 decimal string + currency，避免 float 和单位歧义。

### 4.2 Semantic Validation

合同专用确定性规则，例如：

- 每个事实必须引用输入快照中真实存在的 `source_id` 和 locator；
- `period_start <= period_end <= as_of`；
- 同一指标单位一致；同比/环比基期存在；
- `confidence` 不能代替证据等级；
- Bull/Base/Bear 的关键假设互不矛盾且数值区间有序；
- Thesis 支持项、反证项、失效条件均非空；
- 引用不能指向模型未获授权读取的文档。

### 4.3 Domain Validation

由领域服务执行：

- Instrument 与对象存在；
- referenced Evidence/Research/Thesis version 当前可访问；
- run revision 未 stale；
- expected domain version 未冲突；
- market regime/risk rules 满足；
- append-only/versioning 规则满足；
- 操作的 policy 与 approval 有效。

通过 schema 不代表可以提交；domain validation 是最后写闸门。

## 5. Failure 与 Repair

| 状态 | 含义 | 动作 |
|---|---|---|
| `ACCEPTED` | 三层验证通过 | 可进入下一步；写入仍经 Domain Service |
| `STRUCTURE_INVALID` | 解析/schema 错误 | 允许一次只携带错误路径的 repair |
| `SEMANTIC_INVALID` | 数值、来源、约束错误 | 可修复者一次 repair；缺事实不得让模型编造 |
| `DOMAIN_CONFLICT` | version/policy/current state 冲突 | 不 repair 文本；重读领域状态并新 revision/replan |
| `STALE_REVISION` | 旧 Run 产物 | 审计保存，禁止应用 |
| `NEEDS_REVIEW` | repair 后仍不可靠或结果未知 | 展示给用户/运营，不入权威表 |
| `REJECTED` | 安全策略、未授权来源或不可恢复错误 | 终止该 proposal |

Repair 最多一次，温度低，输入只包含原结果、具体 validation errors、同一 schema 和必要原始来源片段；不允许扩大工具权限或偷偷补充来源。第二次失败进入 `NEEDS_REVIEW`。禁止 regex salvage、忽略 extra fields、自动填充关键财务数字。

## 6. Tool Output 合同

Tool 的 canonical result 与 LLM Proposal 使用同一 registry 原则，但由 Tool adapter 负责产出：

```json
{
  "tool_call_id": "uuid",
  "tool_name": "evidence.search",
  "tool_version": "1.0.0",
  "output_schema": "EvidenceSearchResult@1.0.0",
  "status": "SUCCEEDED",
  "data": {},
  "source_refs": [],
  "observed_at": "...",
  "fresh_until": "...",
  "truncated": false,
  "warnings": []
}
```

Tool adapter 先保留 raw response 的受控对象引用，再把 canonical result 作为不可变记录。模型只能看到经过大小限制、脱敏和 schema 验证的 canonical result。

## 7. 首批合同目录

### 7.1 P0：随 WP-03～WP-06 定义

#### `ResearchModuleProposal@1`

字段：instrument_id、module_type、as_of、source_refs、facts、unknowns、freshness、material_changes、limitations。每个 fact 包含 claim、metric/value/unit/period（适用时）、source locator、observation time 和 evidence grade。

#### `EvidenceExtractionResult@1`

字段：source_document_id、document_version、issuer、published_at、observed_at、extracted_facts、quotes（短 locator，不保存无界全文）、tables、conflicts、extraction_warnings。数值必须保存原单位与归一单位，定位到页/表/段。

#### `ThesisCandidateProposal@1`

字段：instrument_id、base_thesis_version、summary、supporting_evidence_ids、contradicting_evidence_ids、key_assumptions、invalidation_conditions、open_questions、confidence_basis、materiality。禁止仅输出单一结论或无引用分数。

#### `ThesisRevalidationProposal@1`

字段：current_thesis_version、trigger_evidence_ids、per_claim_status、score_delta_proposals、new_risks、recommended_disposition（KEEP/REVISE/INVALIDATE/NEEDS_REVIEW）。它只提案，不覆盖 Thesis。

#### `AgentPlan@1`

字段：goal、run_revision、constraints、ordered_steps、tool_intents、stop_conditions、budget、expected_outputs。Tool 参数仍必须在执行前按 Tool schema 独立验证。

#### `InterventionClassification@1`

仅用于用户未明确选择控制语义时的建议：recommended_type、reason、changes_goal、changes_constraints、urgency。实际 steer/pause/cancel 必须由协议/API 明确提交，模型分类不能自行取消任务。

### 7.2 P1

- `BullBaseBearAnalysis@1`
- `ExpectationDeltaProposal@1`
- `ValuationScenarioProposal@1`
- `PriceInAssessmentProposal@1`
- `CatalystImpactProposal@1`
- `TradePlanRevisionProposal@1`（永远需敏感确认）
- `MemoryWriteProposal@1`
- `DisciplineSummaryProposal@1`

## 8. 提案与领域写入映射

| 合同 | 允许自动生成 | 允许自动提交 | 最终写入者 |
|---|---:|---:|---|
| Evidence extraction | 是 | 仅确定性元数据/待审核事实，取决于 source policy | Evidence Service |
| Research module proposal | 是 | 新版本可按领域规则提交；重大解释需标 proposal | Research Service |
| Thesis candidate/revalidation | 是 | 否，V1 material change 需确认 | Thesis Service |
| Agent plan | 是 | 仅 Runtime 内部当前 revision | Run Orchestrator |
| Trade plan revision | 是 | 否 | TradePlan Service |
| Memory write | 是 | 只有低风险 UI preference；交易/风险偏好需确认 | Memory Service |

任何合同都不能给模型数据库 session、ORM model 或任意 URL 写权限。

## 9. Provider 适配

`LLMProviderPort` 返回统一的：

```text
raw_response_ref
candidate_json
finish_reason
usage
provider_request_id
schema_mode_used       # NATIVE_STRICT / JSON_MODE / TEXT_FALLBACK
safety_metadata
latency
```

优先使用 provider-native strict structured output；不支持时用 JSON mode；text fallback 只能用于无副作用草稿，并仍需完整验证。Provider 声称“strict”不跳过本地 Pydantic/semantic/domain 校验。

## 10. 可观测性与审计

必须记录但脱敏：contract/version/hash、first-pass validation、error paths、repair attempt、最终 disposition、model/provider、token/cost、run revision、input snapshot、source ids。指标包括 first-pass pass rate、repair success、NEEDS_REVIEW、schema drift、source citation failure、domain conflict 和 stale discard。

禁止把完整敏感 prompt/response直接写普通日志；保留受控对象引用和 retention policy。

## 11. 合同测试

每个合同合并前至少具备：

1. JSON Schema snapshot test；
2. valid fixture；
3. missing/extra/wrong-type fixtures；
4. boundary numbers、date、currency、unit tests；
5. fake citation/unknown source test；
6. stale run revision test；
7. domain version conflict test；
8. repair one-and-only-one test；
9. provider adapter conformance test；
10. 不得直接 ORM commit 的 architecture test。

## 12. 验收标准

- 相同 contract version 在任意 provider 下得到相同本地验证结果。
- schema 错误包含机器可读 path/code，不靠字符串搜索。
- 引用不存在时不能入 Evidence/Research/Thesis 权威表。
- repair 不扩大来源、权限或 token budget。
- stale revision 结果即使 schema 完美也不会应用。
- Domain Service 能独立于 LLM 再验证并拒绝 proposal。
- 所有已提交对象保留 proposal、validator version、source refs 和 approval lineage。

