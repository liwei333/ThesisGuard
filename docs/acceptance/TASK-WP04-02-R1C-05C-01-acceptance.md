# TASK-WP04-02-R1C-05C-01 — Independent Acceptance

OVERALL: BLOCKED

## Metadata / verdict boundary

- Date: 2026-09-16, Asia/Shanghai.
- Verifier: Codex, independent code/persistence reviewer.
- Executor status: IMPLEMENTATION_COMPLETE.
- Required: L1_STATIC_REVIEWED, L2_BUILD_VERIFIED, L3_CONTRACT_VERIFIED, L4_DB_VERIFIED.
- Achieved fresh: L1_STATIC_REVIEWED, L2_BUILD_VERIFIED.
- Missing fresh: successful independent contract/DB verification and safe resolution of verifier-run temporary DB residue.
- Blocker: verifier-side executable PATH assembly and temporary database ownership/cleanup approval. Not a demonstrated business-code failure; no business Repair required.
- Skills: ai-task-governor, ai-task-prompt-architect, verification-before-completion, using-superpowers; systematic-debugging used after the verifier setup error.
- Path follows AGENTS.md's docs/acceptance convention.

## Baseline / changed-files snapshot

```text
main HEAD   438738c543e4cae3e805d31324b068c1cd5c7059
main parent 7d3734bc8346c16f9bbf7f7d9806309949c996de
main branch main; tracked/index empty

candidate branch codex/wp04-02-evidence-domain-service
HEAD   0cef44fd2ffd929b40e849e607af0bd4c44d14d2
parent bdd70edc153b6ed5def65ed99c41f325df45f066
 M backend/evidence/services.py
 M tests/test_evidence_services.py

3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  errors.py
7ce76b02928019347625048e7d0acb523d74168cd6bbbdf03184163ac277f959  services.py
b5bfcdeb2db6753c71fd146b935dd26229daae0d73da5bda68af437db137b950  tests/test_evidence_services.py
```

BASELINE_CHANGED_FILES: candidate two cumulative changes; main existing untracked docs and executor report/evidence. Executor-attributable delta: reported 21 service additions and 557 appended test lines, corroborated by task-specific patch and original test-prefix hash. Candidate cumulative diff from HEAD includes earlier accepted slices and is not wholly attributable to 05C-01.

FINAL_CHANGED_FILES: same candidate files and main tracked/index state, plus this report, the verifier-only successor contract and read-only temporary DB inventory. No candidate or existing document edits by this reviewer.

## Classification / gate selection

- Type: backend service/persistence repair acceptance, MEDIUM, Full matrix.
- Risk: lifecycle permission, idempotency/replay, append-only history, multi-table persistence.
- Selected: baseline, scope, contract, architecture, test, DB persistence, regression, evidence.
- Baseline/scope/architecture static gates: PASS. Fresh DB/test/regression completion gates: BLOCKED, not FAIL.

## Full AC evidence matrix

| AC | Requirement | Inspected evidence | Fresh independent evidence / limit | Result |
| --- | --- | --- | --- | --- |
| AC1 | Genuine tests-only RED | Saved red-two/red-all20 logs and metadata, expected missing-domain-error failures; original service hash recorded | Artifact hashes verified; RED was not recreated by altering candidate. Current independent run produced setup ERROR, explicitly not RED | PASS for saved RED evidence |
| AC2 | Five forbidden statuses/four paths, real prior details before writes | Shared _validate_ordinary_correction_prior and three call sites; ordinary branches only, after replay, before new writes | Full static review finds no blocking code defect; fresh assertion execution unavailable | BLOCKED for runtime acceptance |
| AC3 | Caller commit/fresh-session nine-table equality/no key or history residue | 20 parametrized tests select every table column, compare full snapshots after caller commit, check exact prior/current and outer/inner keys | Inspected assertions and saved proofs; independent run never reached assertions | BLOCKED |
| AC4 | Allowed controls/routing/audit/COMMITTED replay | 16 positive, 3 ordinary replay, 2 disclosed legacy replay cases; exact support IDs and strict audit/history assertions | Test source reviewed; no new DERIVED support policy, preserved replay branches; fresh DB result unavailable | BLOCKED |
| AC5 | Full verifier/regression/static matrix and protected scope | 35 recorded commands; final matrix logs/hash/exit values inspected | Fresh Ruff/format/mypy/compileall/heads pass; DB matrix intentionally stopped after unsafe setup failure | BLOCKED |

## Fresh static and integrity checks

