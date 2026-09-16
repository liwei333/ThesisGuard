# TASK-WP04-02-R1C-03A-VERIFY-PREREQUISITES-R1

Status: `READY_FOR_USER_DISPATCH`; no work starts automatically from this document.

## A. Execution Core

- Objective: Restore the exact prerequisites of R1C-03A independent verification, preserve the current candidate, and collect fresh Full-matrix evidence. Do not implement a next business slice.
- Why Now: 2026-09-16 independent acceptance is BLOCKED by local PostgreSQL connection refusal and five missing fixed /tmp verifier artifacts, not a demonstrated code defect.
- Role: prerequisite recovery executor, followed by logically separate VERIFIER. Executor final status is only IMPLEMENTATION_COMPLETE or BLOCKED; it cannot self-approve PASS.
- Type / Size: VERIFICATION_PREREQUISITE_RESTORE / MEDIUM; one closure: enabling and completing unchanged-candidate reverify.
- Required Acceptance: L1_STATIC_REVIEWED, L2_BUILD_VERIFIED, L3_CONTRACT_VERIFIED, L4_DB_VERIFIED; Full Evidence Matrix.

### Context and fixed baseline

Read main AGENTS.md and these main docs completely before action:

```text
/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-03A-acceptance.md
/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-03A-task-contract.md
/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-02-acceptance.md
```

Read the frozen Evidence contract and prior R1 repair/acceptance documents required by R1C-03A. Inspect project environment/startup documentation, existing PostgreSQL instance identity, tools, fixtures and scoped authoritative artifact backups.

Candidate worktree:
`/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`.

```text
branch: codex/wp04-02-evidence-domain-service
HEAD: bdd70edc153b6ed5def65ed99c41f325df45f066
parent: f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af
 M backend/evidence/services.py
 M tests/test_evidence_services.py

3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
43b548232df4267f377c5e144222c9278c3cc478f6800720240c4618b689ebe3  backend/evidence/services.py
47ff645c0f782af67e9f6ee64520105febdb28c6547a43bf89b435bead6c5108  tests/test_evidence_services.py
```

Do not demand clean status, discard changes, or move HEAD. Main baseline at previous inspection is 7d3734bc8346c16f9bbf7f7d9806309949c996de; preserve all main dirty/untracked files and report new unrelated drift without incorporating it.

### Top Blocking AC

1. Exact candidate branch/HEAD/parent/three hashes and two-file dirty state are unchanged before/after; no business code, old verifier contents, historical acceptance, frozen contract or Git mutation.
2. Recover all five authoritative original verifier files with exact hashes below. Record source provenance and archive identical bytes in a durable project evidence directory. Existing mismatching files must not be overwritten. No inference/rewrite from names, summaries, assertions or desired pass counts.
3. Restore/check the existing local PostgreSQL disposable-fixture endpoint at 127.0.0.1:15432 using its actual approved local instance; no alternate host/port/shared DB, replacement service, proxy or infrastructure redesign. Any startup requires exact instance/volume/port identification and normal approvals; no deletion/reset/migration of business DB.
4. Run all original R1C-03A verification targets freshly. Add verifier-owned R1C-03A boundary assertions in a separately named artifact if required to prove all entrance/no-inheritance/fresh-session commit/legacy-history/replay behavior; this is not a substitute for the five originals. DB connection/setup failure or Research skips cannot count as passing coverage.
5. Persist complete commands, exits, fresh outputs, environment/runtime identity, recovered provenance/hash manifest, candidate snapshots and achieved/missing acceptance. Separate executor historical RED from newly observed behavior. Remain BLOCKED if any prerequisite cannot be recovered; do not advance R1C business work or Git integration.

### Original artifact manifest

```text
909f50bd902ecd9c0013121681b614fcbc302f718cc7c9d5dc96f6237d106786  /tmp/test_wp04_02_r1b_r1_wiring_20260915.py
0f7cea4d14735bd165b75d756444259a64483a97e6a338227bc09af806490cc9  /tmp/test_wp04_02_r1b_reverify.py
66be45f354d1df34370eedd9811b3bc68cf29852d45027ea576a67975b18ddfe  /tmp/test_wp04_02_r1a_verifier.py
857914f073c552be98f895a456d2f0ec486452e1c9aed06a87176c6e7fefd48a  /tmp/test_wp04_02_r1c_01_independent_20260915.py
64162c0aafc3ad620ee0cab5e4d8d0ed10e6d61ab8dc21322f4364144c442a05  /tmp/test_wp04_02_r1c_02_independent_20260915.py
```

Recovery is allowed only from authoritative complete originals (project evidence archives, known task exports containing full original source, user-supplied originals/backups), verified byte-for-byte by SHA-256. Use narrowly scoped read-only discovery, not broad home scans or secrets/config export. If unavailable, BLOCKED with precise missing artifact list; request user originals or a dispatcher-approved separately versioned replacement-verifier contract. Do not pretend newly authored tests have the old provenance.

