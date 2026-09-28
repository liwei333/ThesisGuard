# TASK-WP04-02-R1C-05C-01 Focused DB Reverify R10 Repair R1
# Feedback Independent Review R1

## 1. Verdict

**OVERALL: FAIL**

**Corrected classification:**
`FAIL_EVIDENCE_PROTOCOL / DOCKER_PREFLIGHT_DIAGNOSTIC_EVIDENCE_INSUFFICIENT`

The R1 executable-resolution repair itself is accepted: the sealed R10 PATH
failure is reproduced, all five required executables are resolved to validated
absolute paths, formal argv binding is enforced, and the original
`FileNotFoundError` does not recur. However, the overall Repair contract also
required a correctly classified one-shot runtime result and evidence sufficient
for independent acceptance.

The D-stage helper calculates three Docker return codes but omits all three from
the published evidence and discards all stderr without publishing a bounded,
safe error category. The resulting artifact contains `desktop-linux` plus null
container/image fields, but cannot distinguish among at least:

1. the target container or image being absent;
2. the Docker daemon being unavailable or access being denied;
3. the selective `--format` command failing;
4. returned output being malformed for the helper's parser; or
5. a real, parseable identity mismatch.

Therefore the artifact proves only that the D gate evaluated false. It does not
prove that the cause was an external PostgreSQL environment condition. The
executor's `BLOCKED_POSTGRESQL_ENVIRONMENT / DOCKER_IDENTITY_MISMATCH`
classification is not independently supportable. This is a task-owned evidence
protocol defect, so the correct overall verdict is `FAIL`, not `BLOCKED`.

R11 and integration remain prohibited.

## 2. Metadata

| Field | Value |
|---|---|
| Review task | `TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10-REPAIR-R1-FEEDBACK-INDEPENDENT-REVIEW-R1` |
| Repair task | `TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10-REPAIR-R1` |
| Repair worktree | `/Users/qianduoduo/.codex/worktrees/r10-exec-resolution-repair/ThesisGuard` |
| Branch state | detached HEAD |
| Baseline / evidence-commit parent | `3b8650ee069b6eb364520d5ae127ee205bb4345d` |
| Evidence commit / HEAD | `4de35dd15d03dd05748f4c9e3129c2951faa1365` |
| Review date | 2026-09-26 Asia/Shanghai |
| Verifier | independent Codex |
| Report path | `docs/acceptance/TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10-REPAIR-R1-FEEDBACK-INDEPENDENT-REVIEW-R1-acceptance.md` |
| Task type | `REPAIR + OPERATIONS + TESTING + REAL_POSTGRESQL_VERIFICATION` |
| Risk type | one-shot budget, credential boundary, DB lifecycle, evidence classification |
| Task size | `MEDIUM` |
| Evidence matrix | Full |

Required acceptance:

- `L1_STATIC_REVIEWED`
- `L2_BUILD_VERIFIED`
- `L3_CONTRACT_VERIFIED`
- `L4_RUNTIME_VERIFIED`
- `L4_DB_VERIFIED`

Achieved acceptance:

- `L1_STATIC_REVIEWED`
- `L2_BUILD_VERIFIED`
- `L3_CONTRACT_VERIFIED` for the executable-resolution Repair boundary only

Missing acceptance:

- `L4_RUNTIME_VERIFIED`: no validly classified Docker/PostgreSQL runtime chain
- `L4_DB_VERIFIED`: readiness, identity, collection, pytest and lifecycle were
  not reached

## 3. Scope and attribution

Included:

- exact Git ancestry, clean detached worktree and changed-file scope;
- R1 execution report and complete final evidence tree;
- RED/GREEN executable-resolution evidence and sealed helpers;
- D-stage Docker command construction, parsing and published schema;
- execution events, budgets, not-run accounting and classification;
- protected-input, worktree, credential, JSON/JSONL and manifest integrity; and
- selection of the minimum R2 Repair.

Excluded:

- replaying the consumed R1 supervisor;
- running any fresh Docker command or accessing the Docker daemon;
- socket, credential, SQL, secure proof, collect-only or pytest execution;
- database mutation, container mutation or environment remediation;
- modifying the R1 worktree or evidence commit;
- integration, merge, rebase, cherry-pick, push or PR; and
- R11 or later WP-04 work.

The evidence commit has the exact claimed baseline as its sole parent, adds 31
files, changes only the two R1 formal output paths, passes `git show --check`,
and leaves the R1 worktree clean.

## 4. Accepted executable-resolution Repair

The following original R10 failure is closed and must not be reimplemented in
R2:

