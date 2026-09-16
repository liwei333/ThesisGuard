# TASK-WP04-02-R1C-03A-VERIFY-PREREQUISITES-R1 — Independent Review

## Metadata

- OVERALL: `FAIL — VERIFIER_REPAIR_REQUIRED`.
- Task: `TASK-WP04-02-R1C-03A-VERIFY-PREREQUISITES-R1`.
- Date: 2026-09-16, Asia/Shanghai.
- Verifier: Codex, independent review of execution evidence and current repository.
- Report path: docs/acceptance, following AGENTS and existing project convention.
- Required Acceptance: L1_STATIC_REVIEWED, L2_BUILD_VERIFIED, L3_CONTRACT_VERIFIED, L4_DB_VERIFIED; Full matrix.
- Achieved this turn: L1_STATIC_REVIEWED, L2_BUILD_VERIFIED.
- Missing closure evidence: corrected independent all-route oracle and fresh complete verification on an explicitly adopted current baseline.
- Repair Required: YES, verifier-only repair `TASK-WP04-02-R1C-03A-ORACLE-R1`.

This FAIL concerns the newly authored supplemental verifier and incomplete verification deliverable. It is **not** a finding that R1C-03A business behavior fails, and does not authorize changing business code. The executor correctly preserved failing evidence and did not self-approve. Restored original artifacts and recorded runtime results remain useful evidence.

## Baseline, scope and chronology

Input: `/Users/qianduoduo/.codex/attachments/848fdd72-8d93-43e3-9272-00d72631a6fe/pasted-text.txt`.

Read original prerequisite task, execution report, frozen lifecycle/correction/audit schema, new supplemental verifier, candidate seed/command/audit code, recovery manifest, command records, failure log and snapshots. No candidate or old evidence was edited.

The execution packet identifies its historical baseline as bdd70ed + two modified files. Recorded successful matrix ended by 2026-09-16T01:32:03Z. Current repositories have subsequent commits at about 09:41 +08:00:

```text
main HEAD: 438738c543e4cae3e805d31324b068c1cd5c7059
main parent: 7d3734bc8346c16f9bbf7f7d9806309949c996de
main initial status this turn: clean

candidate branch: codex/wp04-02-evidence-domain-service
candidate HEAD: 0cef44fd2ffd929b40e849e607af0bd4c44d14d2
candidate parent: bdd70edc153b6ed5def65ed99c41f325df45f066
candidate initial status this turn: clean
candidate commit scope: M backend/evidence/services.py; M tests/test_evidence_services.py
```

