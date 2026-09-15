# TASK-WP04-02-R1B-REBASELINE-REVERIFY-R1 Acceptance Report

**OVERALL: FAIL**

## Metadata

- Task ID: `TASK-WP04-02-R1B-REBASELINE-REVERIFY-R1`
- Date: `2026-09-15`
- Verifier: Codex independent verifier
- Report Path: `docs/acceptance/TASK-WP04-02-R1B-REBASELINE-REVERIFY-R1-acceptance.md`
- Path basis: existing project `docs/acceptance/` governance convention.
- Candidate worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`
- Candidate branch: `codex/wp04-02-evidence-domain-service`
- Accepted replacement baseline HEAD for this reverify: `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`
- Replacement baseline parent: `3eb494e6613cf3952ffbaaf4166b8cf3ea801555`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, partial `L4_DB_VERIFIED` for green suites and the failing independent counterexample.
- Missing Acceptance: full `L3_CONTRACT_VERIFIED` and full `L4_DB_VERIFIED` because one original R1B blocking semantic AC fails.
- Repair Required: `YES`
- Repair Contract: `docs/acceptance/TASK-WP04-02-R1B-R1-repair-contract.md`
- Next Action: repair R1B exact-version derivation cycle semantics; do not enter R1C.

## Explicit Authorization

The user explicitly authorized this rebaseline verification task to accept:

`f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`

as the content-equivalent new Git baseline for `TASK-WP04-02-R1B`, only if independently verified that:

1. Its parent is `3eb494e6613cf3952ffbaaf4166b8cf3ea801555`.
2. The commit only adds:
   - `backend/evidence/errors.py`
   - `backend/evidence/services.py`
   - `tests/test_evidence_services.py`
3. The three committed blobs match the R1A-R2 accepted hashes.

This authorization replaces only the old exact-HEAD and untracked-candidate baseline clauses. It does not authorize Git mutation, business-contract changes, weaker AC, or R1C/R1D work.

## Baseline / Content-Equivalence Matrix

### Candidate Baseline Gate

| Check | Expected | Actual | Verdict |
|---|---|---|---|
| Candidate branch | `codex/wp04-02-evidence-domain-service` | `codex/wp04-02-evidence-domain-service` | `PASS` |
| Candidate HEAD | `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af` | `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af` | `PASS` |
| Parent | `3eb494e6613cf3952ffbaaf4166b8cf3ea801555` | `3eb494e6613cf3952ffbaaf4166b8cf3ea801555` | `PASS` |
| Commit delta | exactly 3 added files | exactly 3 added files | `PASS` |
| Current candidate modifications | `services.py` and `test_evidence_services.py` only | exactly those 2 files | `PASS` |

`git diff-tree --no-commit-id --name-status -r HEAD`:

```text
A	backend/evidence/errors.py
A	backend/evidence/services.py
A	tests/test_evidence_services.py
```

Current candidate status:

```text
## codex/wp04-02-evidence-domain-service...origin/codex/wp04-02-evidence-domain-service
 M backend/evidence/services.py
 M tests/test_evidence_services.py
```

### R1A-R2 Base Blob Equivalence

| File | `f7c50ab` committed blob SHA-256 | R1A-R2 accepted SHA-256 | Verdict |
|---|---:|---:|---|
| `backend/evidence/errors.py` | `3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec` | `3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec` | `PASS` |
| `backend/evidence/services.py` | `f980f2fcbb789b08dd25982f6af2e548def71a3cba8851d79ae0155748736981` | `f980f2fcbb789b08dd25982f6af2e548def71a3cba8851d79ae0155748736981` | `PASS` |
| `tests/test_evidence_services.py` | `619324318d25bc25a45941e69d0e10a1539ec9eed4d302a817d3e278e9719396` | `619324318d25bc25a45941e69d0e10a1539ec9eed4d302a817d3e278e9719396` | `PASS` |

### Current Candidate Hashes

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
f1c4a9b85505cb152273a246525a4b3214eaaff0847c328f1d2ed2b350fadf0c  backend/evidence/services.py
454f95d269b7521764409b952ba26055c473d62c93c75313b16fa2e4fa66a0ce  tests/test_evidence_services.py
```

These match the reverify task prompt's expected candidate hashes.

