# TASK-TEST-INFRA-LOCAL-POSTGRES-15432-RESTORE-R1 Independent Review R1

**OVERALL: PASS**

## Metadata

- Task ID: `TASK-TEST-INFRA-LOCAL-POSTGRES-15432-RESTORE-R1`
- Review ID: `TASK-TEST-INFRA-LOCAL-POSTGRES-15432-RESTORE-R1-INDEPENDENT-REVIEW-R1`
- Date: 2026-09-22, Asia/Shanghai
- Executor reviewed: Codex operations executor
- Independent verifier: separate Codex review session
- Required acceptance: `L1_STATIC_REVIEWED` and PostgreSQL-service-scope `L4_RUNTIME_VERIFIED`
- Achieved acceptance: both required levels for the local PostgreSQL restoration scope
- Business `L3_CONTRACT_VERIFIED`: not required and not claimed
- Focused `L4_DB_VERIFIED`: not required, not run and not implied
- Repair required: no
- Successor safety condition: a fail-closed catalog-quiescence gate is required before the R5 real database invocation

## Decision

The existing local PostgreSQL prerequisite at `127.0.0.1:15432/postgres` was
restored without recreating the container, replacing the named volume, pulling
an image, or mutating database contents. The retained execution evidence is
internally complete, independently hash-reproducible and consistent with fresh
read-only runtime checks. The restoration task therefore passes within its
strict infrastructure scope.

Fresh independent checks confirmed Docker Desktop `29.7.2`, daemon identity
`docker-desktop`, container `thesisguard-postgres`, image
`pgvector/pgvector:pg17`, image ID
`sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f`,
named volume `thesisguard-postgres-data`, mount target
`/var/lib/postgresql/data`, restart policy `unless-stopped`, running/healthy
state, and both host bindings for port 15432. A fresh `pg_isready` returned
`accepting connections`. Read-only SQL observed database `postgres`, user
`thesisguard`, and PostgreSQL `17.11 (Debian 17.11-1.pgdg12+2)`.

The exact historical set of 45 protected `tg_wp04_service_*` database
identities still matched name, OID, owner and owner OID. No missing or changed
historical identity was found. This review did not connect to those databases
individually and issued no database mutation statement.

The executor correctly disclosed that the whole catalog was changing under an
external or concurrent actor. This is not a failure of the restoration
contract, which required preservation of the fixed 45 identities and no
task-attributable mutation rather than global catalog quiescence. It is,
however, a blocking precondition for an unguarded successor verification.
During this independent review, two read-only catalog digests eight seconds
apart changed from `49|1f32e87a64fb14ecafca65a822149d99` to
`50|c4d0ac9c0bc4766590a351beab72ffbc`, while point-in-time active external and
active `tg_wp04_service_*` session counts were both zero. This proves that
short-lived concurrent database activity is still possible and cannot be
excluded by a single `pg_stat_activity` sample.

## Evidence Integrity

- Execution report SHA-256:
  `6b6e69f182eb425d0f1a5a5f9ab48ce79cfe20a1b9367044d7521df5b8960c0d`
- Root evidence manifest SHA-256:
  `102629d1470ad1ab15992532c36d2d3f388791cd8ce71b5890a4cc7d03706d3b`
- Manifest-declared eligible files: 24
- Independently enumerated eligible files: 24
- Missing, extra, byte-size-mismatched or SHA-256-mismatched files: 0
- JSON parse failures: 0
- Credential-bearing PostgreSQL URL/userinfo pattern matches in the report and
  evidence bundle: 0
- Compose SHA-256 independently rechecked:
  `eed9951ef6b4e900d7abc29a55df25bc51e44a0e637e17dc62017fca5cca500b`
- `.env` SHA-256 independently rechecked without printing its contents:
  `8c135d233c987c5d9a338c6d5e20171dbbb16cfb3cfc04412bc4b55d9ffabaf0`

## Acceptance Matrix