Fresh file SHA-256 values still exactly equal the reviewed R1C-03A candidate:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
43b548232df4267f377c5e144222c9278c3cc478f6800720240c4618b689ebe3  backend/evidence/services.py
47ff645c0f782af67e9f6ee64520105febdb28c6547a43bf89b435bead6c5108  tests/test_evidence_services.py
```

0cef44f commits exactly the cumulative R1C changes: 1136 insertions, 25 deletions in the two files; errors.py is not in its scope. Main's new commit adds documentation/evidence, including other pre-existing untracked documents. Commit titles are not implementation evidence. These later commits are not attributed to the recovery executor; this review does not infer who authorized them. Current clean/HEAD state differs from the old fixed contract, so it is not silently adopted or repaired through Git operations.

BASELINE_CHANGED_FILES for this review: candidate NONE; main NONE. Task-attributable changes this turn: this new review report and a proposed verifier-only repair contract. Existing candidate, all old source/evidence, and Git history are preserved.

## Independent evidence checks actually completed

1. Rehashed five original /tmp artifacts and their five durable copies: every hash matches the original contract, and each pair is identical by SHA-256.
2. Checked all 66 entries in evidence-file-manifest.json against actual file sizes and SHA-256: no missing/mismatching entry. Manifest SHA is 15e57d836f05cfefaf59508f50d79db7aaa8cee591d138d28ce2062c66e033e2.
3. Checked all 37 command-results log references against log_sha256: no mismatch.
4. Checked the 12 referenced original Add File/patch source records at their exact known export line numbers against recorded SHA-256: no mismatch. Source recovery is supported by complete original records, not summary reconstruction.
5. Observed an existing Docker backend listener at TCP15432 using lsof. Recorded postgres identity/volume/17.11 readiness is available in the hash-checked packet. This review did not run a new PG transaction or start/replace infrastructure.
6. Fresh candidate Ruff check and format check passed; mypy passed for three files (existing unused-section note); compileall passed. Both repositories' latest commit diff-check passed. Candidate HEAD/parent/scope/status/file hashes were read directly.

Static commands use /opt/miniconda3/bin tools, the three arguments backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py, and no-cache/check flags. Mypy uses explicit-package-bases, ignore-missing-imports, MYPYPATH=. and /tmp/tg-r1c03a-oracle-review-mypy; compileall uses /tmp/tg-r1c03a-oracle-review-pycache. No installation or dependency upgrade occurred.

DB tests were **not rerun in this turn** because the candidate no longer meets the old fixed HEAD/dirty precondition. The following are verified recorded execution results, not newly executed test claims:

| Recorded target | Result / exit |
| --- | --- |
| focused | 142 passed, 97 deselected / 0 |
| R1C-02 / R1C-01 originals | 43 / 8 passed / 0 |
| R1B wiring / reverify / R1A originals | 3 / 4 / 12 passed / 0 |
| full services | 239 passed / 0 |
| persistence/migration/Research regression | 35 passed, 2 warnings / 0 |
| supplemental boundary oracle | 15 failed, 43 passed / 1 |

Hash integrity and byte equality do not establish fresh acceptance of a changed Git baseline. Original successful results are not discarded; they also do not override the supplemental coverage defect.

## Root findings: verifier defects, not business repair findings

### VF-01 — Invalid automatic-route input construction (11 nodes)

New verifier `docs/acceptance/verifiers/test_wp04_02_r1c03a_prerequisites_boundary_20260916.py:80` requires old_support.supersedes_evidence_version_id to be non-null before calling revise_correct_evidence.

The shared seed calls verified_evidence_fact, which creates a brand-new source-backed FACT v1 without a predecessor (candidate tests:300-372). The derived seed links that exact initial FACT; subsequent lifecycle versions of the derived series copy that same support ID (tests:3438-3520). A predecessor is therefore not guaranteed and in these recorded cases is None. Initial v1 with no predecessor is explicitly legitimate under frozen section12.

Nine negative automatic inputs and two ordinary automatic cases stop in verifier construction; they do not exercise the intended service. Deleting the assertion without supplying a valid different exact support would not fix the coverage gap. A correct oracle must construct a real distinct eligible exact support via lawful public setup, prove different origin/identity and acyclic lineage, and capture the rejection baseline only after setup commits.

### VF-02 — Unsupported audit-event literal conflates row lifecycle with event taxonomy (4 nodes)

New verifier line262 requires every correction route's event_type to be EVIDENCE_CORRECTION. For direct/underlying replacement, the create command records EVIDENCE_VERSION_CREATED; same-series append records EVIDENCE_CORRECTION (services:797-814 versus :1508-1517).

Frozen sections12/13 require the persisted EvidenceVersion CORRECTION status tuple and predecessor lineage. Section evidence_audit_event:1351-1363 permits generic Created/etc.; it does not require the same event_type literal for every public route. The four recorded cases had already passed fresh-session row/history/no-inheritance/routing/children assertions when this extra literal expectation failed. Actor/time assertions after line262 were not reached; do not claim they passed.

Changing candidate production event names solely to satisfy this assertion would be unjustified scope expansion. The revised oracle must retain strict row audit fields and verify an exact-version audit event, correct ownership-specific actor/time, and a documented allowed route mapping; do not accept arbitrary events or catch all exceptions.

Preserved old supplemental SHA: 6d3592f86d13ca5e66988a5522542d52cf630ab3ebc0a51121bd786e401b0b89.

Preserved owned-boundary.log SHA: 030b6fba4e6e7d12ddbaee183f45f5be108c1effe333e05b9f2acb93ac9e95d0.

## Full AC / Gate Matrix

| AC | Requirement | Evidence | Boundary / verdict |
| --- | --- | --- | --- |
| 1 | Fixed baseline and no mutation | Historical snapshots/logs preserved; current new clean commit and file equality read directly | Current baseline authorization absent: BLOCKED; no executor scope violation inferred |
| 2 | Original recovery/provenance/exact durable copies | Five paired hashes, 12 source records, 66-entry manifest check | Recovery content validated: PASS |
| 3 | Original local endpoint, no DB substitution | Original identity/volume packet intact, listener now present | Restoration evidence supported: PASS for recorded restoration, not a fresh PG transaction claim |
| 4 | Correct independent all-entry boundary proof and full regression | Required original matrix packet intact; supplemental has invalid construction/oracle | VF-01/VF-02 prevent intended proof: FAIL |
| 5 | Complete durable truthful evidence | 37 command logs checked, failed log preserved, no expectation edits | Evidence capture PASS; final acceptance not closed |

Task Type VERIFICATION_PREREQUISITE_RESTORE / verifier repair; Size MEDIUM; risks audit/DB integrity/replay; Full matrix. G0 BLOCKED for current baseline, G1 PASS for inspection scope, G2 FAIL and G4 FAIL for supplemental proof, G3 PASS for static ownership review, DB Persistence/G5 BLOCKED for new-baseline final reverification, G6 FAIL for independent coverage gap. Blocking FAIL dominates OVERALL. UI/worker/API implementation/migration-change gates do not apply.

## Decision and next task

The executor's BLOCKED stop was appropriate for its no-expectation-edit authority. Independent review resolves the two oracle problems sufficiently to issue a **verifier-only repair**, not another business repair or repeated environment restoration.

Next: `TASK-WP04-02-R1C-03A-ORACLE-R1`. The proposed contract requests explicit adoption of clean candidate 0cef44f and main438738c for this repair/reverify only. It preserves all old originals, supplemental source, failure logs and packet, creates a separately named corrected oracle, and reruns the Full matrix after user dispatch. The document alone is not authorization to start or a new PASS.

R1C-03A business acceptance remains open. Production approved rules remain empty; positive trusted registry, initial-import/full ordinary-correction qualification, R1D, whole WP04-02 closure, Git integration, Sector Crowding and Capability Runtime remain unadvanced.