## Classification and Gates

- Task Type: baseline reconciliation, independent verification, domain-service repair acceptance.
- Risk Type: immutable lineage, exact EvidenceVersion graph, provenance-derived identity, replacement routing, DB rollback/no-residue, audit correctness.
- Touched Layers: Evidence service and real-PostgreSQL service tests.
- Task Size: `MEDIUM`.
- Evidence Matrix Type: `Full`.
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G3 Architecture, G4 Test, DB Persistence, G5 Regression, G6 Evidence.
- Not Applicable Gates: API/OpenAPI, frontend/browser, schema/migration modification.

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | `PASS` | Authorized `f7c50ab`; parent, delta and base blobs match required values |
| G1 Scope | `PASS` | Current diff is exactly `backend/evidence/services.py` and `tests/test_evidence_services.py`; no candidate code/test file was modified by verifier |
| G2 Contract | `FAIL` | Candidate rejects same-series historical exact-version support before exact graph cycle traversal can decide; this broadens contract semantics |
| G3 Architecture | `FAIL` | Exact `EvidenceVersion` graph validation is implemented as a same-series prohibition in revision path |
| G4 Test | `FAIL` | Candidate's 4 R1B tests pass, but independent verifier counterexample fails |
| DB Persistence | `FAIL` | Real PostgreSQL verifier test fails on replacement that should be legal under exact-version graph semantics |
| G5 Regression | `PASS for regressions only` | R1A verifier, 95-case service suite and 35-case regression suite pass; they do not override the blocking R1B failure |
| G6 Evidence | `FAIL` | Independent reviewer and verifier-owned PostgreSQL test both identify the same blocking issue |

## Original R1B Top Blocking AC Matrix

| Top AC | Requirement | Implementation Evidence | Verification Evidence | Boundary / Negative Evidence | Verdict |
|---|---|---|---|---|---|
| TOP-AC-01 | MANUAL, DERIVED and CROSS_INSTRUMENT identities are service-derived; caller `origin_key` / CROSS `scope_key` cannot select lineage | `_derive_origin_key` and `_derive_scope_key` in `backend/evidence/services.py`; candidate R1B tests cover caller conflicts and canonical examples | Candidate `pytest -k r1b`: `4 passed` | No independent blocking issue found here | `PASS` |
| TOP-AC-02 | THESIS_INFERENCE/DERIVED requires exact supports and rejects missing support, invalid role, duplicate edge, self-reference and exact graph cycles | `_validate_derivation_links` validates role/missing/duplicate and traverses support graph, but also rejects any support whose `evidence_series_id` equals the revised series | Independent verifier `/tmp/test_wp04_02_r1b_reverify.py`: `1 failed, 3 passed`; failure is `EvidenceInvalidDerivationLink: Evidence cannot derive from its own series` | Same-series historical exact support that does not create an exact-version cycle is rejected before replacement routing | `FAIL` |
| TOP-AC-03 | Support/member set changes route to replacement v1; metadata-only child changes append N+1 | `revise_correct_evidence` routes via `_revision_identity_changed`; tests cover changed support/member set | Candidate tests pass | The failing verifier case changes support set and should route to replacement v1, but is rejected before routing because one support is an older exact version in the same series | `FAIL` |
| TOP-AC-04 | N+1 correction/status/tombstone keeps complete child snapshot; nullable explicit clear differs from omitted | `_append_status_or_revision` copies derivation links; `_UNSET` differentiates omitted/explicit `None`; candidate tests cover tombstones and nullable clear | Candidate `95 passed`; independent no-residue tests around failed child validation pass for 3/4 verifier cases | No additional failure found in this AC beyond the same derivation validation blocker | `PASS with TOP-AC-02 dependency` |
| TOP-AC-05 | Provenance/extractor fail-closed; failures leave no partial rows; R1A/WP04-01/WP03 regressions remain green | `_validate_extraction_provenance`; expanded `evidence_table_counts`; candidate tests cover extractor and no-residue | R1A verifier `12 passed`; service suite `95 passed`; regression `35 passed`; independent verifier no-residue tests passed except the intended failing exact-graph semantic case | Full R1B cannot pass because TOP-AC-02 fails | `PASS for covered regression/no-residue, OVERALL FAIL` |

