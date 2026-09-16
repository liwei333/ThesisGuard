# TASK-WP04-02-R1C-05C-01-INDEPENDENT-REVERIFY-R1

Status: READY_FOR_USER_DISPATCH for verifier-only preflight; cleanup phase requires separate exact-list approval.

## A. Execution core

- Role: independent verifier/environment diagnostician, not business repair executor.
- Objective: safely close the verifier-side PATH/setup/residue blocker and independently verify unchanged 05C-01 candidate.
- Why now: original acceptance is BLOCKED after reviewer-side fixture setup failure; no business bug is demonstrated. Do not create a code Repair or advance to 05C-02.
- Size/type: MEDIUM, one independent-verification closure / testing and bounded local fixture operations.
- Required: L1_STATIC_REVIEWED, L2_BUILD_VERIFIED, L3_CONTRACT_VERIFIED, L4_DB_VERIFIED; Full matrix.
- Read full original 05C-01 task/dispatch, current acceptance, executor report, policy addendum, fixed verifiers and original fixture source.

### Fixed candidate

```text
main HEAD   438738c543e4cae3e805d31324b068c1cd5c7059
main parent 7d3734bc8346c16f9bbf7f7d9806309949c996de
candidate branch codex/wp04-02-evidence-domain-service
HEAD   0cef44fd2ffd929b40e849e607af0bd4c44d14d2
parent bdd70edc153b6ed5def65ed99c41f325df45f066
 M backend/evidence/services.py
 M tests/test_evidence_services.py
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  errors.py
7ce76b02928019347625048e7d0acb523d74168cd6bbbdf03184163ac277f959  services.py
b5bfcdeb2db6753c71fd146b935dd26229daae0d73da5bda68af437db137b950  tests/test_evidence_services.py
```

### Top blocking AC

1. Exact branch/HEAD/parent/dirty scope/file/verifier hashes match. No candidate or existing evidence edits.
2. Before DB tests, validate Python/pytest/Alembic/Ruff/mypy discovery and child subprocess PATH under the effective normally approved execution environment; all diagnostic variables unset. Use existing inspected tools, no installation.
3. Read-only residue investigation yields a per-name ownership/emptiness/active-connection plan. Do not infer all 45 observed names belong to the failed run. No deletion before explicit user approval of the exact confirmed names and operation. Uncertain names remain untouched.
4. After safe approved residue resolution, unchanged candidate passes independent focused/full original verifier/regression/static matrix, including caller-commit/fresh-session/history/audit/replay evidence. Record actual results, not executor narrative.
5. Before/after precise DB-name inventories and fixture ID/teardown evidence prove this new verifier run has no unresolved residue; final candidate/scope/protected hashes unchanged. Produce one formal independent acceptance report.

### Scope, phases and stop conditions

Phase A: read-only preflight and cleanup plan. Permitted DB diagnostics are narrowly bounded read-only catalog/metadata checks on 127.0.0.1:15432 through normal permissions. Capture an actual before-name snapshot. Check original run timing/logs and per-DB contents/connections; creation age alone is insufficient ownership proof. The supplied 45-name inventory is not a deletion list. If ownership cannot be proved, report it and ask for direction rather than guessing.

Phase B: only after explicit user approval of the exact confirmed fixture DB names and cleanup operations. No prefix/glob bulk deletion, all temporary DB cleanup, business/shared/production DB targets, arbitrary writes to tables, volume/container deletion or forced termination outside explicitly approved targets. Normal fixture teardown for new tests remains allowed when independently dispatched, but extra cleanup of old residue is a separately approved action.

Assemble an explicit command-local PATH containing the already inspected Alembic location; do not repurpose system environment variables or change shell profiles. Verify shutil.which('alembic') and an Alembic heads inspection before any fixture creates a DB. Log effective tool paths/versions and ensure child executable resolution is identical for the actual test command.

Run the original 05C-01 matrix unchanged at final hashes: focused r1c05c01, 05A/04A preservation, tuple verifier, 58-scene oracle, five original verifiers, full service, persistence/migration/Research regressions, Ruff/format/mypy/compileall/heads and final scope/hash. Only original disposable fixture, no alternate instances/host/port, proxy or approval bypass. Do not rerun business RED by editing services or tests. The saved RED evidence is reviewed as historical.

If any setup/teardown error appears, stop further DB tests, capture exact created names and diagnose. Never count setup errors as RED or assert cleanup merely because there is no printed error. Any business assertion regression is a finding for the dispatcher, not permission to repair code or alter expectations.

Allowed new evidence: only uniquely named report/manifest/log/plan files under main docs/acceptance/TASK-WP04-02-R1C-05C-01-INDEPENDENT-REVERIFY-R1-evidence/, and a new independently named final acceptance. Preserve the existing BLOCKED acceptance, executor artifacts and DB inventory. No candidate/code/test/fixture/verifier/frozen/canonical edits, Git writes, business migration or dependency changes.

### High-risk counterexamples / evidence

- 45 prefix-matching names versus 41 failed setups: never delete the extra/uncertain DBs based on count or prefix.
- Parent tool works but child Alembic missing: preflight must verify the exact child environment, not a different shell.
- New fixture fails before yield/finalizer: exact new names must be captured; no blind repeated test loops or broad cleanup.
- New-write state rejection versus historical COMMITTED replay: verify both under unchanged production rules and real fresh sessions.

Map all original AC to inspected helpers/test nodes and fresh results. Report effective environment, actual tool paths, all commands/exits/log hashes, approval provenance/cleanup targets, before/after DB and file inventories, and residue uncertainties.

## B. Governance appendix

Use ai-task-governor, systematic-debugging and verification-before-completion. Executor reports IMPLEMENTATION_COMPLETE or BLOCKED; independent verifier supplies PASS/FAIL/BLOCKED in a new formal report. No self-approval from executor logs. No 05C-02/R1D or API/Research/Thesis/Agent work, trusted rules, Capability Runtime, Sector Crowding or Git integration.