After recovery, archive exact copies at `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/` with a task-specific hash/provenance manifest. This newly dispatched recovery contract permits restoration of absent original paths and new exact evidence copies; it does not permit editing originals, changing fixed hashes, or weakening old contracts. Do not commit these artifacts.

### Scope / Must / Must Not

Allowed: read-only code/fixture/environment inspection; exact original recovery to absent fixed /tmp paths; exact persistent evidence copies and new manifest/report under main docs/acceptance; normal approved existing-local-instance recovery; isolated pytest fixture creation/migration/teardown only; optional separately named verifier-owned new tests outside candidate.

Forbidden: candidate business/test changes, errors/models/repositories/schema/migration/API changes, old report/contract/verifier edits, production trusted rule activation, initial/correction policy implementation, R1D work, Docker/host/port/DB substitution, arbitrary SQL, broad cleanup, dependency upgrades, Git add/commit/merge/rebase/reset/checkout/push. Do not use missing tools as a reason to install/upgrade automatically; discover already installed runtime paths and report versions/resolution.

Existing PostgreSQL service startup is not permission to create a new alternate fixture route or modify volumes. If exact identity or normal startup authorization cannot be established, BLOCKED and ask for the missing authority. Fixture-specific temporary DB teardown is allowed by existing tests; suspected leftovers require precise reports, not cluster-wide cleanup.

### High-risk examples

- Given a recovered artifact with wrong hash, Then do not install/archive it as accepted evidence; BLOCKED.
- Given available PostgreSQL only at another port/shared environment, Then do not redirect the fixture or set TG_TEST_ADMIN_DATABASE_URL; BLOCKED.
- Given unchanged hash-locked candidate and restored prerequisites, When an assertion fails, Then report the exact semantic failure; no candidate repair or expectation adjustment in this task.
- Given fresh-session caller commit after illegal trusted request, Then no business/audit/idempotency residue and prior exact/children remain unchanged; prove with real PostgreSQL, not helper-only unit checks.

### Required Verification

Before runtime, verify all three candidate hashes and five restored artifact hashes, inspect actual fixture default route, and confirm TG_TEST_ADMIN_DATABASE_URL, TG_R1C_REPLAY_BASELINE, TG_R1C02_REPLAY_PRIOR are unset. Identify Python/pytest/Ruff/mypy/Alembic versions and command paths; use a coherent existing environment for DB pytest/Alembic subprocess. Report any approved static-runtime difference.

From the unchanged candidate through normal permissions, run the complete Required Verification block in the original R1C-03A contract. It includes these DB targets with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q <target> -rs`:

```text
tests/test_evidence_services.py -k "r1c or trusted or current_valid or lifecycle or state_transition"
/tmp/test_wp04_02_r1c_02_independent_20260915.py
/tmp/test_wp04_02_r1c_01_independent_20260915.py
/tmp/test_wp04_02_r1b_r1_wiring_20260915.py
/tmp/test_wp04_02_r1b_reverify.py
/tmp/test_wp04_02_r1a_verifier.py
tests/test_evidence_services.py
tests/test_evidence_persistence.py tests/test_migrations.py tests/test_evidence_migrations.py tests/test_research_api.py tests/test_research_persistence.py
```

Run Ruff check/format check, mypy, compileall and Alembic heads with the original three-file arguments and options; absolute paths to existing tools are allowed if needed, with resolution evidence. Run diff-check, status, HEAD/parent, candidate+artifact hashes again after all verification. New evidence archives need actual whitespace/hash checks; git diff does not validate untracked files. Expected migration metadata head is 000000000004.

These node counts are historical expectations for an unchanged candidate (142 focused, 239 services, 35 regression, old verifiers 43/8/3/4/12), not acceptance oracles. Inspect assertion results, skips, failures and fixture cleanup. Do not hardcode outputs or edit tests to match counts.

### Stop Conditions / Expected Evidence

BLOCKED if candidate drift, no authoritative original, hash conflict, required environment/startup approval unavailable, fixture setup/cleanup error, forbidden changes needed, or verification standards would need alteration. A genuine semantic failure is reported for independent verifier/dispatcher to issue a repair contract, not silently repaired here.

Executor evidence: source→artifact hash manifest, exact local instance/endpoint and normal permission evidence, runtime paths/versions, all executed commands/exits, caller-commit/fresh-session checks, original-verifier regressions, beginning/final snapshots and all newly created evidence paths. Output only IMPLEMENTATION_COMPLETE or BLOCKED; successful prerequisite/execution collection waits for a separate independent PASS/FAIL/BLOCKED acceptance.

## B. Governance Appendix

Use ai-task-governor, systematic-debugging and verification-before-completion. Preserve core invariants, anti-drift, Full evidence-based acceptance and the logical executor/verifier distinction. Historical PASS and code presence are not current proof.

Production approved trusted rule set stays empty. Positive registry/semantic validators, initial-import and full ordinary-correction qualifications, R1D, final WP04-02 reverify, API/Research references, Sector Crowding and Capability Runtime do not unlock through prerequisite restoration alone.