- RED proves the sealed R10 `SAFE_ENV.PATH` cannot resolve bare `docker` and
  identifies the three bare Docker call sites;
- RED side-effect counters for subprocess, Docker, network, socket, SQL,
  credentials, proof child and formal writes are all zero;
- GREEN validates exact absolute paths for Git, Docker, `pg_isready`, Python
  3.12 and pytest;
- each inventory entry is an executable regular file and records its realpath;
- formal argv uses inventory-bound absolute paths;
- missing, directory, non-executable and realpath-mismatch counterexamples fail
  closed;
- an injected Docker resolution failure bypasses Docker/TCP/proof/collect/pytest;
- C2 executes and passes before D in the formal event chain; and
- the original `FileNotFoundError` is not reproduced.

Fresh independent Ruff and AST checks passed for all four sealed helper files.
This supports `L3_CONTRACT_VERIFIED` for the narrow executable-resolution
boundary. It does not prove the D-O runtime/database boundary.

## 5. Decisive D-stage evidence defect

The formal helper runs exactly these three read-only Docker commands through the
validated absolute Docker path:

1. `docker context show`;
2. selective `docker inspect --format ... thesisguard-postgres`; and
3. selective `docker image inspect --format ... pgvector/pgvector:pg17`.

The helper receives:

- `context_code`;
- `inspect_code`; and
- `image_code`.

It also receives stderr for every command. But the function discards stderr and
publishes none of the three return codes. Its published
`docker-postgres-preflight.json` contains only the parsed identity fields and a
boolean `gate_passed`.

Observed published facts are:

- Docker executable resolution passed;
- Docker context text is `desktop-linux`;
- `gate_passed=false`;
- container/image/health/mount/restart fields are null; and
- port mapping is false.

Those facts do not reveal whether container inspect failed, image inspect
failed, parsing failed, or parseable values mismatched. The context command can
return `desktop-linux` from local Docker configuration even when later daemon
operations fail, so context text alone is not sufficient external-environment
evidence.

The previously accepted R9 Repair preflight demonstrates the required pattern:
it published `context_return_code`, `inspect_return_code`, and
`image_inspect_return_code` in addition to safe identity fields. Its successful
artifact recorded all three as zero. R1 regressed this diagnostic boundary by
omitting those fields.

No fresh Docker access is needed to establish this defect; it is visible in the
sealed helper and final evidence schema.

## 6. Runtime claims and preserved safe behavior

The formal event chain is internally consistent:

```text
A -> B -> C -> C2 -> D -> P -> Q
```

Accepted safe facts:

- one escalated Repair supervisor invocation and zero default-sandbox formal
  supervisor invocations;
- supervisor retry zero;
- one selective, read-only, three-command Docker preflight;
- Docker mutation zero;
- container environment, env-file, logs and full inspect were not read;
- `pg_isready`, TCP, proof, collect-only and real pytest invocation counts are
  zero;
- task database create/drop sends, manual cleanup, `DROP ... FORCE`,
  `pg_terminate_backend` and historical mutation are zero;
- proof parent/child/retry is `0/0/0`; and
- no later gate was bypassed after D evaluated false.

Not accepted or not verified:

- an exact external cause for the D-stage result;
- current container/image/daemon state;
- PostgreSQL readiness or reachability;
- safe PostgreSQL identity;
- the exact 41-node collection contract;
- historical-45/live-catalog/quiescence/observer evidence;
- the real 41-node pytest result; and
- fixture lifecycle, restoration and post-run observation.

These later values remain `NOT_RUN` or `UNKNOWN`; they cannot inherit historical
R9 values.

## 7. Fresh independent integrity checks

Fresh checks performed without Docker, network, socket, credentials, SQL,
proof, collection or pytest confirmed:

- `HEAD=4de35dd15d03dd05748f4c9e3129c2951faa1365`;
- `HEAD^=3b8650ee069b6eb364520d5ae127ee205bb4345d`;
- changed files: 31; out-of-scope paths: 0;
- manifest: 29 listed and 29 actual non-manifest files; missing/hash/byte
  mismatch `0/0/0`;
- report SHA-256:
  `7f240d20a970775c132a64e90cf86a098d92827b16e07a80c1bb4b03b4130bfa`;
- manifest SHA-256:
  `0094a0b957c3702f5dc7cc7dc96efbd960a7498df53546c39197be20f0a3de52`;
- final JSON/JSONL: 25 files, 31 documents, invalid 0;
- final independent credential scan: 30 evidence files plus report, findings 0;
- protected-input before/after diff: 0 across 11 entries;
- worktree-snapshot before/after diff: 0;
- repository pycache before/after: `0/0`, task-created/changed 0;
- Ruff: `All checks passed!`; and
- AST parsing: four helper files passed.