## Blocking Finding

### BF-01 — Exact `EvidenceVersion` graph cycle defense is broadened into a same-series prohibition

Result: `BLOCKING`

Files:

- `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/services.py:2358`
- `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/services.py:1551`
- `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/services.py:875`
- `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/tests/test_evidence_services.py:1226`

Problem:

`_validate_derivation_links()` rejects a support if the support's `evidence_series_id` equals the current revised series:

```python
if support.evidence_series_id == derived_evidence_series_id:
    raise EvidenceInvalidDerivationLink(...)
```

This is broader than the frozen WP04 contract and the R1B task contract. The contract defines `evidence_derivation_link.supporting_evidence_version_id` as an exact `EvidenceVersion` foreign key, prohibits exact self-links, and requires cycle detection by traversing exact derivation links. It does not state that every historical exact version from the same `EvidenceSeries` is forbidden as support.

Impact:

- A changed support set that includes an older exact EvidenceVersion from the same series is rejected before `_revision_identity_changed()` can route to replacement v1.
- The replacement path required by R1B TOP-AC-03 is therefore unreachable for this valid exact-version graph case.
- The candidate test labeled “self support” uses `supporting_evidence_version_id=derived.id`, which is an old exact version during revision, not an exact self-link to the not-yet-created replacement version. That test encodes the overbroad same-series interpretation.

Independent reviewer finding:

The `requesting-code-review` reviewer independently reported the same blocking issue and gave a `FAIL` opinion.

## Independent Counterexample Evidence

Verifier-owned test file:

`/tmp/test_wp04_02_r1b_reverify.py`

Command:

```bash
PYTHONPATH=/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service \
pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_reverify.py -rs
```

Final result after fixing verifier fixture wiring:

```text
F...                                                                     [100%]
1 failed, 3 passed in 4.63s
```

Failing node:

`test_replacement_can_support_prior_exact_version_without_exact_cycle`

Observed failure:

```text
backend.evidence.errors.EvidenceInvalidDerivationLink: Evidence cannot derive from its own series
```

Scenario:

1. Create source-backed support `F1`.
2. Create DERIVED exact version `D1` supported by `F1`.
3. Revise/correct `D1` with a changed support set `{D1, F1}`.
4. This is not an exact-version cycle: there is an edge from the new replacement version to existing exact `D1`; traversal from `D1` does not reach the new not-yet-created exact version.
5. Expected under contract: support set changed, so create replacement EvidenceSeries v1 with `supersedes_evidence_version_id=D1`.
6. Actual: service rejects before replacement routing with same-series prohibition.

Passing verifier-owned nodes:

- `test_cross_instrument_invalid_replacement_leaves_no_residue`
- `test_manual_matching_caller_origin_does_not_override_canonical_identity`
- `test_derivation_failure_does_not_write_link_rows`

These passing nodes provide additional evidence that some R1B boundaries work, but they do not neutralize the blocking exact-graph failure.

## Command Evidence

All commands were run from the candidate worktree unless otherwise noted.

| Command | Result |
|---|---|
| `git status --short --branch --untracked-files=all` | `M backend/evidence/services.py`; `M tests/test_evidence_services.py` |
| `git rev-parse HEAD` | `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af` |
| `git rev-parse HEAD^` | `3eb494e6613cf3952ffbaaf4166b8cf3ea801555` |
| `git diff-tree --no-commit-id --name-status -r HEAD` | exactly 3 added files |
| `git diff --name-status` | exactly 2 modified files |
| Current candidate `shasum -a 256 ...` | matched reverify prompt expected hashes |
| `pytest -p no:cacheprovider -q tests/test_evidence_services.py -k r1b -rs` | `4 passed, 91 deselected, 2 warnings in 3.87s` |
| `PYTHONPATH=<candidate> pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_reverify.py -rs` | `1 failed, 3 passed in 4.63s` |
| `PYTHONPATH=<candidate> pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1a_verifier.py -rs` | `12 passed in 6.84s` |
| `pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs` | `95 passed, 2 warnings in 75.21s` |
| `pytest -p no:cacheprovider -q tests/test_evidence_persistence.py tests/test_migrations.py tests/test_evidence_migrations.py tests/test_research_api.py tests/test_research_persistence.py -rs` | `35 passed, 4 warnings in 25.06s` |
| `ruff check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py` | `All checks passed!` |
| `ruff format --check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py` | `3 files already formatted` |
| `MYPYPATH=. mypy --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1b-reverify-mypy ...` | `Success: no issues found in 3 source files` |
| `PYTHONPYCACHEPREFIX=/tmp/tg-r1b-reverify-pycache python -m compileall -q ...` | exit 0 |
| `DATABASE_URL=postgresql+asyncpg://thesisguard:thesisguard_dev_password@127.0.0.1:15432/thesisguard alembic -c migrations/alembic.ini heads` | `000000000004 (head)` |
| `git diff --check` | exit 0 |