- Fresh candidate/main status, HEAD/parent, errors/services/tests and executor report SHA-256 match feedback.
- Executor report SHA-256: e1678c9818f6673cf950433c3ae3b183c3a45f83b36e7cb0828da65d09057dfd.
- All 80 manifest-listed artifacts have matching byte lengths and SHA-256; report hash matches its manifest. This proves current artifact integrity, not automatic acceptance of self-reported runtime results.
- Independently checked all 283 named main protected files and 63 non-authorized candidate protected files against the saved path/hash map: no mismatch. Seven durable verifier hashes match.
- Original 191662-byte test prefix SHA-256 remains dce8c3644441399ef443d54073c3121e8f59ebcd330c6955458c5db703056308; no old test prefix rewrite.
- All 14 saved final-matrix log hashes and exit-0 metadata match. Logs report focused 41, 05A 11, 04A 87, tuple 4, oracle 58, five verifiers 70, full service 378, regressions 35. These are executor-run recorded results, not fresh independent successes.
- Fresh Ruff check/format: exit 0, all checks pass / three formatted files.
- Fresh mypy: exit 0, no issues in three source files; unused module-config note is non-blocking.
- Fresh compileall: exit 0; cache redirected outside candidate.
- Fresh Alembic heads: exit 0, 000000000004 (head); no standalone migration executed.
- Three diagnostic variables TG_TEST_ADMIN_DATABASE_URL, TG_R1C_REPLAY_BASELINE, TG_R1C02_REPLAY_PRIOR checked UNSET.

## Independent verifier failure — owned by this review

This reviewer ran the original focused suite via normal require_escalated permission, with explicit Homebrew pytest and candidate/Homebrew PYTHONPATH, but failed to assemble an explicit subprocess PATH containing the inspected Alembic executable.

```text
41 selected nodes, 337 deselected
41 setup ERROR, exit 1
FileNotFoundError: [Errno 2] No such file or directory: 'alembic'
```

The failure occurs at the original pg_sessionmaker fixture subprocess.run, line 105. The fixture creates a UUID-named database before launching Alembic; its teardown try/finally begins only after successful migration/engine setup. Therefore these failures did not register the normal yielded-fixture cleanup for the created DBs. This is a verifier-side environment assembly error, not a 05C-01 domain assertion failure and not evidence of business RED.

The normal shell can see /opt/miniconda3/bin/alembic and direct static/head commands succeeded. The executor's successful command environment explicitly prepends /opt/miniconda3/bin; the failed independently escalated test used no explicit PATH assembly. Future verifier preflight must check executable discovery under exactly the effective child environment before DB creation.

No further DB tests, DB deletion, connection termination or code/fixture modification was attempted after diagnosing this.

## Read-only residue diagnosis and limits

Two normally approved read-only diagnostics were run on the same 127.0.0.1:15432 instance:

1. PostgreSQL 16 psql --list: exit 1 due to the PostgreSQL 17 catalog column rename (d.daticulocale); no mutation.
2. Narrow system-catalog SELECT of names starting tg_wp04_service_: exit 0, 45 names returned. Full observed names are in TASK-WP04-02-R1C-05C-01-independent-db-inventory.json.

There was no pre-run DB-name snapshot. Although 41 setup failures imply this run likely created 41 of those 45 names, the exact ownership of each name is not independently proven. Do not label all 45 as this run's DBs or assume they are empty. Do not delete by prefix, list length, age alone or reported count.

The inventory is a read-only observation, NOT a cleanup authorization or a confirmed deletion list. User approval and per-database ownership/emptiness/connection checks are needed before any extra exact cleanup outside the original fixture. No business/shared/production DB or Docker volume may be targeted.

## Blocking findings / no business repair

- BLOCKING: independent DB assertions have not succeeded; verifier setup left potentially uncleaned disposable databases and exact ownership lacks a before-snapshot.
- Owner: this independent review, not the candidate executor.
- Business repair required: NO, absent demonstrated code defect.
- Non-blocking: candidate code/test scope and saved evidence are consistent; static review found no unauthorized latest/support/hash/concurrency implementation.

## Next action

Next smallest task is TASK-WP04-02-R1C-05C-01-INDEPENDENT-REVERIFY-R1, verifier-only. First fix the effective tool environment without edits/installations and produce a read-only, per-database ownership/cleanup plan. Only after explicit approval of an exact confirmed cleanup list may it clear those disposable DBs and complete the original full verification matrix.

Do not dispatch 05C-02, change the candidate, create a business R2 or claim 05C-01 PASS until this verifier closure completes. No Git integration, R1C/WP04-02 completion, trusted success or source/support/time policy is authorized.