| AC | Requirement | Independent evidence | Verdict |
|---|---|---|---|
| AC-01 | Restore only the existing authorized PostgreSQL service | Existing container auto-restored under `unless-stopped`; no explicit start/up/create/recreate command was recorded | PASS |
| AC-02 | Preserve the existing named volume and image | Fresh Docker inspection matches the retained name, driver, creation time, mount, reference and image ID | PASS |
| AC-03 | Prove service health on the exact endpoint | Container is running/healthy; host port 15432 is published; fresh `pg_isready` accepts connections | PASS |
| AC-04 | Prove read-only database identity | Fresh read-only SQL matches database, user and server version | PASS |
| AC-05 | Preserve the fixed 45 historical UNKNOWN identities | Fresh exact comparison found 45/45 matches and zero missing/mismatched identities | PASS |
| AC-06 | Make no logical database or unrelated-container mutation | Executor command/mutation audits report zero prohibited operations; no contradictory evidence was found | PASS |
| AC-07 | Close credential-safe evidence completely | Manifest rebuild exact 24/24; all JSON parses; no retained credential URL/userinfo pattern | PASS |
| AC-08 | Do not claim focused business DB verification | Executor records pytest 0 and R5 not run | PASS |

## Gate Results

| Gate | Result | Basis |
|---|---|---|
| G0 Baseline | PASS for execution-time state | Retained baseline and source/config hashes are coherent and complete |
| G1 Scope | PASS | Only the authorized restore report/evidence was produced by the task; no prohibited operation is recorded |
| G2 Infrastructure contract | PASS | Recovery path A matches the authorized existing-resource path |
| G4 Runtime check | PASS | Fresh Docker and PostgreSQL health checks reproduce the claimed state |
| DB persistence/business verification | NOT APPLICABLE | No business test, fixture, migration, DDL or DML was authorized or run |
| G6 Evidence | PASS | Recursive manifest and credential-safety checks close exactly |

## Post-Execution Git State Qualification

The executor sealed evidence against `main@675217c3`, candidate `e942cbcc`, and
the then-uncommitted accepted R5 harness bytes on `df836cb3`. After that seal,
other work changed repository state: current `main` is `cc551623`, and the
harness branch is clean at `f9a41ea`. Commit timestamps show those integration
and harness commits occurred after the restoration manifest was generated.
The candidate remains clean at `e942cbcc`.

This later Git movement does not contradict the earlier restoration evidence,
but it invalidates reuse of the old SHA assumptions in a successor prompt.
Any R5 task must explicitly pin the current integrated main as protected
context, pin the clean R5 harness commit `f9a41ea`, and use a detached
`675217c3` snapshot only where the accepted harness's immutable main-baseline
check requires it. It must not silently rewrite the accepted runner constants.

## Counterexample and Boundary Review

1. The service is not merely listening through an unrelated process: Docker
   inspection ties host port 15432 to the named healthy target container.
2. The target did not come from a replacement volume or image: the retained
   and fresh identities agree exactly.
3. The 45 historical databases were not inferred from a prefix count: exact
   name/OID/owner/owner-OID tuples were compared.
4. Global catalog stability is not accepted. The executor disclosed drift,
   and this review independently reproduced drift over eight seconds.
5. Absence of a session in one `pg_stat_activity` snapshot is insufficient to
   prove quiescence; the successor must use a sustained catalog digest window.
6. A PASS here does not turn pytest 0 into business verification and does not
   close 05C-01, R1C, or WP-04-02.

## Final Decision Rationale

`PASS` is supported for the narrowly defined local PostgreSQL restoration. The
service is available and healthy, the existing durable storage identity was
preserved, fixed historical identities remain intact, evidence is complete,
and no database mutation was authorized or observed from this task.

The next real database verification must fail closed on current external
catalog churn. It may proceed only after a sustained quiescence window proves
an identical complete catalog and zero active external client backends. If the
window changes, it must return `BLOCKED_CONCURRENT_DB_ACTIVITY` before the
single real pytest invocation and before any CREATE attempt.

## Next Action

Dispatch `TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R5` to a **new Codex
independent DB verifier, not zcode**. The task must include a 120-second
read-only catalog-quiescence gate, fresh output paths, a detached historical
main snapshot for the immutable harness pin, exactly one real 41-scenario
invocation only after all gates pass, complete current-catalog protection, and
strict resource-ledger attribution.

Do not clean any pre-existing database, weaken or edit the verifier harness,
modify current main/candidate source, or infer ownership from a database-name
prefix.