The stored credential scan reports 28 evidence files because it explicitly
excludes itself and the manifest; a fresh independent scan of all 30 final
evidence files plus the report found zero findings. The stored JSON audit was
generated before the last two JSON artifacts and reports 23 files/29 documents;
the final-tree independent result is 25 files/31 documents. Both are explainable
finalization-order differences and do not block evidence integrity.

## 8. Full evidence matrix

| Blocking acceptance condition | Result | Evidence |
|---|---|---|
| Exact baseline, isolation and evidence-only scope | PASS | parent/HEAD, clean status, 31 paths and scope audit |
| Reproduce original missing Docker resolution without side effects | PASS | sealed RED evidence and independent source inspection |
| Resolve and bind all formal executables before D | PASS | inventory, C2 event, GREEN negative cases and sealed argv code |
| Preserve proof/no-clobber/credential/mutation boundaries | PASS | hashes, budgets, proof preflight, scans and snapshots |
| Produce independently classifiable D-stage evidence | FAIL | Docker return codes and bounded error categories are absent |
| Prove the reported external Docker/PostgreSQL blocker | FAIL | null fields have multiple task-local/external causes |
| Complete the original R10 D-O runtime chain | FAIL | E-O are `NOT_RUN`; no L4 runtime/DB evidence |
| Tamper-evident final bundle | PASS | manifest, report hash, JSON/JSONL and final credential scan pass |

## 9. Acceptance gates

| Gate | Result | Reason |
|---|---|---|
| G0 Baseline | PASS | Exact parent, detached HEAD, clean status and ancestry verified |
| G1 Scope | PASS | Evidence-only 31-file commit; out-of-scope 0 |
| G2 Contract | FAIL | Runtime outcome cannot be classified from published D-stage evidence |
| G3 Architecture | NOT_APPLICABLE | No production architecture change |
| G4 Test/runtime | FAIL | Executable regression passes, but the required runtime chain is not verified |
| DB Persistence | BLOCKED | No real DB path was reached after D; external cause is not proven |
| G5 Regression | PASS | Original executable-resolution defect is closed with RED/GREEN evidence |
| G6 Evidence | FAIL | Critical Docker return-code/error-category evidence is missing |

Blocking G2, G4 and G6 failures require `OVERALL=FAIL`, regardless of the
unreached DB gate.

## 10. Counterexamples

| Risk | Result |
|---|---|
| Treat `desktop-linux` text as proof the daemon/container is available | Rejected; later daemon commands can still fail |
| Treat all-null identity fields as proof the container is absent | Rejected; format, daemon, permission and parser failures produce the same artifact |
| Treat executable GREEN as proof of Docker identity | Rejected; it proves launch binding only |
| Treat D failure as permission to continue to readiness/TCP | Preserved fail-closed behavior; all later counts are zero |
| Retry the one-shot supervisor | Preserved; retry zero |
| Leak raw Docker stderr while diagnosing | Preserved; raw stderr is absent, but a bounded category is also missing |

## 11. Repair decision

**Repair required: YES**

Repair ID:

`TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10-REPAIR-R2`

R2 must start from exact commit
`4de35dd15d03dd05748f4c9e3129c2951faa1365` in a new clean managed worktree.
The R1 worktree and its evidence are immutable root evidence.

R2 must only close the D-stage diagnostic-classification defect and then rerun
the original verification once under a new, explicitly approved budget. It must
preserve the accepted executable resolver and all security/mutation/no-retry
boundaries.

Before runtime, R2 must prove offline that:

1. context, container-inspect and image-inspect return codes are always
   published;
2. parse status and observed field count are published without raw output;
3. safe, bounded categories distinguish daemon unavailable, permission denied,
   container missing, image missing, format/parse failure and parseable identity
   mismatch;
4. raw stderr, raw inspect output, credentials and container environment remain
   absent; and
5. each failure category stops before readiness/TCP/proof/collect/pytest.

After those gates pass, R2 may consume exactly one new escalated supervisor
invocation for the full D-O chain. If the external Docker environment is truly
unavailable, R2 may end `BLOCKED_POSTGRESQL_ENVIRONMENT`, but only with the safe
return-code/category evidence that proves it. Helper/format/parser failures must
be `FAIL_EVIDENCE_PROTOCOL`.

Until R2 independently passes:

- R11 allowed: **NO**
- Integration allowed: **NO**
- Candidate accepted: **NO**
- WP-04-02 / WP-04: **`PARTIALLY_IMPLEMENTED`**
- Production readiness: **not established**
- Strategy status: **`UNPROVEN`**