## No-Residue and Immutable Snapshot Evidence

Evidence from candidate tests:

- Failure paths compare `EvidenceSeries`, `EvidenceVersion`, `EvidenceSourceLocator`, `EvidenceInstrumentLink`, `EvidenceDerivationLink`, `EvidenceIdempotencyRecord`, and `EvidenceAuditEvent` counts through `evidence_table_counts`.
- Candidate R1B tests cover wrong MANUAL origin, source-less invalid provenance, DERIVED invalid role/missing support/duplicate edge, wrong DERIVED origin, same-series self/cycle fixture, wrong CROSS scope, invalid non-nullable clear, incomplete extractor provenance and partial extractor pair.

Evidence from verifier-owned tests:

- `test_cross_instrument_invalid_replacement_leaves_no_residue`: passed; invalid replacement member leaves table counts unchanged.
- `test_derivation_failure_does_not_write_link_rows`: passed; duplicate derivation edge leaves full counts and explicit `EvidenceDerivationLink` count unchanged.
- `test_replacement_can_support_prior_exact_version_without_exact_cycle`: failed before write due overbroad semantic rejection. This is not a residue failure; it is a contract semantic failure.

Historical child-row immutability:

- Candidate tests verify same-support DERIVED metadata change appends N+1 and old derivation rows remain unchanged.
- Candidate tests verify DERIVED and CROSS_INSTRUMENT tombstones preserve mandatory child rows.
- No independent contradiction found, but R1B still fails due BF-01.

## Required / Achieved / Missing Acceptance

| Level | Required | Achieved | Missing |
|---|---:|---:|---|
| `L1_STATIC_REVIEWED` | yes | yes | none |
| `L2_BUILD_VERIFIED` | yes | yes | none |
| `L3_CONTRACT_VERIFIED` | yes | no | exact-version derivation graph semantics fail |
| `L4_DB_VERIFIED` | yes | no | independent real-PostgreSQL counterexample fails |

## Candidate and Main State After Verification

Candidate worktree:

```text
## codex/wp04-02-evidence-domain-service...origin/codex/wp04-02-evidence-domain-service
 M backend/evidence/services.py
 M tests/test_evidence_services.py
```

Candidate HEAD:

```text
f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af
```

Main worktree before persisting this report:

```text
## main...origin/main
?? docs/acceptance/TASK-WP04-02-R1B-REBASELINE-REVERIFY-R1-task-contract.md
?? docs/acceptance/TASK-WP04-02-R1B-acceptance.md
```

Verifier did not modify candidate code, candidate tests, Git history, branch state, or `main` business code. The only intended main-worktree additions from this verifier are this report and the minimal repair contract.

## Final Decision Rationale

`FAIL`.

The rebaseline itself is accepted: `f7c50ab` is the authorized replacement baseline, its parent and three-file delta match, and its committed blobs are content-equivalent to the R1A-R2 accepted candidate. The candidate also preserves R1A and passes its own R1B tests, the full service suite, the 35-test regression suite, Ruff, format, mypy, compileall, Alembic and diff checks.

However, the original R1B semantic AC remain unchanged. The implementation rejects a valid exact-version replacement scenario because it treats any support from the same EvidenceSeries as a derivation error. The frozen contract requires exact EvidenceVersion self/cycle validation by graph traversal, not a broad same-series prohibition. This is a blocking semantic failure in TOP-AC-02 and TOP-AC-03.

R1B is not accepted. R1C/R1D/WP04-03 remain blocked until a narrow R1B repair passes independent re-verification.

