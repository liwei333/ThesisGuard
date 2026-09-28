# R8 approved continuation prompt

Use this prompt only after the user has supplied the exact destructive-operation
approval required by the R8 independent partial review. Paste the user's
approval text verbatim into the destination thread together with this prompt.
Without that approval, stop without invoking any formal supervisor.

## Execution Core

- Task ID:
  `TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10-REPAIR-R8-PYTEST-RUNTIME-AND-RESIDUAL-RESTORE-R1-APPROVED-CONTINUATION-R1`
- Parent task:
  `TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10-REPAIR-R8-PYTEST-RUNTIME-AND-RESIDUAL-RESTORE-R1`
- Executor: Codex, continuing existing thread
  `01a0dd57-daed-7fa2-b769-615ab1444ece`.
- Worktree:
  `/Users/qianduoduo/.codex/worktrees/r8-runtime-residual-exec/ThesisGuard`.
- Exact baseline: `1613c89209f91a4bb64dab04c588250b0b5f6a85`.
- Runtime root:
  `/private/tmp/tg-r10-r8-pytest-runtime-r1-visible-exec`.
- Task size: SMALL continuation of a MEDIUM Repair.
- Task type: `REPAIR + DATABASE_MAINTENANCE + EVIDENCE`.
- Required acceptance:
  `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`,
  `L4_RUNTIME_VERIFIED`, `L4_DB_VERIFIED`.
- Evidence matrix: Full.

Objective: after confirming the exact user approval below, perform the one
remaining guarded R8 formal maintenance phase, verify exact catalog restoration,
close the evidence package, create the single evidence-only commit and report
`AWAITING_INDEPENDENT_ACCEPTANCE`. Do not rerun or rebuild the already accepted
offline runtime unless the existing seal fails verification.

## Required explicit approval

Proceed only if the user has explicitly approved, in substance, all of the
following:

> I approve at most one non-FORCE `DROP DATABASE` attempt against
> `tg_wp04_service_1161dc4e02604c5ba23d157af5436b71` (expected OID `9273601`,
> owner `thesisguard`, owner OID `10`) only after the live PostgreSQL identity,
> complete catalog, exact target identity and zero-session checks all pass. If
> any check differs, no drop is authorized.

If that approval is absent, ambiguous or narrower, stop as
`BLOCKED_USER_DESTRUCTIVE_APPROVAL_AWAITING_INDEPENDENT_ACCEPTANCE` without
creating the formal marker.

## Top Blocking AC

1. The existing worktree remains at the exact baseline with only attributable
   R8 evidence files; the task-local runtime contract and `READY` receipt still
   match exactly; the formal invocation marker and all formal result files are
   absent before invocation.
2. Exactly one escalated formal supervisor may start. It must perform the
   already-frozen ordered Docker/readiness/TCP/secure-identity/catalog/target/
   zero-session checks before any mutation. No retry is allowed.
3. Only if the complete live R7 post-run catalog and the exact target tuple
   match may the supervisor execute at most one quoted, non-FORCE
   `DROP DATABASE` for the exact target. If the target is already absent, zero
   mutation is allowed only when the complete catalog already equals the
   accepted R7 pre-run catalog.
4. After the formal phase, the complete catalog must equal the accepted R7
   pre-run catalog: count 49, target absent, historical count 45, historical
   hash
   `3b28f630bff3c1b2842e8e4b46787c588df9feaeabe3db9d356a51b4258a6f05`,
   and every non-target identity unchanged.
5. Final evidence must close: strict JSON/JSONL, zero credential/raw-exception
   findings, zero repository pycache, exact helper hashes, manifest and report
   checksum, one evidence-only commit whose sole parent is the exact baseline,
   and a clean final worktree.

## Required continuation sequence

1. Read `AGENTS.md`, the original 514-line R8 prompt, and the independent
   partial review. Reapply `using-superpowers`, `systematic-debugging`,
   `test-driven-development` as appropriate, and
   `verification-before-completion`.
2. Confirm exact worktree/baseline/attribution. Do not inspect, adopt or modify
   the excluded `/Users/qianduoduo/.codex/worktrees/804b/ThesisGuard` attempt.
3. Verify, without rebuilding:
   - runtime contract equals its sealed task-local copy;
   - current gate returns `READY`;
   - 52 wheels, sdist 0, hash mismatch 0;
   - formal marker/result/maintenance/catalog-restoration files are absent.
4. Request `require_escalated` exactly once with a user-facing justification
   naming the exact temporary database and stating that one non-FORCE drop is
   possible only after all live guards pass.
5. Run only the frozen R8 maintenance supervisor in formal mode. Do not manually
   reproduce its SQL, read a connection value in the parent, or run a second
   supervisor.
6. If any precondition blocks, retain only sanitized fixed classifications,
   finalize a failure/block evidence package and do not retry.
7. If the formal phase succeeds or proves the catalog was already exactly
   restored, perform fresh postcondition/protected-input checks, generate the
   execution report and full evidence closure, and create exactly one
   evidence-only commit.

## Fixed budgets and prohibitions

- formal escalated supervisor: at most `1`;
- supervisor retry: `0`;
- secure-proof parent/child/retry: at most `1/1/0`;
- exact drop attempts: at most `1`;
- successful DB mutations: at most `1`;
- `DROP ... FORCE`: `0`;
- `pg_terminate_backend`: `0`;
- Docker mutation: `0`;
- manual/wildcard cleanup: `0`;
- database create/migration: `0/0`;
- collect-only/project pytest: `0/0`;
- application source/test/fixture/migration/config changes: `0`;
- merge/rebase/cherry-pick/push/PR/integration: `0`.

Do not change the original contract or regenerate dependencies to hide drift.
Do not run the 41-node focused suite. Do not self-approve.

## Final deliverables

Complete the original required paths:

- `docs/acceptance/TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10-REPAIR-R8-PYTEST-RUNTIME-AND-RESIDUAL-RESTORE-R1-execution-report.md`
- `docs/acceptance/TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10-REPAIR-R8-PYTEST-RUNTIME-AND-RESIDUAL-RESTORE-R1-evidence/`

Report exact counts, safe identity, live branch, catalog before/after,
mutation/drop/force/terminate/manual-cleanup budgets, strict evidence results,
baseline/HEAD/parent, changed paths and final clean status.

Final status must be one of:

- `IMPLEMENTATION_COMPLETE_AWAITING_INDEPENDENT_ACCEPTANCE`;
- `EXECUTION_FAIL_AWAITING_INDEPENDENT_ACCEPTANCE`;
- a precise `BLOCKED_*_AWAITING_INDEPENDENT_ACCEPTANCE`.

State explicitly:

- next full DB reverify allowed=`NO — awaiting independent acceptance`;
- R11 allowed=`NO`;
- integration allowed=`NO`;
- WP-04-02/WP-04 remain `PARTIALLY_IMPLEMENTED`;
- strategy remains `UNPROVEN`.
