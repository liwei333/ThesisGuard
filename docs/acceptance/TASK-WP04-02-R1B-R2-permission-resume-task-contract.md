# TASK-WP04-02-R1B-R2 Permission Resume — Proposed Task Contract

**Status: PENDING_USER_AUTHORIZATION — NOT_DISPATCHED**

This is a dispatcher-authored proposed authorization/continuation supplement, not evidence of user consent. Generating or reading it grants no permission. It preserves the original R2 task, scope, AC and verification standards; it is not R3.

## A. Execution Core

- Resume ID: `TASK-WP04-02-R1B-R2-PERMISSION-RESUME`.
- Business task remains `TASK-WP04-02-R1B-R2`.
- Objective: after informed explicit user approval and successful normal tool permission, reproduce the existing real-DB red wiring tests and resume the original R2 two-file repair.
- Why now: executor stopped before edits after sandbox DB denial and a supplied approval-review model-capacity failure.
- Type/size: permission-gated REPAIR continuation / SMALL.
- Required business acceptance: L1_STATIC_REVIEWED, L2_BUILD_VERIFIED, L3_CONTRACT_VERIFIED, L4_DB_VERIFIED; Full evidence matrix.

### Authorization Text for the User to Send

The following is a proposed user message only. It becomes effective only when the user explicitly sends/adopts it after understanding the risk:

```text
我已知悉这些本地测试会连接 127.0.0.1:15432，创建随机临时 PostgreSQL 数据库，在临时库运行现有迁移和测试，正常由 fixture 清理本次创建的临时库；测试会消耗本地资源，失败可能留下需报告的临时库。

我明确批准从既有候选 worktree 通过正常权限机制运行原 TASK-WP04-02-R1B-R2 Required Verification 中列明的六条 pytest 命令及其现有 fixture 所需子进程/临时数据库操作。

授权不包括修改 main/Git 历史、共享或生产数据库 reset/migration、任意 SQL/广泛清理、外部主机访问、Docker/代理/改端口等绕过权限、修改 verifier/合同或扩大文件修改范围。

请重新申请该命令所需的正常权限；获准后先复现真实 red wiring failure，再按原 R2 合同继续两文件修复和完整验证。若工具仍拒绝或不可用，保持 BLOCKED，不绕过。
```

### Preconditions / Top Blocking AC

1. An explicit post-rejection user approval exists, covering the exact disclosed local commands/fixture operations. Do not treat this document, prior task dispatch or the request to review BLOCKED feedback as that approval.
2. Candidate baseline/hashes/verifier remain exact; normal permission request succeeds. No alternate execution route or weaker DB evidence substitutes for denied pytest.
3. Original wiring verifier reaches its business assertions against real disposable PostgreSQL. Current expected pre-repair red: three wiring assertion failures, not PermissionError or setup failure. If it unexpectedly turns green on identical files, investigate/report the discrepancy rather than invent a red result or edit the verifier.
4. Only then resume original R2 production-target repair; all original AC, preservation requirements and full matrix remain binding. Permissions success itself is not implementation acceptance.

### Baseline / Investigation / Scope

Worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`.

Branch/HEAD: `codex/wp04-02-evidence-domain-service` / `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`; parent `3eb494e6613cf3952ffbaaf4166b8cf3ea801555`.

Read AGENTS.md, original R2 repair contract, prior R1 acceptance and permission-block acceptance. Initial candidate must still have only services.py and test_evidence_services.py modifications. Validate these SHA-256 values:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
2659bc4d06bd60c242a389365e96e60e4cc9bef0f31d5d924ef43e1e23da8331  backend/evidence/services.py
16784fc35abb8db4a41f7ed90307f3710edf52df98594a39b3cf707371e83681  tests/test_evidence_services.py
909f50bd902ecd9c0013121681b614fcbc302f718cc7c9d5dc96f6237d106786  /tmp/test_wp04_02_r1b_r1_wiring_20260915.py
```

Inspect effective test connection configuration without exposing passwords. TG_TEST_ADMIN_DATABASE_URL or other overrides must not redirect tests to an external/shared production instance; approval is confined to loopback port 15432. Unexpected configuration requires BLOCKED and user direction, not silently rewriting env or connecting elsewhere.

After red reproduction, allowed code edits remain only services.py and test_evidence_services.py; errors.py unchanged. Preserve all existing candidate and main governance files. Any file-system approval needed for this out-of-root worktree must be obtained normally; DB approval does not bypass it.

### Explicit Local Pytest Scope / Required Verification

These are the six originally required pytest invocations covered by the proposed approval. Run from the exact candidate worktree; ask for normal escalation as required, with local test scope/risk in the justification:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_r1_wiring_20260915.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_reverify.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1a_verifier.py -rs
pytest -p no:cacheprovider -q tests/test_evidence_services.py -k r1b -rs
pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs
pytest -p no:cacheprovider -q tests/test_evidence_persistence.py tests/test_migrations.py tests/test_evidence_migrations.py tests/test_research_api.py tests/test_research_persistence.py -rs
```

Original R2 Ruff/format/mypy/compileall/Alembic-head/diff/status/hash commands are still mandatory after implementation. The service ID allocation must remain private, actual new target must be validated before version/children flush, all legal historical-DAG cases and previous behavior preserved.

### Must Not / Stop Conditions

No retry before explicit informed approval; no psql/Docker/proxy/alternate host or port, indirect tool path or sandbox-disable workaround. No mock DB substitution, test skip/xfail/verifier edit, scope/AC change, new R3, R1C/R1D implementation, Git operations or main mutation.

If user approval absent, tool still rejects/unavailable, DB/setup/verifier unavailable, baseline/hashes changed, or forbidden changes needed: report BLOCKED, preserving exact command and error with secrets redacted. Report known temporary DB residue; no broad cleanup or deletion by prefix. Do not repeatedly resubmit an unchanged rejected action or change route to obtain the same denied result.

### Expected Evidence / Executor Final Response

Identify actual user approval and normal permission outcome separately from DB assertion outcome. Report fresh preflight snapshot/hashes; red reproduction exact command/exits/assertions; subsequent original R2 implementation locations/ID equality and pre-flush timing; full verification outcomes, final two-file status/hashes and achieved/missing acceptance.

Executor final status only IMPLEMENTATION_COMPLETE or BLOCKED. Keep repair candidate uncommitted for independent verification.

## B. Governance Appendix

Core invariants and anti-drift rules from ai-task-governor remain binding. Approval review's reported capacity error is not an authorization grant or proof of DB failure. This supplement grants no new business scope and does not rewrite historical PASS/FAIL/BLOCKED facts.

R2 and R1B must receive independent acceptance before R1C. Whole WP04-02 remains unaccepted; no Git integration authorized.
