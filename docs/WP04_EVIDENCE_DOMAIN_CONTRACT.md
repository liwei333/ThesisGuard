# WP-04 Evidence Domain Contract

## 1. Document Status

Status: implementation contract for WP-04.

Task: TASK-WP04-00.

Scope: documentation only. This file freezes the Evidence domain semantics that
WP04-01 must implement in PostgreSQL models, Alembic migration, and domain
services. It does not implement Python code, migrations, API, OpenAPI, frontend
client, worker jobs, MinIO writes, embeddings, RAG, or Thesis logic.

Authority level: this contract is the WP-04 source for Evidence domain identity,
versioning, source provenance, deduplication, idempotency, concurrency, storage
truth, and the WP03 Research reference migration target. Current source code and
accepted WP03 public contracts remain the authority for the current system.

## 2. Purpose and Scope

The purpose is to remove ambiguity before persistence work begins. WP04-01 must
not decide again what an Evidence unit is, which entity is versioned, how source
documents differ from atomic Evidence, which ID Research and Thesis must cite,
how correction and retraction preserve history, or which storage system owns
truth.

In scope:

- Evidence domain vocabulary and state machines.
- Source document identity, immutable source versions, and locators.
- Atomic Evidence identity and immutable Evidence versions.
- PostgreSQL, MinIO, pgvector, Redis, event, and LLM truth boundaries.
- Deduplication, idempotency, and optimistic concurrency contracts.
- Database, command/query, and error blueprints for WP04-01 through WP04-03.
- WP03 `source_refs: list[str]` current fact and migration target.

Out of scope:

- Any implementation change.
- Any modification of WP03 code, schema, OpenAPI, generated client, or existing
  documentation.
- Any new user, tenant, or authorization model beyond the current V1
  single-user boundary.
- Any automatic trading capability.

## 3. Authoritative Sources

Current implementation and accepted contract sources read for this contract:

| Source | Contract use |
|---|---|
| `AGENTS.md` | Project invariants: Thesis First, Fact over narrative, LLM only proposes, immutable history, PostgreSQL/MinIO/pgvector/Redis roles. |
| `README.md` | Product principles, evidence chain, Research knowledge library, Agent anti-appeasement, no auto trading. |
| `docs/ThesisGuard_V1_Technical_Architecture_Design.md` | Existing Evidence sketch, storage split, SourceGrade S-E, Research pipeline, RAG metadata, WP-04 and WP-05 dependencies. |
| `docs/ThesisGuard_V1_PRD.md` | Evidence must include content, source, date, related Thesis, source grade, verification status; InformationType; SourceGrade S-F and F-grade restriction. |
| `docs/STRUCTURED_OUTPUT_CONTRACTS.md` | LLM Proposal boundary, Pydantic/semantic/domain validation, raw value and normalized value, page/table/paragraph locator, source references. |
| `docs/AGENT_RUNTIME_ARCHITECTURE.md` | PostgreSQL durable truth; Redis is live fan-out/coordination; domain events separate from runtime events; idempotency and revision principles. |
| `docs/PROJECT_STATUS_AUDIT_2026-09-12.md` | Pre-WP03 status and risk: Evidence/Thesis contracts absent, Redis durable-truth risk, fact boundary blocker. |
| `docs/WP03_RESEARCH_PACKAGE_API.md` | Current Research API, request hashing, idempotency, expected_version, error envelope, `source_refs` fact boundary. |
| `docs/WP03_RESEARCH_PACKAGE_PERSISTENCE.md` | Append-only Research versions, current by highest version, copy-on-write modules, `source_refs` defaults. |
| `docs/WP03_RESEARCH_PACKAGE_CLIENT.md` | Generated client boundary and current generated Research model contract. |
| `docs/acceptance/TASK-WP03-INTEGRATION-acceptance.md` | WP03 integrated into local main with 67-test local baseline. |
| WP03 acceptance reports | Repairs closed typed error contracts, generated client contracts, idempotency, concurrency, and append-only Research behavior. |
| `backend/research/*` | Current Research models, schemas, services, API, request hash, expected_version, errors, and source_refs implementation. |
| `migrations/versions/20260912_003_research_package.py` | Actual WP03 table constraints and source_refs JSON column. |
| `backend/instrument/*` | Current string UUID primary key convention and instrument foreign-key style. |
| `backend/common/storage.py` | Existing MinIO client boundary. |
| `backend/common/events.py` | Existing Redis Stream helper and `evidence.created` event name, not a durable fact store. |
| `apps/web/src/api/generated/*Research*` | Current generated Research package/module/error model surface. |
| `tests/test_research_api.py` and `tests/test_research_persistence.py` | Executable current behavior for idempotency, expected_version, concurrency, and empty source_refs. |

## 4. Current Implementation Reality

Current implemented facts:

- `backend/evidence/` contains only `__init__.py`; there is no Evidence model,
  migration, service, API, worker, parser, MinIO writer, embedding pipeline, or
  RAG implementation.
- WP03 has append-only `research_package` versions and `research_module`
  snapshots.
- `ResearchModule.source_refs` is a PostgreSQL JSON column exposed as
  `source_refs: list[str]` in Pydantic and generated TypeScript.
- WP03 does not have a typed Evidence foreign key. A string inside `source_refs`
  is not a database reference and must not be interpreted as one.
- WP03 idempotency is `(instrument_id, idempotency_key)` plus server-generated
  `request_hash`. Same key and same hash replays the existing package; same key
  and different hash raises `IDEMPOTENCY_CONFLICT`.
- WP03 refresh uses `expected_version`; two concurrent refreshes based on the
  same current version produce at most one next version.
- `backend/common/events.py` defines `evidence.created`, but events are published
  via Redis Streams only and are not durable Evidence truth.
- `backend/common/storage.py` can put and get MinIO objects, but no Evidence raw
  object contract is implemented.
- PostgreSQL contains pgvector extension support, but no Evidence embedding
  table exists.

Implementation gap:

- The project has a product/architecture concept of Evidence, source grade,
  RAG, and immutable history, but the entity boundary and version semantics were
  not previously frozen at implementation level.

## 5. Problem Statement

WP04 must prevent five classes of schema drift:

1. Raw source documents must not be merged with atomic Evidence facts.
2. Stable logical identity must not be merged with immutable version rows.
3. Research and Thesis must not cite floating URLs, titles, or latest/current
   pointers when an audit reference is required.
4. Corrections, disputes, invalidations, and retractions must not overwrite or
   delete historical rows.
5. Redis, pgvector, LLM output, and events must not become the system of record
   for Evidence truth.

## 6. Domain Glossary

`SourceDocument`: stable logical identity for one source document lineage. It
answers "which issuer/source document is this?" It does not own the bytes.

`SourceDocumentVersion`: immutable version of one SourceDocument. It answers
"which exact content, versioned metadata, SourceGrade, MinIO object reference,
and source lifecycle snapshot was committed?"

`EvidenceSeries`: stable logical identity for one atomic Evidence lineage. It
answers "which claim lineage, scope, and provenance origin is this?"

`EvidenceVersion`: immutable version of one EvidenceSeries. It answers "which
exact atomic claim/value/status/provenance snapshot was committed?"

`SourceLocator`: exact location of source-backed EvidenceVersion support inside
one specific SourceDocumentVersion. Manual provenance is not a SourceLocator.

`InformationType`: one of `FACT`, `ESTIMATE`, `THESIS_INFERENCE`,
`USER_HYPOTHESIS`.

`SourceGrade`: one of `S`, `A`, `B`, `C`, `D`, `E`, `F`.

`VerificationStatus`: current reliability status encoded on each immutable
EvidenceVersion row.

`current Evidence`: derived read result for the highest version of an
EvidenceSeries. It is not a mutable pointer.

`current valid Evidence`: derived read result that first reads the highest
version of an EvidenceSeries and then checks eligibility. It must not fall back
to an older version when the highest version is ineligible.

`source-backed Evidence`: EvidenceSeries and EvidenceVersion with
`provenance_kind='SOURCE_BACKED'`, one stable `primary_source_document_id`, and
one exact `source_document_version_id` per EvidenceVersion.

`source-less Evidence`: EvidenceSeries and EvidenceVersion with manual or
derived provenance and no SourceDocumentVersion. It must not invent SourceGrade
or SourceLocator rows.

`identity dimension`: one of the fields included in `series_identity_hash`:
`scope_type`, `scope_key`, `information_type`, `claim_key`, `metric_key`,
`period_start`, `period_end`, `provenance_kind`,
`primary_source_document_id`, or `origin_key`.

## 7. Canonical Entity Boundary

Selected entity boundary:

| Concept | Stable ID | Immutable version ID | Owned truth |
|---|---|---|---|
| SourceDocument | `source_document.id` | none | source identity and issuer-level canonicalization. |
| SourceDocumentVersion | `source_document_version.id` | itself | exact content hash, version_fingerprint, versioned metadata, MinIO object references, source grade snapshot, source lifecycle snapshot. |
| EvidenceSeries | `evidence_series.id` | none | stable claim lineage, normalized scope, and provenance origin. |
| EvidenceVersion | `evidence_version.id` | itself | atomic claim/value/status/provenance snapshot. |
| SourceLocator | `evidence_source_locator.id` | itself | locator from an EvidenceVersion to one SourceDocumentVersion. |

Raw documents and atomic Evidence cannot be one entity:

- One annual report can contain hundreds of facts, estimates, and management
  statements.
- One atomic fact can be corroborated by multiple source documents, but each
  source lineage remains its own EvidenceSeries. Corroboration is expressed by
  immutable links, not by stuffing multiple source lineages into one
  EvidenceVersion.
- One source document can be corrected without making every extracted Evidence
  lineage identical.
- One Evidence correction can change a normalized value while the raw document
  remains unchanged.
- RAG chunks and embeddings are retrieval aids for source text, not atomic
  business facts.

## 8. Identity and Versioning Model

SourceDocument identity:

- Primary key: UUID string.
- Stable logical key: `(publisher_key, source_type, external_document_id)` when
  external ID exists; otherwise `(publisher_key, source_type, canonical_url)`.
- `canonical_url` is normalized but does not alone define identity when a stable
  exchange/issuer identifier exists.

SourceDocumentVersion identity:

- Primary key: UUID string.
- Version: integer starting at `1`, strictly increasing per SourceDocument.
- `content_hash` is the lowercase SHA-256 hex digest of canonical raw bytes.
  For HTML, the bytes are the captured normalized document bytes stored in
  MinIO. It never includes observation time, fetch time, SourceGrade, parser
  metadata, or review metadata.
- `version_fingerprint` is the lowercase SHA-256 hex digest of canonical JSON
  with sorted keys and normalized timestamp strings for:
  `content_hash`, `media_type`, `source_grade`, `published_at`,
  `source_version_label`, `source_revision_id`, `document_language`,
  `parser_name`, `parser_version`, `text_object_hash`, `source_status`,
  `source_status_changed_at`, `source_status_reason`,
  `source_status_actor`, and `versioned_metadata`.
- `observed_at` and `fetched_at` do not participate in source-version identity.
  Re-observation of the same fingerprint records observation/audit metadata and
  reuses the existing SourceDocumentVersion.
- Unique constraints: `(source_document_id, version)` and
  `(source_document_id, version_fingerprint)`.
- Ordinary indexes: `content_hash`, `source_grade`, `observed_at`,
  `published_at`, and `source_status`.
- Content is immutable. Changed raw bytes, grade reclassification, versioned
  metadata correction, source lifecycle notice, parser-output correction, or
  source-stated revision creates a different version_fingerprint and a new
  SourceDocumentVersion.
- MinIO object keys may be reused for identical canonical bytes by content hash.
  A SourceDocumentVersion points at the reused object key when bytes match and
  at a new object key when bytes differ.

EvidenceSeries identity:

- Primary key: UUID string.
- Stable logical key: `series_identity_hash`.
- `series_identity_hash` is SHA-256 over canonical JSON with:
  `scope_type`, `scope_key`, `information_type`, `claim_key`, `metric_key`,
  `period_start`, `period_end`, `provenance_kind`, `primary_source_document_id`,
  and `origin_key`.
- `scope_type` is one of `INSTRUMENT`, `MARKET`, `SECTOR`, `POLICY`, or
  `CROSS_INSTRUMENT`.
- `scope_key` is non-null. For `INSTRUMENT`, it is the instrument UUID. For
  `MARKET`, it is the fixed value `MARKET`. For `SECTOR`, it is the canonical
  sector key. For `POLICY`, it is the policy domain key. For
  `CROSS_INSTRUMENT`, it is a stable hash of the sorted linked instrument IDs.
- `metric_key`, `period_start`, and `period_end` are canonicalized with explicit
  JSON null values before hashing; PostgreSQL nullable UNIQUE semantics are not
  used to define EvidenceSeries identity.
- Source-backed series use `provenance_kind='SOURCE_BACKED'`,
  `primary_source_document_id` non-null, and `origin_key` null.
- Source-less user-authored or derived series use `primary_source_document_id`
  null and non-null `origin_key`. `origin_key` is `manual:{actor}:{normalized
  manual subject}` for manual provenance and `derived:{sorted supporting
  evidence version ids hash}` for derived provenance.
- The domain service may reuse an existing series only when
  `series_identity_hash` matches. Same claim from a different source lineage has
  a different `primary_source_document_id`, therefore a different series.
- Correction using a newer SourceDocumentVersion from the same
  `primary_source_document_id` stays in the same EvidenceSeries and appends an
  EvidenceVersion.
- Any change to an identity dimension creates a new EvidenceSeries starting at
  version 1. The first EvidenceVersion in the new series records
  `supersedes_evidence_version_id` pointing to the exact prior EvidenceVersion.
- Replacement EvidenceVersion v1 is not brand-new initial evidence. It is a
  correction lineage event even though its per-series `version` equals 1.
  Therefore it must set `supersedes_evidence_version_id` to the replaced exact
  EvidenceVersion and must record non-null `status_changed_at`,
  `status_changed_by_actor`, `status_change_kind='CORRECTION'`, and
  `status_reason`. Ordinary replacement v1 has `verification_status='UNREVIEWED'`;
  trusted deterministic replacement v1 may have `verification_status='VERIFIED'`
  only when the command also records a non-null `trusted_correction_rule`.
- Identity-changing data must not be appended as EvidenceVersion N+1 inside the
  previous EvidenceSeries.
- Corrections that keep all identity dimensions unchanged may append
  EvidenceVersion N+1 in the same series. These include claim content,
  normalized value, display text, status, locator, source_grade_snapshot, or a
  newer SourceDocumentVersion under the same `primary_source_document_id`.
- For `CROSS_INSTRUMENT`, changing the sorted instrument ID set changes
  `scope_key`, therefore creates a new EvidenceSeries. Changes only to
  instrument-link role, display order, or link metadata for the same sorted ID
  set may append an EvidenceVersion in the same EvidenceSeries with new
  immutable `evidence_instrument_link` child rows.
- For `DERIVED`, changing the sorted supporting EvidenceVersion ID set changes
  `origin_key`, therefore creates a new EvidenceSeries. Changes only to
  derivation role, support_order, support_weight, or derived expression for the
  same supporting ID set may append an EvidenceVersion in the same
  EvidenceSeries with new immutable `evidence_derivation_link` child rows.

EvidenceVersion identity:

- Primary key: UUID string.
- Version: integer starting at `1`, strictly increasing per EvidenceSeries.
- Unique constraint: `(evidence_series_id, version)`.
- Every content change, normalization change, status change, correction,
  invalidation, retraction, or source-grade snapshot change creates a new
  EvidenceVersion.
- A new EvidenceVersion cannot change the parent EvidenceSeries identity
  dimensions. If the payload changes any identity dimension, the command creates
  a new EvidenceSeries version 1 instead.
- Brand-new initial EvidenceVersion v1 has no predecessor:
  `supersedes_evidence_version_id` is null. Only this no-predecessor v1 may use
  the all-null lifecycle audit tuple when it is `UNREVIEWED`.
- Replacement EvidenceVersion v1 has a predecessor:
  `supersedes_evidence_version_id` is non-null. It can never use the all-null
  lifecycle audit tuple solely because `version=1`.

Current rule:

- `current` is a derived query: highest `version` for one EvidenceSeries.
- There is no mutable `current_version_id` pointer in V1.
- `current valid` first reads the same highest version. If that version is
  `RETRACTED`, `INVALIDATED`, `REJECTED`, `DISPUTED`, `UNREVIEWED`, or otherwise
  ineligible for the requested downstream role, the series is currently
  unavailable for that role. The query must not fall back to an older eligible
  version.
- Query helpers may return current, current valid eligibility, or exact version,
  but audit references always store exact `evidence_version.id`.

Delete policy:

- No physical delete for SourceDocument, SourceDocumentVersion, EvidenceSeries,
  EvidenceVersion, locator, idempotency record, or audit event.
- Test database teardown and failed uncommitted transactions are outside the
  domain model.
- Future retention can archive MinIO objects only when exact history references
  remain resolvable and a tombstone object preserves metadata.

## 9. InformationType Contract

Allowed values:

| Value | Meaning | Source requirement | Thesis core support |
|---|---|---|---|
| `FACT` | Objective statement about a company, metric, event, filing, policy, or market condition. | Requires exactly one primary SourceDocument lineage, one exact SourceDocumentVersion, and at least one SourceLocator. | Allowed when SourceGrade is not F and the latest EvidenceVersion is eligible. |
| `ESTIMATE` | Forecast, analyst estimate, management guidance, consensus, target price, or model projection. | External estimates require source version and locator. User-authored estimates may be source-less only with manual provenance. | Allowed as support only when clearly marked as estimate and not F-grade rumor. |
| `THESIS_INFERENCE` | Derived reasoning connecting facts or estimates to an investment thesis. | May be source-less only when it has at least one exact supporting EvidenceVersion through `evidence_derivation_link`. | Allowed only as reasoning support, never as the sole core support. |
| `USER_HYPOTHESIS` | User-authored claim or assumption. | Requires `created_by_actor='USER'`, `manual_entry_reason`, timestamp, and optional cited EvidenceVersion IDs. | Not allowed as confirmed support until promoted by verified Evidence. |

LLM extraction:

- LLM may propose all four information types.
- The proposal is not a system record until the Evidence domain service validates
  structure, source locator, semantic constraints, current version, and allowed
  state transition.
- The submitted EvidenceVersion records `extractor_type`, `extractor_version`,
  and `created_by_actor`.

Type changes:

- `information_type` is immutable within an EvidenceSeries.
- Reclassification across type creates a new EvidenceSeries and links the old
  version via non-null `supersedes_evidence_version_id` on the replacement
  EvidenceVersion v1.

Display versus machine fields:

- Display fields: `display_title`, `display_text`, `source_quote`,
  `short_citation`.
- Machine fields: `claim_key`, `metric_key`, `raw_value`, `raw_unit`,
  `normalized_value`, `normalized_unit`, `period_start`, `period_end`, `as_of`,
  `currency`, `source_locator`.

## 10. SourceGrade Contract

Allowed values and meanings:

| SourceGrade | Meaning |
|---|---|
| `S` | Company announcement and formal financial report. |
| `A` | Exchange, regulator, official data, or official policy source. |
| `B` | Company investor relations, investor communication, or institution survey first-party material. |
| `C` | Broker research report. |
| `D` | Authoritative financial media. |
| `E` | Social media, public account, forum, or unverified online discussion. |
| `F` | Rumor or unverified information. |

Selected decision:

- SourceGrade is stored on SourceDocumentVersion for source-backed Evidence.
- EvidenceVersion snapshots SourceGrade at commit time as
  `source_grade_snapshot` for source-backed Evidence.
- Source-less EvidenceVersion rows set `source_grade_snapshot` to null. They do
  not fabricate an S-F value.
- SourceGrade reclassification creates a new SourceDocumentVersion with the same
  content hash and reusable object key, a different `version_fingerprint`, a new
  version number, and `version_reason='GRADE_RECLASSIFICATION'`.
- Evidence that should reflect the new grade creates a new EvidenceVersion.

Invariant:

- Historical EvidenceVersion and future ThesisVersion audit reads use the grade
  snapshot they cited at the time.
- Query layers can show that a newer source version has a lower grade.

F-grade rule:

- F-grade EvidenceVersion may exist only in the unverified intelligence pool.
- F-grade EvidenceVersion cannot become core Thesis support.
- The future Thesis service enforces this at the command boundary that links
  EvidenceVersion to core Thesis support.
- Evidence service also exposes a stable error blueprint for attempts to create
  core support links with F-grade Evidence.

## 11. SourceType Contract

Selected decision: closed enum in V1.

Allowed `SourceType` values and complete SourceGrade compatibility policy:

| Value | Allowed SourceGrade values |
|---|---|
| `COMPANY_ANNOUNCEMENT` | S |
| `FINANCIAL_REPORT` | S |
| `EXCHANGE_FILING` | A |
| `REGULATORY_DATA` | A |
| `OFFICIAL_DATA` | A |
| `POLICY_DOCUMENT` | A |
| `INVESTOR_RELATIONS` | B |
| `INSTITUTIONAL_SURVEY` | B, C |
| `BROKER_RESEARCH` | C |
| `INDUSTRY_REPORT` | C or D |
| `FINANCIAL_MEDIA` | D |
| `SOCIAL_MEDIA` | E, F |
| `RUMOR` | F |
| `WEB_PAGE` | D, E, or F |
| `USER_NOTE` | F |

Extension rule:

- Adding a SourceType requires a migration or enum-contract change, generated
  schema update, and regression tests.
- Unknown strings are rejected at the domain boundary.
- The enum value is uppercase snake case, maximum 64 characters, and stored in a
  PostgreSQL check constraint or enum-compatible string constraint matching the
  project style.

Validation:

- SourceType and SourceGrade are validated by the complete matrix above.
- Any pair not listed above is invalid and returns
  `EVIDENCE_INVALID_SOURCE_GRADE`.
- Source-less Evidence has no SourceDocument row, no SourceType, and null
  `source_grade_snapshot`; it is validated by manual or derivation provenance
  rules instead of this matrix.

## 12. Verification and Lifecycle State Machine

Allowed `VerificationStatus` values:

| Status | Meaning | Terminal |
|---|---|---|
| `UNREVIEWED` | Created by extraction or manual entry and not yet accepted for use. | No |
| `PENDING_REVIEW` | Human or deterministic review has been requested. | No |
| `VERIFIED` | Domain service accepted the EvidenceVersion for eligible downstream use. | No |
| `REJECTED` | Review found the EvidenceVersion unsupported or invalid before downstream use. | Yes for that version |
| `DISPUTED` | A challenge exists; the version remains readable but not eligible as fresh core support. | No |
| `INVALIDATED` | The claim was time-expired or disproved by later evidence. | Yes for that version |
| `RETRACTED` | Source or domain operation withdrew the version from valid use. | Yes for that version |

Initial status:

- Default initial status is `UNREVIEWED`.
- A deterministic system command may create `VERIFIED` only when the source type,
  locator, schema, and semantic checks are all satisfied in the same transaction.
- Ordinary correction creates `UNREVIEWED` and must be reviewed again.
- A deterministic trusted correction command may create `VERIFIED` only when it
  names the trusted correction rule and completes schema, source, locator,
  semantic, status metadata, and audit checks in the same transaction. It does
  not inherit prior status by default.

Status audit metadata:

- `status_changed_at`, `status_changed_by_actor`, `status_change_kind`, and
  `status_reason` are all-null only for brand-new initial version 1 with
  `verification_status='UNREVIEWED'`, `supersedes_evidence_version_id` null, and
  no lifecycle transition.
- The four fields are all-non-null for every post-creation lifecycle/status
  append, including ordinary correction that produces `UNREVIEWED`.
- The four fields are all-non-null for initial direct `VERIFIED` trusted import.
- The four fields are all-non-null for every replacement EvidenceVersion v1
  where `supersedes_evidence_version_id` is non-null. Replacement/correction
  cannot bypass audit requirements by starting a new EvidenceSeries at
  `version=1`.
- Partial null status audit metadata is invalid.
- Allowed `status_change_kind` values and command mapping:
  `INITIAL_VERIFICATION` for initial trusted import directly to `VERIFIED`;
  `REVIEW_REQUEST` for `request_review`;
  `REVIEW_DECISION` for `verify_evidence` and `reject_evidence`;
  `DISPUTE` for `mark_disputed` and dispute resolution;
  `INVALIDATION` for `invalidate_evidence`;
  `RETRACTION` for `retract_evidence`;
  `CORRECTION` for ordinary correction and trusted deterministic correction.

State transition table:

| From | Command | To | Creates EvidenceVersion | Notes |
|---|---|---|---:|---|
| none | create_evidence_version | UNREVIEWED | Yes | Brand-new extraction or manual entry; status audit fields all-null only for no-predecessor version 1. |
| none | create_verified_evidence_version | VERIFIED | Yes | Deterministic trusted import; status_change_kind INITIAL_VERIFICATION. |
| prior exact EvidenceVersion | create_replacement_evidence_series | UNREVIEWED or VERIFIED | Yes | Identity-changing correction creates replacement v1; sets non-null supersedes_evidence_version_id and complete CORRECTION audit tuple. |
| UNREVIEWED | request_review | PENDING_REVIEW | Yes | Same content, status revision; status_change_kind REVIEW_REQUEST. |
| PENDING_REVIEW | verify_evidence | VERIFIED | Yes | Requires actor and review evidence; status_change_kind REVIEW_DECISION. |
| UNREVIEWED | reject_evidence | REJECTED | Yes | No downstream link allowed; status_change_kind REVIEW_DECISION. |
| PENDING_REVIEW | reject_evidence | REJECTED | Yes | No downstream link allowed; status_change_kind REVIEW_DECISION. |
| VERIFIED | mark_disputed | DISPUTED | Yes | Keeps exact prior version readable; status_change_kind DISPUTE. |
| DISPUTED | resolve_dispute_verified | VERIFIED | Yes | May keep same content or include corrected content; status_change_kind DISPUTE. |
| DISPUTED | resolve_dispute_rejected | REJECTED | Yes | Current version becomes rejected; status_change_kind DISPUTE. |
| VERIFIED | invalidate_evidence | INVALIDATED | Yes | Used for expiry or disproving event; status_change_kind INVALIDATION. |
| VERIFIED | retract_evidence | RETRACTED | Yes | Creates complete tombstone EvidenceVersion; status_change_kind RETRACTION. |
| DISPUTED | retract_evidence | RETRACTED | Yes | Complete tombstone current version; status_change_kind RETRACTION. |
| VERIFIED | correct_evidence | UNREVIEWED | Yes | Default correction; status_change_kind CORRECTION; must be reviewed again. |
| VERIFIED | trusted_deterministic_correction | VERIFIED | Yes | Named deterministic correction rule; status_change_kind CORRECTION. |

Illegal transitions:

- Any terminal version row cannot be modified in place.
- `REJECTED`, `INVALIDATED`, and `RETRACTED` cannot be promoted by updating the
  same row.
- A new version may supersede a terminal version only by appending `N+1`.

Distinctions:

- VerificationStatus is not SourceGrade. SourceGrade evaluates source quality;
  VerificationStatus evaluates this committed EvidenceVersion.
- VerificationStatus is not current/latest. Current is a query result by version.
- Retraction and invalidation are reliability lifecycle outcomes encoded as new
  immutable versions.

Historical read:

- Exact version reads return the status recorded on that version.
- Series reads show current status plus any newer correction/retraction lineage.
- Current valid reads never scan backward to an older eligible version. A latest
  DISPUTED, INVALIDATED, RETRACTED, REJECTED, or UNREVIEWED version means the
  series is currently unavailable for downstream roles requiring eligibility.

## 13. Correction, Dispute, Invalidation and Retraction

Correction:

- Meaning: content or normalized value is corrected because source or extraction
  was wrong.
- Action: creates a new SourceDocumentVersion when source content changed.
- If all EvidenceSeries identity dimensions are unchanged, creates a new
  EvidenceVersion in the same EvidenceSeries.
- If correction changes `scope_type`, `scope_key`, `information_type`,
  `claim_key`, `metric_key`, `period_start`, `period_end`, `provenance_kind`,
  `primary_source_document_id`, or `origin_key`, it creates a new EvidenceSeries
  starting at version 1 and links to the replaced exact EvidenceVersion through
  non-null `supersedes_evidence_version_id`.
- Result status: `UNREVIEWED` for ordinary correction. Only
  `trusted_deterministic_correction` may create a corrected `VERIFIED` version.
- Ordinary correction records non-null `status_changed_at`,
  `status_changed_by_actor`, `status_change_kind='CORRECTION'`, and
  `status_reason`; it cannot omit audit metadata because UNREVIEWED is also the
  default initial status.
- Identity-changing ordinary correction records the same correction audit tuple
  on the replacement EvidenceVersion v1. Its `version=1` value does not make it a
  brand-new no-predecessor initial row.
- Trusted deterministic correction records the same four status audit fields,
  `status_change_kind='CORRECTION'`, and non-null `trusted_correction_rule`.
- Prior Research/Thesis exact references stay pointed at the old
  EvidenceVersion.
- Query can show `superseded_by_evidence_version_id`.

Dispute:

- Meaning: an actor challenges the validity, interpretation, or locator.
- Action: creating a dispute note is an audit event; changing status to
  `DISPUTED` creates a new EvidenceVersion.
- Current version changes only after the status-version append commits.

Invalidation or expiry:

- Meaning: claim is no longer valid for its effective window, or later evidence
  disproves it.
- Action: creates a new EvidenceVersion with `VerificationStatus=INVALIDATED`,
  `status_changed_at`, `status_changed_by_actor`,
  `status_change_kind='INVALIDATION'`, and `status_reason`.
- The INVALIDATED tombstone is a complete EvidenceVersion snapshot. It copies
  forward all required claim, display, provenance, source, grade, metric/value,
  period/as_of/effective, extractor, and manual fields from the prior version
  unless the invalidation command explicitly supplies a corrected replacement
  value that does not change EvidenceSeries identity.
- Source-backed, DERIVED, and CROSS_INSTRUMENT mandatory child rows are copied
  for the new tombstone EvidenceVersion as needed to satisfy provenance and
  query constraints.
- The old version remains readable.

Retraction:

- Meaning: source is withdrawn or the domain owner withdraws the Evidence from
  valid downstream use.
- Action: creates a tombstone EvidenceVersion with
  `VerificationStatus=RETRACTED`.
- RETRACTED is not a sparse row. It is a complete EvidenceVersion snapshot that
  satisfies every non-null field and conditional provenance constraint in the
  `evidence_version` table.
- Tombstone creation copies forward still-valid snapshot fields from the prior
  version, including `information_type`, `provenance_kind`, `display_title`,
  `display_text`, `claim_key`, metric/value/unit/currency fields,
  period/as_of/effective fields, `source_document_version_id`,
  `source_grade_snapshot`, extractor fields, and manual provenance fields.
- Tombstone creation updates `verification_status`, `status_changed_at`,
  `status_changed_by_actor`, `status_change_kind='RETRACTION'`,
  `status_reason`, `supersedes_evidence_version_id`, and `created_at`.
- Source-backed tombstone versions copy mandatory immutable SourceLocator child
  rows for the new EvidenceVersion when the prior version had them.
- DERIVED tombstone versions copy mandatory immutable `evidence_derivation_link`
  child rows for the new EvidenceVersion.
- CROSS_INSTRUMENT tombstone versions copy mandatory immutable
  `evidence_instrument_link` child rows for the new EvidenceVersion.
- Historical EvidenceVersion rows and their original child rows are not modified
  or deleted.
- Raw MinIO object is not physically deleted in V1. Metadata marks the source
  version as retracted through SourceDocumentVersion fields
  `source_status='RETRACTED'`, `source_status_changed_at`,
  `source_status_actor`, and `source_status_reason`; exact audit reads remain
  resolvable.

UI/API hint rule:

- A read of a referenced old version returns the exact old version plus relation
  metadata: newer version exists, disputed, invalidated, or retracted.
- No reference silently drifts to a newer version.

## 14. Source Identity and Provenance

Canonical source URL:

- Lowercase scheme and host.
- Strip URL fragment except when the fragment is the only stable web anchor.
- Remove known tracking parameters.
- Preserve path, query parameters that identify the document, and issuer domain.
- URL canonicalization is not the same as content identity.

Publisher and issuer:

- Store `publisher_key`, `publisher_name`, `issuer_key`, `issuer_name`, and
  `issuer_instrument_id` when known.
- For company announcements, issuer is the company; publisher can be exchange or
  company channel.

External document identifier:

- Store exchange announcement ID, regulator filing ID, report ID, URL canonical
  key, or provider document ID when present.

Times:

- `published_at`: source-stated publication time.
- `observed_at`: time ThesisGuard observed or fetched the source.
- `fetched_at`: time raw object was stored.
- Evidence `as_of`: time the claim is true or evaluated.

Content hash:

- Hash input is canonical raw bytes for binary files.
- For HTML pages, hash input is the captured normalized document content stored
  in MinIO, not live URL content.
- Hash algorithm is SHA-256 hex. It identifies canonical bytes only and is not
  the SourceDocumentVersion unique key.

Version fingerprint:

- Hash algorithm is SHA-256 hex over the canonical JSON fields listed in section
  8.
- `observed_at` and `fetched_at` are excluded.
- Grade reclassification, versioned metadata correction, source retraction
  notice, parser-output correction, or byte correction changes the
  version_fingerprint.

Object key:

- MinIO object key is immutable and based on content hash plus extension. The
  same canonical bytes may be reused by multiple SourceDocumentVersion rows.
- If MinIO write succeeds and the PostgreSQL transaction later fails, retry uses
  content_hash to discover the orphaned object and either reuses it or marks it
  as an orphan in audit/maintenance metadata. No committed Evidence or source
  version exists until PostgreSQL commits.

Language, parser, and extractor:

- Store `document_language`.
- Store `parser_name`, `parser_version`, `extractor_name`,
  `extractor_version`, and `prompt_template_version` when an LLM or parser
  proposed extraction.

Actors:

- `created_by_actor` is one of `SYSTEM`, `USER`, `LLM_PROPOSAL`,
  `IMPORTER`, `ADMIN_SCRIPT`.
- Manual entry requires `manual_entry_reason`.
- Automatic extraction requires source document version and extractor metadata.

Separate actions:

- Collection action observes and stores source bytes.
- Extraction action proposes facts from a source version.
- Domain commit action creates SourceDocumentVersion and EvidenceVersion rows.
- Manual provenance action records actor, reason, observed time, and optional
  supporting EvidenceVersion IDs without creating a SourceDocumentVersion.

## 15. Source Locator Contract

SourceLocator belongs to one source-backed EvidenceVersion and one exact
SourceDocumentVersion from the EvidenceSeries primary SourceDocument lineage.
Source-less manual or derived Evidence has no SourceLocator row.

Required fields:

- `source_document_version_id`.
- `locator_type`.
- `raw_locator`.
- `short_citation`.
- `locator_payload`.

Allowed locator types:

- `PAGE`
- `PAGE_PARAGRAPH`
- `SECTION`
- `TABLE`
- `TABLE_CELL`
- `WEB_ANCHOR`
- `TIME_RANGE`

Locator payload:

- Page locator: `page_number`, optional `bbox`.
- Paragraph locator: `page_number`, `paragraph_index`.
- Table locator: `page_number`, `table_index`, optional `row_index`,
  `column_index`, `cell_ref`.
- Web locator: `canonical_url`, optional `anchor`, `css_selector`,
  `text_quote_hash`.

Manual provenance:

- Manual provenance is stored on EvidenceVersion fields and, when supporting
  Evidence is cited, through `evidence_derivation_link`.
- It is not represented as `locator_type='MANUAL_NOTE'` and must not require a
  fake SourceDocumentVersion.

Integrity:

- The locator's SourceDocumentVersion must equal the EvidenceVersion
  `source_document_version_id`.
- The EvidenceVersion source version must belong to the EvidenceSeries
  `primary_source_document_id`.
- Page, table, paragraph, and cell coordinates must be validated against parser
  metadata when parser metadata exists.
- Invalid locator returns `EVIDENCE_INVALID_SOURCE_LOCATOR`.

## 16. Deduplication Contract

1. SourceDocument recognition:

- Database unique candidate: `(publisher_key, source_type,
  external_document_id)` when external ID exists.
- Fallback unique candidate: `(publisher_key, source_type, canonical_url)`.
- Domain service resolves identity before appending version.

2. SourceDocumentVersion content deduplication:

- Canonical unique key: `(source_document_id, version_fingerprint)`.
- `content_hash` is indexed and may drive MinIO object reuse, but it is not
  sufficient for SourceDocumentVersion identity.
- Reimporting the same fingerprint for the same SourceDocument returns the
  existing SourceDocumentVersion when request hash is identical; with a new
  idempotency key it records a new observation/audit event, not a new source
  version.
- Same URL with different content changes `content_hash`, changes
  `version_fingerprint`, and creates a new SourceDocumentVersion.
- Same bytes with grade reclassification or versioned metadata correction keeps
  `content_hash`, changes `version_fingerprint`, and creates a new
  SourceDocumentVersion while reusing the MinIO object key.
- Same content from a different URL does not merge SourceDocument identity. It
  may share a MinIO blob by object hash, but each SourceDocumentVersion remains
  separate.
- Concurrent imports of the same fingerprint are guarded by unique
  `(source_document_id, version_fingerprint)`. One transaction creates the row;
  others reread and return or reconcile with the existing row.

3. Evidence candidate deduplication:

- Candidate key includes `series_identity_hash`, `source_document_version_id`
  for source-backed Evidence, exact source locator, `normalized_value`,
  `normalized_text_value`, and `normalized_unit`.
- Candidate deduplication prevents duplicate EvidenceVersion rows from the same
  extraction and same source version.

4. EvidenceSeries identity matching:

- Same claim from same source lineage may map to the same EvidenceSeries.
- Same claim from a newer SourceDocumentVersion under the same
  `primary_source_document_id` maps to the same EvidenceSeries.
- Same claim from a different SourceDocument lineage creates a distinct
  EvidenceSeries. Corroboration may link the two exact EvidenceVersions, but
  must not merge lineages.
- Any change to a `series_identity_hash` dimension creates a distinct
  EvidenceSeries with version 1. The service must not append that payload as
  N+1 to the old EvidenceSeries.
- `CROSS_INSTRUMENT` member-set changes and DERIVED supporting-ID-set changes
  are identity changes because they change `scope_key` or `origin_key`.
- Changes only to child-link role, display order, support_order,
  support_weight, link metadata, or expression text may append N+1 when the
  identity dimensions remain unchanged.

5. Semantic similarity candidate:

- Vector or text similarity can create `evidence_similarity_candidate` rows for
  human or deterministic domain review.
- Vector similarity never auto-merges different Evidence lineages.

Counterexamples:

- Same fact from two sources: two lineages remain independent.
- Same URL with changed content: append SourceDocumentVersion with a new
  version_fingerprint.
- Same content at different URL: separate SourceDocument identity, optional
  shared blob.
- Same source repeated with unchanged bytes: no extra source version.
- Same source repeated with unchanged bytes and changed observed_at only: no
  extra source version.
- Same bytes with grade or versioned metadata correction: append
  SourceDocumentVersion with reused object bytes.
- Similar sentence with different period, unit, or value: separate Evidence.
- Correcting `metric_key`, `period_start`, or `period_end`: new EvidenceSeries,
  not a version append.
- CROSS_INSTRUMENT A+B changed to A+C: new EvidenceSeries because `scope_key`
  changes.
- DERIVED support set V1+V2 changed to V1+V3: new EvidenceSeries because
  `origin_key` changes.

## 17. Idempotency Contract

Scope:

- Idempotency key scope is `operation + target aggregate`.
- Source import scope: `source_document:{source_document_id or identity_key}`.
- Evidence create/revise scope: `evidence_series:{evidence_series_id or
  proposed_series_identity_hash}`.
- Research reference refresh scope:
  `research_instrument:{instrument_id}:expected:{expected_research_version}`.

Request hash:

- Server computes canonical `request hash` from operation, target ID,
  canonical semantic payload, source document version IDs, locator payload,
  normalized value fields, `version_fingerprint`, expected_version, or
  `expected_research_version` for Research snapshot refresh.
- Evidence create/correct request hash includes the canonical identity
  dimensions used to compute `series_identity_hash`. When any identity
  dimension differs, the request targets a different EvidenceSeries creation
  or lineage-supersession operation rather than an append to the old series.
- Idempotency key is not part of request hash.

Replay:

- Same key and same request hash returns the first committed result reference.
- Same key and different request hash returns
  `EVIDENCE_IDEMPOTENCY_CONFLICT`.
- The conflict is not retryable with the same key.

Failure handling:

- Structural validation errors before transaction do not occupy the key.
- Domain validation errors before any write do not occupy the key.
- Unknown outcome after a database or storage uncertainty creates a record with
  `status='UNKNOWN_OUTCOME'`; the same key must reconcile before retry.
- Successful mutation and idempotency record commit in the same transaction when
  no MinIO write is needed. When MinIO is involved, PostgreSQL records object key
  and content hash only after successful object write; the DB transaction owns
  the durable source metadata.
- Source import ordering is: validate payload, resolve idempotency key, compute
  content_hash and version_fingerprint, write/reuse MinIO object by content_hash,
  insert SourceDocumentVersion guarded by
  `(source_document_id, version_fingerprint)`, commit idempotency record in the
  same PostgreSQL transaction as source metadata. If DB commit fails after MinIO
  write, retry reconciles by content_hash and version_fingerprint before writing
  another object.

Retention:

- V1 stores idempotency records permanently for source and Evidence writes
  because audit history is permanent.

Relationship to WP03:

- The style matches WP03: same key + same hash replays; same key + different
  hash conflicts.
- WP04 uses an explicit idempotency table because SourceDocumentVersion and
  EvidenceVersion are separate aggregates.

## 18. Optimistic Concurrency Contract

Commands requiring `expected_version`:

- append SourceDocumentVersion after version 1.
- create EvidenceVersion in an existing EvidenceSeries.
- revise, correct, dispute-status-change, verify, reject, invalidate, or retract
  an EvidenceSeries.
- create a new ResearchPackage snapshot with typed Evidence links using
  `expected_research_version`.
- create a replacement EvidenceSeries after identity-dimension change does not
  use the old series `expected_version` to mutate it; it references the replaced
  exact EvidenceVersion through non-null `supersedes_evidence_version_id` and
  starts the new series at version 1.

Meaning:

- `expected_version` is the current highest version number of the target
  SourceDocument or EvidenceSeries at command start.
- `expected_research_version` is the current highest ResearchPackage version for
  the target `instrument_id` at command start. It protects the ResearchPackage
  snapshot sequence, not EvidenceSeries.
- Exact immutable EvidenceVersion IDs do not require EvidenceSeries
  expected_version when being referenced by Research. Their immutability is
  protected by the EvidenceVersion primary key.

Concurrent revision:

- Service locks the aggregate row or uses a unique constraint on
  `(aggregate_id, version)` as the final guard.
- Two requests based on version N attempt N+1.
- At most one commits N+1.
- The loser returns `EVIDENCE_VERSION_CONFLICT` with `expected_version=N` and
  `current_version=N+1`.
- For Research reference refresh, two requests based on ResearchPackage N
  attempt to create ResearchPackage N+1 with typed link children. At most one
  commits; the loser rereads current ResearchPackage version and uses a
  Research-version conflict error.
- For concurrent identity-changing replacement, unique `series_identity_hash`
  permits at most one replacement EvidenceSeries for the same new identity. A
  duplicate creator rereads the existing new series instead of appending to the
  old series.

Ordering with idempotency:

1. Resolve idempotency key.
2. Same key and same request hash returns prior result before concurrency check.
3. Same key and different request hash returns idempotency conflict.
4. New key proceeds to expected_version check.
5. Database unique constraint is the final defense.

## 19. Storage System-of-Record Matrix

| Data | PostgreSQL | MinIO | pgvector | Redis | Rebuildable |
|---|---|---|---|---|---|
| SourceDocument metadata | system of record | no | no | no | no |
| SourceDocumentVersion metadata | system of record | no | no | no | no |
| raw file | object key and hash | system of record for bytes | no | no | no, except refetch creates new version |
| normalized extracted text | metadata and text ref | immutable text object for large text | optional index input | no | yes from raw and parser |
| EvidenceSeries | system of record | no | no | no | no |
| EvidenceVersion | system of record | no | no | no | no |
| SourceLocator | system of record | optional parser artifact | no | no | no |
| content hash | system of record | object metadata | no | no | no |
| embeddings | source metadata and rebuild job state | no | retrieval index only | no | yes from PostgreSQL and MinIO |
| event delivery | durable outbox when implemented | no | no | live fan-out only | yes from PostgreSQL |
| idempotency records | system of record | no | no | no | no |
| parser/extractor result | commit metadata and accepted values | raw/canonical artifact object | no | no | accepted facts no; proposal artifacts yes from stored object |
| audit metadata | system of record | no | no | live projection only | no |

Additional rules:

- PostgreSQL stores all authoritative structured facts.
- MinIO stores immutable bytes and large parser artifacts.
- pgvector stores search indexes that can be rebuilt without changing Evidence
  identity or version.
- Redis loss cannot lose Evidence truth.
- `evidence.created` is a notification about a committed fact, not the fact.
- LLM output before domain service commit is a proposal artifact.

## 20. Cross-Module Reference Contract

Evidence to Instrument:

- EvidenceSeries uses non-null `scope_type` and `scope_key` for identity.
- `scope_type='INSTRUMENT'` stores the instrument UUID in `scope_key`.
- `scope_type='MARKET'`, `SECTOR`, `POLICY`, and `CROSS_INSTRUMENT` avoid
  nullable identity fields.
- Cross-instrument Evidence uses immutable child rows in
  `evidence_instrument_link` attached to the exact EvidenceVersion snapshot that
  expressed the claim.

Research reference target:

- Target contract: ResearchPackage/ResearchModule audit references store exact
  `evidence_version.id`.
- Current/latest lookups may be used to build a view, but persisted audit links
  use exact EvidenceVersion.
- Current WP03 behavior is authoritative: ResearchPackage is append-only per
  instrument, ResearchModule belongs to one exact ResearchPackage version, and
  refresh creates ResearchPackage N+1 without mutating N.
- `research_module_evidence_link` is an immutable child of a ResearchModule
  snapshot. Rows are created only inside the transaction that creates a new
  ResearchPackage/ResearchModule snapshot.
- Post-hoc insert, update, or delete of links for an existing historical
  ResearchModule is forbidden.
- Changing typed Evidence references creates ResearchPackage N+1 for the
  instrument with `expected_research_version=N`.
- Copy-on-write of unchanged modules from N to N+1 copies typed link rows as new
  child rows pointing at the same exact EvidenceVersion IDs.
- If cited Evidence is later corrected or retracted, old Research links continue
  to point at the original EvidenceVersion. Current Research views may display
  a warning or suggested newer EvidenceVersion, but they must not modify the old
  link.

Thesis reference target:

- Future ThesisVersion support, opposition, and invalidation links store exact
  EvidenceVersion IDs.

Current WP03 fact:

- `research_module.source_refs` currently stores `list[str]`.
- It is free-form JSON string data, not a typed Evidence foreign key.
- It remains unchanged in this task.

Migration target:

- A follow-up task adds `research_module_evidence_link` with exact
  `research_module_id`, `research_package_id`, `evidence_version_id`,
  `link_role`, `created_at`, and audit fields as immutable ResearchModule
  snapshot children.
- Existing string `source_refs` can be retained as legacy display notes until
  migration completes.
- No code may treat existing strings as valid database references.

Retracted referenced version:

- Exact read resolves old version and displays status.
- New core Thesis support cannot use RETRACTED, INVALIDATED, REJECTED,
  DISPUTED, UNREVIEWED, or F-grade EvidenceVersion.

## 21. Database Blueprint

All primary keys use `String(36)` UUID strings, matching current project style.
Timestamps use timezone-aware `DateTime(timezone=True)`.

### `source_document`

| Field | Type | Null | Notes |
|---|---|---:|---|
| `id` | String(36) | no | PK. |
| `publisher_key` | String(128) | no | Stable publisher identifier. |
| `publisher_name` | String(256) | no | Display. |
| `issuer_key` | String(128) | yes | Company/regulator issuer key. |
| `issuer_name` | String(256) | yes | Display. |
| `source_type` | String(64) | no | Check against SourceType enum. |
| `external_document_id` | String(256) | yes | Exchange/provider/issuer ID. |
| `canonical_url` | Text | yes | Normalized URL. |
| `title` | Text | yes | Source-level title. |
| `document_language` | String(16) | yes | ISO-like code. |
| `created_at` | DateTime tz | no | Creation timestamp. |
| `created_by_actor` | String(32) | no | Actor enum. |

Constraints and indexes:

- PK `id`.
- Unique partial identity on `(publisher_key, source_type,
  external_document_id)` when external ID exists.
- Unique partial identity on `(publisher_key, source_type, canonical_url)` when
  external ID is absent and URL exists.
- Indexes on `issuer_key`, `source_type`, `canonical_url`.
- Delete policy: no physical delete.

### `source_document_version`

| Field | Type | Null | Notes |
|---|---|---:|---|
| `id` | String(36) | no | PK. |
| `source_document_id` | String(36) | no | FK restrict. |
| `version` | Integer | no | Starts at 1. |
| `version_reason` | String(64) | no | NEW_CONTENT, CORRECTION, REFETCH_CHANGED, GRADE_RECLASSIFICATION, METADATA_CORRECTION, RETRACTION_NOTICE. |
| `source_grade` | String(1) | no | Check S-F. |
| `version_fingerprint` | String(64) | no | sha256 hex over canonical source-version payload. |
| `published_at` | DateTime tz | yes | Source-stated time. |
| `observed_at` | DateTime tz | no | ThesisGuard observed time. |
| `fetched_at` | DateTime tz | no | Object store time. |
| `content_hash` | String(128) | no | sha256 hex. |
| `source_version_label` | String(128) | yes | Source-stated version/revision label. |
| `source_revision_id` | String(128) | yes | Provider revision ID when available. |
| `media_type` | String(128) | no | MIME. |
| `object_key` | Text | no | MinIO key. |
| `text_object_key` | Text | yes | Normalized text object. |
| `text_object_hash` | String(128) | yes | sha256 hex of normalized text object. |
| `parser_name` | String(128) | yes | Parser identity. |
| `parser_version` | String(64) | yes | Parser version. |
| `versioned_metadata` | JSON | no | Canonical metadata included in version_fingerprint. |
| `source_status` | String(32) | no | ACTIVE, RETRACTED, SUPERSEDED. |
| `source_status_changed_at` | DateTime tz | yes | Source lifecycle notice time. |
| `source_status_actor` | String(32) | yes | SYSTEM, USER, IMPORTER, ADMIN_SCRIPT. |
| `source_status_reason` | Text | yes | Required for RETRACTED or SUPERSEDED. |
| `created_at` | DateTime tz | no | Commit time. |

Constraints and indexes:

- Unique `(source_document_id, version)`.
- Unique `(source_document_id, version_fingerprint)`.
- Check `version >= 1`, SourceGrade, allowed version_reason, and allowed
  source_status.
- Check SourceType/SourceGrade pair through the section 11 matrix by service and
  database-compatible constraint where practical.
- Check source lifecycle metadata: `source_status='ACTIVE'` requires null
  status-change fields; `RETRACTED` or `SUPERSEDED` requires
  `source_status_changed_at`, `source_status_actor`, and
  `source_status_reason`.
- Indexes on `content_hash`, `version_fingerprint`, `source_grade`,
  `source_status`, `observed_at`, `published_at`.
- Immutable fields: all except no fields are mutable.

### `evidence_series`

| Field | Type | Null | Notes |
|---|---|---:|---|
| `id` | String(36) | no | PK. |
| `scope_type` | String(32) | no | INSTRUMENT, MARKET, SECTOR, POLICY, CROSS_INSTRUMENT. |
| `scope_key` | String(256) | no | Canonical scope identifier. |
| `information_type` | String(32) | no | Check fixed enum. |
| `claim_key` | String(256) | no | Service-generated stable key. |
| `metric_key` | String(128) | yes | Machine metric. |
| `period_start` | DateTime tz | yes | Claim period. |
| `period_end` | DateTime tz | yes | Claim period. |
| `provenance_kind` | String(32) | no | SOURCE_BACKED, MANUAL, DERIVED. |
| `primary_source_document_id` | String(36) | yes | FK restrict for SOURCE_BACKED only. |
| `origin_key` | String(256) | yes | Required for MANUAL and DERIVED source-less series. |
| `series_identity_hash` | String(64) | no | sha256 hex canonical lineage key. |
| `created_at` | DateTime tz | no | Creation timestamp. |
| `created_by_actor` | String(32) | no | Actor. |

Constraints and indexes:

- Unique `(series_identity_hash)`.
- Check allowed scope_type and provenance_kind.
- Check SOURCE_BACKED requires non-null `primary_source_document_id` and null
  `origin_key`.
- Check MANUAL and DERIVED require null `primary_source_document_id` and non-null
  `origin_key`.
- Check `scope_type='INSTRUMENT'` uses an instrument UUID in `scope_key`;
  `CROSS_INSTRUMENT` requires companion `evidence_instrument_link` rows when an
  EvidenceVersion is committed.
- Check or service invariant: any change to `scope_type`, `scope_key`,
  `information_type`, `claim_key`, `metric_key`, `period_start`, `period_end`,
  `provenance_kind`, `primary_source_document_id`, or `origin_key` creates a new
  row with a new `series_identity_hash`; it is not represented by a new
  EvidenceVersion inside the old row.
- Check `period_start <= period_end` when both present.
- Indexes on `scope_type`, `scope_key`, `primary_source_document_id`,
  `information_type`, `claim_key`, `metric_key`.
- Delete policy: no physical delete.

### `evidence_version`

| Field | Type | Null | Notes |
|---|---|---:|---|
| `id` | String(36) | no | PK. |
| `evidence_series_id` | String(36) | no | FK restrict. |
| `version` | Integer | no | Starts at 1. |
| `source_document_version_id` | String(36) | yes | Required except allowed manual USER_HYPOTHESIS or THESIS_INFERENCE from cited Evidence. |
| `information_type` | String(32) | no | Snapshot, matches series. |
| `provenance_kind` | String(32) | no | Snapshot, matches series. |
| `source_grade_snapshot` | String(1) | yes | S-F for SOURCE_BACKED; null for source-less. |
| `verification_status` | String(32) | no | Check VerificationStatus. |
| `status_changed_at` | DateTime tz | yes | Null only for brand-new initial version 1 UNREVIEWED with `supersedes_evidence_version_id` null and no lifecycle transition. |
| `status_changed_by_actor` | String(32) | yes | Null only when status_changed_at is null. |
| `status_change_kind` | String(32) | yes | INITIAL_VERIFICATION, REVIEW_REQUEST, REVIEW_DECISION, DISPUTE, INVALIDATION, RETRACTION, CORRECTION. |
| `status_reason` | Text | yes | Human/domain reason for status change. |
| `display_title` | Text | no | Display. |
| `display_text` | Text | no | Display. |
| `claim_key` | String(256) | no | Snapshot. |
| `metric_key` | String(128) | yes | Machine metric. |
| `raw_value` | Text | yes | Original value. |
| `raw_unit` | String(64) | yes | Original unit. |
| `normalized_value` | Numeric | yes | Decimal-compatible numeric. |
| `normalized_text_value` | Text | yes | Non-numeric normalized value. |
| `normalized_unit` | String(64) | yes | Canonical unit. |
| `currency` | String(16) | yes | Currency. |
| `period_start` | DateTime tz | yes | Claim period. |
| `period_end` | DateTime tz | yes | Claim period. |
| `as_of` | DateTime tz | no | Claim observation time. |
| `effective_from` | DateTime tz | yes | Validity. |
| `effective_to` | DateTime tz | yes | Validity. |
| `supersedes_evidence_version_id` | String(36) | yes | FK restrict. |
| `created_at` | DateTime tz | no | Commit time. |
| `created_by_actor` | String(32) | no | Actor. |
| `extractor_name` | String(128) | yes | Extractor identity. |
| `extractor_version` | String(64) | yes | Extractor version. |
| `prompt_template_version` | String(128) | yes | LLM proposal provenance. |
| `manual_entry_reason` | Text | yes | Required for user hypothesis without source. |
| `manual_observed_at` | DateTime tz | yes | Required for source-less manual provenance. |
| `trusted_correction_rule` | String(128) | yes | Required only for trusted deterministic correction to VERIFIED. |

Constraints and indexes:

- Unique `(evidence_series_id, version)`.
- Check `version >= 1`.
- Check fixed InformationType, nullable SourceGrade, VerificationStatus, and
  provenance_kind.
- Check `period_start <= period_end` when both present.
- Check `effective_from <= effective_to` when both present.
- Check source/provenance rule: SOURCE_BACKED requires non-null
  `source_document_version_id` and non-null `source_grade_snapshot`; MANUAL and
  DERIVED require null `source_document_version_id` and null
  `source_grade_snapshot`.
- Check FACT requires SOURCE_BACKED.
- Check external ESTIMATE requires SOURCE_BACKED; user-authored estimate may be
  MANUAL with `manual_entry_reason` and `manual_observed_at`.
- Check USER_HYPOTHESIS requires MANUAL, `created_by_actor='USER'`,
  `manual_entry_reason`, and `manual_observed_at`.
- Check THESIS_INFERENCE requires DERIVED and at least one
  `evidence_derivation_link` enforced by service in the same transaction.
- Check status metadata all-null/all-non-null: `status_changed_at`,
  `status_changed_by_actor`, `status_change_kind`, and `status_reason` are
  either all null or all non-null.
- Check the all-null case is allowed only when `version=1` and
  `verification_status='UNREVIEWED'` and `supersedes_evidence_version_id IS
  NULL`.
- Check `supersedes_evidence_version_id IS NOT NULL` requires non-null
  `status_changed_at`, `status_changed_by_actor`, `status_change_kind`, and
  `status_reason`, even when `version=1`.
- Check replacement EvidenceVersion v1 uses `status_change_kind='CORRECTION'`
  because it represents identity-changing correction lineage, not brand-new
  initial creation.
- Check `version > 1`, initial `VERIFIED`, request review, review decision,
  dispute, invalidation, retraction, ordinary correction, and trusted
  deterministic correction all require the four status audit fields.
- Check status_change_kind mapping: INITIAL_VERIFICATION only for initial
  trusted `VERIFIED`; REVIEW_REQUEST only for PENDING_REVIEW; REVIEW_DECISION
  for VERIFIED or REJECTED review outcomes; DISPUTE for DISPUTED or dispute
  resolution; INVALIDATION only for INVALIDATED; RETRACTION only for RETRACTED;
  CORRECTION for ordinary or trusted correction.
- Check ordinary correction target status is UNREVIEWED unless
  `trusted_correction_rule` is non-null and service validated the deterministic
  correction rule.
- Check tombstone completeness: RETRACTED and INVALIDATED rows must satisfy the
  same non-null snapshot and provenance constraints as any other EvidenceVersion
  row and must set `supersedes_evidence_version_id`.
- Indexes on `evidence_series_id`, `source_document_version_id`,
  `verification_status`, `source_grade_snapshot`, `provenance_kind`, `as_of`.
- Immutable fields: all.

### `evidence_source_locator`

| Field | Type | Null | Notes |
|---|---|---:|---|
| `id` | String(36) | no | PK. |
| `evidence_version_id` | String(36) | no | FK cascade only if parent creation rolls back; no domain delete. |
| `source_document_version_id` | String(36) | no | FK restrict. |
| `locator_type` | String(32) | no | Check locator enum. |
| `raw_locator` | Text | no | Original locator. |
| `short_citation` | String(256) | no | Display citation. |
| `locator_payload` | JSON | no | Structured locator. |
| `quote_hash` | String(128) | yes | Hash of bounded quote. |
| `created_at` | DateTime tz | no | Commit time. |

Constraints:

- Unique `(evidence_version_id, source_document_version_id, locator_type,
  raw_locator)`.
- Check locator_type enum.
- Domain validation confirms the source version equals EvidenceVersion
  `source_document_version_id` and belongs to the EvidenceSeries
  `primary_source_document_id`.

### `evidence_instrument_link`

| Field | Type | Null | Notes |
|---|---|---:|---|
| `id` | String(36) | no | PK. |
| `evidence_version_id` | String(36) | no | FK restrict to exact EvidenceVersion snapshot. |
| `instrument_id` | String(36) | no | FK restrict to instrument. |
| `role` | String(32) | no | PRIMARY_SCOPE, RELATED_COMPANY, SECTOR_MEMBER, PEER, POLICY_TARGET. |
| `link_order` | Integer | yes | Optional display order; not part of series identity. |
| `link_metadata` | JSON | yes | Bounded metadata; not part of series identity. |
| `created_at` | DateTime tz | no | Commit time. |

Constraints:

- Unique `(evidence_version_id, instrument_id, role)`.
- Indexes on `instrument_id`, `evidence_version_id`, and `role`.
- Required for `scope_type='CROSS_INSTRUMENT'` and optional for sector/policy
  fan-out. Single-instrument Evidence uses `scope_type='INSTRUMENT'` and may add
  one PRIMARY_SCOPE link for query speed, but identity remains in `scope_key`.
- Immutable/delete policy: no physical delete. Replacing instrument membership
  changes the sorted instrument ID set, therefore changes `scope_key` and creates
  a new EvidenceSeries. Changes only to role, link_order, or link_metadata for
  the same instrument ID set may append a new EvidenceVersion in the same series
  with new immutable link rows.

### `evidence_corroboration_link`

| Field | Type | Null | Notes |
|---|---|---:|---|
| `id` | String(36) | no | PK. |
| `left_evidence_version_id` | String(36) | no | FK restrict to lower ordered ID. |
| `right_evidence_version_id` | String(36) | no | FK restrict to higher ordered ID. |
| `relation_type` | String(32) | no | CORROBORATES, CONFLICTS_WITH, PARTIALLY_SUPPORTS. |
| `created_at` | DateTime tz | no | Commit time. |
| `created_by_actor` | String(32) | no | Actor. |

Constraints:

- Canonical pair ordering: `left_evidence_version_id` is lexicographically less
  than `right_evidence_version_id` for symmetric relation types.
- Check no self-link.
- Unique `(left_evidence_version_id, right_evidence_version_id, relation_type)`.
- Index both EvidenceVersion FKs.
- Immutable/delete policy: no physical delete; disputed corroboration is another
  audit event or a new relation row with a different relation_type.

### `evidence_derivation_link`

| Field | Type | Null | Notes |
|---|---|---:|---|
| `id` | String(36) | no | PK. |
| `derived_evidence_version_id` | String(36) | no | FK restrict to THESIS_INFERENCE or source-less estimate when applicable. |
| `supporting_evidence_version_id` | String(36) | no | FK restrict to exact support EvidenceVersion. |
| `role` | String(32) | no | SUPPORTS_INFERENCE, INPUT_FACT, INPUT_ESTIMATE, MANUAL_CONTEXT. |
| `support_order` | Integer | yes | Optional display order. |
| `support_weight` | Numeric | yes | Optional deterministic weight, not truth. |
| `created_at` | DateTime tz | no | Commit time. |

Constraints:

- Check no self-link.
- Service rejects cycles by traversing existing derivation links in the same
  transaction before commit.
- Unique `(derived_evidence_version_id, supporting_evidence_version_id, role)`.
- Index both EvidenceVersion FKs.
- Immutable/delete policy: no physical delete. A changed supporting
  EvidenceVersion ID set changes `origin_key` and creates a new EvidenceSeries.
  Changes only to role, support_order, support_weight, or derived expression for
  the same supporting ID set may append a new EvidenceVersion in the same series
  with new immutable derivation rows.

### `evidence_idempotency_record`

| Field | Type | Null | Notes |
|---|---|---:|---|
| `scope` | String(128) | no | Operation scope. |
| `idempotency_key` | String(128) | no | Client key. |
| `request_hash` | String(128) | no | Server hash. |
| `status` | String(32) | no | COMMITTED or UNKNOWN_OUTCOME. |
| `response_ref_type` | String(64) | no | SourceDocumentVersion, EvidenceVersion, link. |
| `response_ref_id` | String(36) | yes | Result ID. |
| `created_at` | DateTime tz | no | Commit time. |

Constraints:

- Primary key `(scope, idempotency_key)`.
- Index on `request_hash`.

### `evidence_audit_event`

| Field | Type | Null | Notes |
|---|---|---:|---|
| `id` | String(36) | no | PK. |
| `aggregate_type` | String(64) | no | SourceDocument, EvidenceSeries, EvidenceVersion. |
| `aggregate_id` | String(36) | no | Aggregate ID. |
| `event_type` | String(64) | no | Created, DisputeNoteAdded, RetractionImported, etc. |
| `payload` | JSON | no | Audit payload. |
| `occurred_at` | DateTime tz | no | Timestamp. |
| `actor` | String(32) | no | Actor. |

Delete policy: no physical delete.

### `research_module_evidence_link`

Planned for WP04-04, not WP04-01 if WP04-01 is limited to Evidence persistence
foundation. The table is still specified here so the Research snapshot contract
is not re-decided later.

| Field | Type | Null | Notes |
|---|---|---:|---|
| `id` | String(36) | no | PK. |
| `research_module_id` | String(36) | no | FK to research_module. |
| `research_package_id` | String(36) | no | FK to research_package. |
| `research_package_version` | Integer | no | Snapshot version copied from ResearchPackage. |
| `evidence_version_id` | String(36) | no | FK to evidence_version. |
| `link_role` | String(32) | no | SUPPORTING, CONTRADICTING, SOURCE_ONLY, UNKNOWN. |
| `created_by_refresh_id` | String(36) | no | ID of ResearchPackage N+1 creation workflow. |
| `created_at` | DateTime tz | no | Commit time. |

Constraints and indexes:

- Unique `(research_module_id, evidence_version_id, link_role)`.
- Indexes on `research_package_id`, `research_module_id`,
  `evidence_version_id`, and `(research_package_id, research_package_version)`.
- Check `research_package_version >= 1`.
- Insert policy: rows are created only while creating a new immutable
  ResearchPackage/ResearchModule snapshot. There is no standalone post-hoc
  insert command for an existing module.
- Update/delete policy: no domain UPDATE or DELETE. If references change,
  create ResearchPackage N+1 and new module/link child rows.

## 22. Domain Command and Query Blueprint

Commands:

| Command | Input | Output | Preconditions | Transaction and concurrency | Errors |
|---|---|---|---|---|---|
| register_source_document | source identity, source_type, publisher, issuer | SourceDocument | identity valid | upsert by identity key | duplicate identity conflict only when payload differs |
| append_source_document_version | source_document_id, expected_version, content_hash, version_fingerprint, object key, versioned metadata, idempotency key | SourceDocumentVersion | source exists, expected_version matches unless creating version 1 | lock SourceDocument; unique `(source_document_id, version_fingerprint)` | not found, version conflict, duplicate source version |
| create_evidence_series_version | scope_type, scope_key, information_type, claim fields, provenance_kind, source version or manual/derivation provenance, locator, idempotency key | EvidenceVersion | scope/provenance/source/locator valid | create series by `series_identity_hash`; unique hash guards duplicate series | invalid locator, invalid grade/type, duplicate candidate |
| create_replacement_evidence_series | prior_evidence_version_id, new identity dimensions, payload, status_changed_at, status_changed_by_actor, status_change_kind, status_reason, trusted_correction_rule, idempotency key | new EvidenceSeries version 1 and replacement EvidenceVersion version 1 | at least one identity dimension changed; prior exact EvidenceVersion exists; status_change_kind is CORRECTION; status_reason is non-null | create new series by new `series_identity_hash`; set `supersedes_evidence_version_id` to prior exact version; ordinary replacement v1 is UNREVIEWED; trusted deterministic replacement v1 may be VERIFIED only with valid trusted_correction_rule; old row and old series are not mutated | duplicate identity, invalid replacement, missing audit tuple, partial audit tuple, invalid trusted correction |
| revise_correct_evidence | evidence_series_id, expected_version, corrected fields, source version or cited Evidence, status audit fields | EvidenceVersion | expected_version matches and identity dimensions unchanged | append N+1 with status_change_kind CORRECTION; if identity changes route to create_replacement_evidence_series | version conflict, invalid state, identity change required |
| mark_disputed | evidence_series_id, expected_version, reason, status audit fields | EvidenceVersion | current status allows dispute | append N+1 with status_change_kind DISPUTE | invalid state transition |
| verify_or_reject | evidence_series_id, expected_version, decision, reviewer metadata, status audit fields | EvidenceVersion | current status reviewable | append N+1 with status_change_kind REVIEW_DECISION | invalid state transition |
| request_review | evidence_series_id, expected_version, reason, status audit fields | EvidenceVersion | current status UNREVIEWED | append N+1 with status_change_kind REVIEW_REQUEST | invalid state transition |
| retract_or_invalidate | evidence_series_id, expected_version, reason, source notice, status audit fields | EvidenceVersion | exact current version known | append complete N+1 tombstone/status snapshot, copy mandatory child rows, set RETRACTION or INVALIDATION kind | invalid state transition |
| create_research_package_version_with_evidence_links | instrument_id, expected_research_version, refresh payload, module snapshots, exact EvidenceVersion link set, idempotency key | ResearchPackage N+1 with module/link child rows | exact EvidenceVersion IDs exist; expected ResearchPackage version matches | lock current instrument ResearchPackage; create package/module/link rows atomically | research version conflict, retracted evidence reference |
| idempotent_replay | scope, key, request hash | prior response reference | record exists | read idempotency table | idempotency conflict |

`create_replacement_evidence_series` invariants:

- Input fields are exactly: `prior_evidence_version_id`, the new identity
  dimensions, corrected payload fields, `status_changed_at`,
  `status_changed_by_actor`, `status_change_kind`, `status_reason`, optional
  `trusted_correction_rule`, and idempotency key.
- `status_change_kind` must be `CORRECTION`; `status_changed_at`,
  `status_changed_by_actor`, and `status_reason` must be non-null. Partial
  lifecycle audit tuples are rejected.
- Ordinary identity-changing replacement creates replacement EvidenceVersion v1
  with `verification_status='UNREVIEWED'`.
- Trusted deterministic identity-changing replacement may create replacement
  EvidenceVersion v1 with `verification_status='VERIFIED'` only when
  `trusted_correction_rule` is non-null and validated.
- The transaction inserts a new EvidenceSeries identified by the new
  `series_identity_hash`, inserts replacement EvidenceVersion v1 with non-null
  `supersedes_evidence_version_id=prior_evidence_version_id`, writes required
  child rows for the new version, and records idempotency.
- The prior EvidenceVersion row, prior EvidenceSeries row, and prior child rows
  remain immutable. The command never appends S1/N+1 to express an
  identity-changing correction.

Queries:

| Query | Reads current or exact | Output |
|---|---|---|
| get_current_evidence | current derived | Highest EvidenceVersion for a series with lineage metadata. |
| get_current_valid_evidence | latest-first eligibility | Reads highest EvidenceVersion and returns eligible or currently unavailable; it does not fall back. |
| get_exact_evidence_version | exact | One immutable EvidenceVersion with locators and source version. |
| list_evidence_history | history | All versions for one EvidenceSeries in ascending version order. |
| list_evidence_by_instrument | current or exact filter | EvidenceSeries and current versions for one instrument. |
| list_evidence_by_source_document_version | exact source version | EvidenceVersions extracted from a SourceDocumentVersion. |
| resolve_research_source_references | compatibility | Maps WP03 legacy strings and typed links when available. |
| detect_references_to_retracted_or_disputed_versions | exact references | Research/Thesis references whose EvidenceVersion status changed in newer series version. |

Authorization boundary for V1:

- Single-user local system.
- No `user_id` or tenant is added to core Evidence tables in V1.
- `created_by_actor` records provenance, not authorization.

## 23. Error Contract Blueprint

Stable error envelope:

```json
{
  "detail": {
    "code": "EVIDENCE_STABLE_CODE",
    "message": "Human-readable message",
    "expected_version": 1,
    "current_version": 2
  }
}
```

| Code | HTTP suggestion | Meaning | Retryability | Required detail fields |
|---|---:|---|---|---|
| `EVIDENCE_SOURCE_DOCUMENT_NOT_FOUND` | 404 | SourceDocument missing. | Retry after correcting ID. | source_document_id |
| `EVIDENCE_SOURCE_VERSION_NOT_FOUND` | 404 | SourceDocumentVersion missing. | Retry after correcting ID. | source_document_version_id |
| `EVIDENCE_VERSION_NOT_FOUND` | 404 | EvidenceVersion missing. | Retry after correcting ID. | evidence_version_id |
| `EVIDENCE_VERSION_CONFLICT` | 409 | expected_version stale. | Retry after reread. | expected_version, current_version |
| `RESEARCH_VERSION_CONFLICT` | 409 | expected_research_version stale while creating ResearchPackage N+1 with typed links. | Retry after reread. | expected_research_version, current_research_version |
| `EVIDENCE_IDEMPOTENCY_CONFLICT` | 409 | Same key different request hash. | Not with same key. | scope, idempotency_key |
| `EVIDENCE_DUPLICATE_SOURCE_VERSION` | 409 | Same source version content already exists. | Replay or use existing. | source_document_id, existing_version_id |
| `EVIDENCE_INVALID_STATE_TRANSITION` | 409 | Status command not legal. | Retry only with legal command. | from_status, requested_status |
| `EVIDENCE_INVALID_SOURCE_LOCATOR` | 422 | Locator missing, points at wrong source version, or invalid coordinates. | Retry after correcting payload. | source_document_version_id, locator_path |
| `EVIDENCE_INVALID_SOURCE_GRADE` | 422 | Grade is unknown or incompatible with source type. | Retry after correcting payload. | source_grade, source_type |
| `EVIDENCE_INVALID_SOURCE_TYPE` | 422 | SourceType outside enum. | Retry after correcting payload. | source_type |
| `EVIDENCE_INVALID_PROVENANCE` | 422 | Source-backed/manual/derived provenance rule failed. | Retry after correcting payload. | provenance_kind, validation_path |
| `EVIDENCE_INVALID_CORROBORATION_LINK` | 422 | Corroboration self-link, duplicate, or bad relation. | Retry after correcting payload. | left_evidence_version_id, right_evidence_version_id |
| `EVIDENCE_INVALID_DERIVATION_LINK` | 422 | Derivation self-link, cycle, or missing support. | Retry after correcting payload. | derived_evidence_version_id, supporting_evidence_version_id |
| `RESEARCH_HISTORICAL_MODULE_LINK_FORBIDDEN` | 409 | Command tried to add/remove typed Evidence link on existing historical ResearchModule. | Create ResearchPackage N+1 instead. | research_module_id, research_package_id |
| `EVIDENCE_F_GRADE_CORE_THESIS_REJECTED` | 409 | Future Thesis service tried to use F-grade Evidence as core support. | Not without higher-grade support. | evidence_version_id, source_grade |
| `EVIDENCE_RETRACTED_REFERENCE` | 409 | Command tried to use retracted or invalid Evidence. | Retry with another version. | evidence_version_id, verification_status |
| `EVIDENCE_VALIDATION_ERROR` | 422 | Schema/domain validation error. | Retry after correcting payload. | validation_path |
| `EVIDENCE_PERSISTENCE_CONFLICT` | 409 | Database unique/check constraint conflict. | Retry after reread when safe. | constraint_kind |

## 24. Given/When/Then Examples

### Example 1 - Idempotent Replay

Given the same create Evidence request, same idempotency key, and same canonical
request hash.

When the request is submitted again.

Then the service returns the first committed EvidenceVersion reference, creates
no SourceDocumentVersion, creates no EvidenceVersion, and emits no duplicate
domain fact.

### Example 2 - Idempotency Key Reuse Conflict

Given an idempotency key already bound to one request hash.

When a new payload reuses that key with a different request hash.

Then the service returns `EVIDENCE_IDEMPOTENCY_CONFLICT`, creates no new version,
does not overwrite the existing idempotency record, and the caller must use a
new key after rereading state.

### Example 3 - Concurrent Revision

Given current EvidenceSeries version N and two commands both declare
`expected_version=N`.

When both commands try to create the next version concurrently.

Then at most one command creates N+1, the other returns
`EVIDENCE_VERSION_CONFLICT` with expected/current versions, no second N+1 exists,
and version N is not overwritten.

### Example 4 - Same Fact from Two Sources

Given two SourceDocument lineages express the same company revenue number.

When both are extracted.

Then two source-backed EvidenceSeries rows exist because
`primary_source_document_id` differs, optional `evidence_corroboration_link`
records may connect the exact EvidenceVersions, no text or vector similarity
auto-merges them, and Research/Thesis can cite either exact EvidenceVersion
separately.

### Example 5 - Corrected Source

Given Research cites EvidenceVersion V1 extracted from SourceDocumentVersion S1.

When the issuer publishes corrected source content and the system imports it.

Then SourceDocumentVersion S2 is appended with a new version_fingerprint,
EvidenceVersion V2 is appended in the same EvidenceSeries, V1 continues to
resolve, the Research reference remains V1, and query layers can show that V2 is
newer.

### Example 6 - Retraction

Given an EvidenceVersion has been cited.

When its source is retracted or a domain command retracts it.

Then no history is physically deleted, exact old references resolve, current
read returns the latest tombstone/current status, current valid does not fall
back to the old version, future core Thesis support cannot treat that latest
version as eligible, and audit metadata records who, when, and why.

### Example 7 - F-Grade Core Thesis Restriction

Given SourceGrade `F` on an EvidenceVersion.

When the future Thesis service tries to set it as core thesis support.

Then the command returns `EVIDENCE_F_GRADE_CORE_THESIS_REJECTED`, Thesis remains
unchanged, the Evidence remains available in the unverified intelligence pool,
and WP04 does not implement Thesis service behavior.

### Example 8 - Locator Integrity

Given an EvidenceVersion claims support from SourceDocumentVersion A but its
locator points to SourceDocumentVersion B or an invalid page/table coordinate.

When the create command is validated.

Then the service rejects the command with `EVIDENCE_INVALID_SOURCE_LOCATOR` and
does not commit the EvidenceVersion.

### Example 9 - Research Reference Migration

Given current WP03 uses `source_refs: list[str]`.

When a later integration task migrates Research to precise Evidence references.

Then the new representation stores exact EvidenceVersion IDs, old strings are
treated only as legacy notes, compatibility boundaries are explicit, and this
task has not modified WP03 code or OpenAPI.

### Example 10 - Unchanged Re-Observation

Given SourceDocumentVersion S1 has content_hash H and version_fingerprint F1.

When the same bytes and same versioned metadata are observed later with a new
`observed_at`.

Then no new SourceDocumentVersion is created, S1 is returned or referenced, and
the repeated observation is represented only by idempotency/audit or collection
metadata.

### Example 11 - Grade Reclassification

Given SourceDocumentVersion S1 has content_hash H and SourceGrade C.

When the domain reclassifies the same bytes to SourceGrade D.

Then content_hash remains H, MinIO object key may be reused, version_fingerprint
changes, and SourceDocumentVersion S2 is appended with
`version_reason='GRADE_RECLASSIFICATION'`.

### Example 12 - Versioned Metadata Correction

Given SourceDocumentVersion S1 has content_hash H and published_at P1.

When the source-stated publication time or other versioned metadata is corrected
to P2 without changing bytes.

Then content_hash remains H, version_fingerprint changes, and S2 is appended
with `version_reason='METADATA_CORRECTION'`.

### Example 13 - Concurrent Duplicate Source Import

Given two workers compute the same `(source_document_id, version_fingerprint)`.

When both attempt to commit a SourceDocumentVersion concurrently.

Then the unique constraint permits at most one row; the loser rereads the
existing row and returns or reconciles with that ID instead of creating a
duplicate.

### Example 14 - MinIO Write Succeeds and DB Commit Fails

Given canonical bytes have been written to MinIO and PostgreSQL commit fails
before SourceDocumentVersion is committed.

When the same import is retried.

Then retry uses content_hash and version_fingerprint to discover and reuse or
mark the orphan object, and no committed Evidence or source version exists until
PostgreSQL commits.

### Example 15 - Market-Wide and Cross-Instrument Identity

Given one market-wide policy claim and one claim that applies to instruments A
and B.

When both are committed.

Then the market-wide series uses `scope_type='MARKET'` and `scope_key='MARKET'`,
the cross-instrument series uses `scope_type='CROSS_INSTRUMENT'` and sorted
instrument-hash `scope_key`, and exact EvidenceVersion child rows in
`evidence_instrument_link` provide instrument query fan-out.

### Example 16 - Nullable Metric and Period Dimensions

Given two otherwise identical claims have null metric_key and null period.

When the service computes `series_identity_hash`.

Then explicit JSON null values are included in the hash, PostgreSQL nullable
UNIQUE semantics are not relied upon, and duplicate identity cannot bypass the
unique `series_identity_hash`.

### Example 17 - Source-Less FACT Rejected

Given a payload declares `information_type='FACT'` with manual provenance and no
SourceDocumentVersion.

When the create command is validated.

Then it returns `EVIDENCE_INVALID_PROVENANCE`, creates no EvidenceVersion, and
does not create a fake SourceDocumentVersion.

### Example 18 - User-Authored Estimate

Given a user creates an estimate with `created_by_actor='USER'`,
`manual_entry_reason`, and `manual_observed_at`.

When the estimate is committed as manual provenance.

Then EvidenceVersion has null `source_document_version_id`, null
`source_grade_snapshot`, no SourceLocator row, and manual provenance fields
explain the origin.

### Example 19 - Derived Thesis Inference Requires Support

Given a `THESIS_INFERENCE` payload has zero supporting EvidenceVersion IDs.

When the create command is validated.

Then it returns `EVIDENCE_INVALID_DERIVATION_LINK` or
`EVIDENCE_INVALID_PROVENANCE` and commits nothing.

### Example 20 - Valid Derived Thesis Inference

Given a `THESIS_INFERENCE` payload cites exact supporting EvidenceVersion IDs.

When the create command commits.

Then the derived EvidenceVersion has provenance_kind DERIVED, null
source_document_version_id, null source_grade_snapshot, no SourceLocator row,
and immutable `evidence_derivation_link` rows to each support.

### Example 21 - Corroboration Self-Link Rejected

Given an EvidenceVersion ID is submitted as both sides of a corroboration link.

When the link command validates.

Then it returns `EVIDENCE_INVALID_CORROBORATION_LINK` and creates no link.

### Example 22 - Derivation Self-Link or Cycle Rejected

Given a derived EvidenceVersion would directly or indirectly support itself.

When the derivation links are validated in the commit transaction.

Then the service rejects the write with `EVIDENCE_INVALID_DERIVATION_LINK`.

### Example 23 - Latest DISPUTED Is Not Currently Eligible

Given EvidenceSeries version 1 is VERIFIED and version 2 is DISPUTED.

When current valid is queried for a role requiring eligible Evidence.

Then the query reads version 2, reports currently unavailable for that role, and
does not fall back to version 1.

### Example 24 - Latest INVALIDATED or RETRACTED Is Not Currently Eligible

Given EvidenceSeries version 1 is VERIFIED and version 2 is INVALIDATED or
RETRACTED.

When current valid is queried.

Then the query reads version 2 and reports currently unavailable; exact read of
version 1 still returns the historical old row.

### Example 25 - Correction of Prior Eligible Evidence

Given an EvidenceSeries current version is VERIFIED.

When ordinary correction changes content, normalized value, or locator.

Then a new EvidenceVersion is appended with status UNREVIEWED, prior exact
references remain pointed at the old version, and eligibility waits for review.

### Example 26 - Trusted Deterministic Correction

Given a named deterministic trusted correction rule can fully validate source,
locator, semantic value, status metadata, and audit in one transaction.

When that command corrects an eligible EvidenceVersion.

Then it may append a new VERIFIED EvidenceVersion with
`trusted_correction_rule` recorded; this is the only direct eligible correction
path.

### Example 27 - Source Retraction Notice

Given an issuer retracts a source document version.

When the retraction notice is imported.

Then a new SourceDocumentVersion is appended with source_status RETRACTED,
source_status_changed_at, source_status_actor, and source_status_reason; any
affected Evidence lifecycle change is a separate EvidenceVersion append.

### Example 28 - Illegal SourceType and SourceGrade Pair

Given source_type is `FINANCIAL_REPORT` and source_grade is `F`.

When SourceDocumentVersion is validated.

Then the pair is rejected by the section 11 matrix with
`EVIDENCE_INVALID_SOURCE_GRADE`.

### Example 29 - Add Typed Evidence Reference to Current ResearchPackage

Given instrument I has current ResearchPackage version N and a desired typed
Evidence link set.

When WP04-04 creates ResearchPackage N+1 with
`expected_research_version=N`.

Then new ResearchModule snapshot rows and their `research_module_evidence_link`
children are created atomically; ResearchPackage N and its modules are not
modified.

### Example 30 - Concurrent Research Reference Refresh

Given two refresh commands both target instrument I with
`expected_research_version=N`.

When both attempt to create typed Evidence links in ResearchPackage N+1.

Then at most one ResearchPackage N+1 commits; the other receives
`RESEARCH_VERSION_CONFLICT` and must reread.

### Example 31 - Copy Unchanged Research Module Links

Given ResearchPackage N has a module snapshot with typed Evidence links.

When ResearchPackage N+1 copies the unchanged module by copy-on-write.

Then new link child rows are created for the copied module snapshot and point at
the same exact EvidenceVersion IDs.

### Example 32 - Cited Evidence Corrected After Research Snapshot

Given ResearchPackage N cites EvidenceVersion V1.

When Evidence correction creates V2.

Then ResearchPackage N still cites V1; current Research views may show V2 as a
newer option but must not mutate the old link.

### Example 33 - Cited Evidence Retracted After Research Snapshot

Given ResearchPackage N cites EvidenceVersion V1.

When V1's series later appends a RETRACTED latest version.

Then the old Research link still points to V1, exact audit replay works, and
current UI/API views may display a retraction warning without changing N.

### Example 34 - Historical ResearchModule Link Insert Rejected

Given a ResearchModule already belongs to committed ResearchPackage N.

When a command tries to insert or delete a `research_module_evidence_link` row
for that historical module outside ResearchPackage N+1 creation.

Then the command is rejected with `RESEARCH_HISTORICAL_MODULE_LINK_FORBIDDEN`.

### Example 35 - Cross-Instrument Membership Change

Given EvidenceSeries S1 has `scope_type='CROSS_INSTRUMENT'` and `scope_key`
computed from sorted instrument IDs A+B.

When the applicable instrument member set changes to A+C.

Then `scope_key` changes, `series_identity_hash` changes, the service creates a
new EvidenceSeries S2 starting at version 1, S2's first EvidenceVersion points
to the prior exact EvidenceVersion through non-null
`supersedes_evidence_version_id`, records non-null CORRECTION status audit
fields, and the command must not append a member-changed EvidenceVersion to S1.

### Example 36 - Cross-Instrument Link Metadata Change

Given EvidenceSeries S1 has the same sorted instrument ID set A+B.

When only `evidence_instrument_link.role`, `link_order`, or `link_metadata`
changes and no EvidenceSeries identity dimension changes.

Then the service may append EvidenceVersion N+1 in S1 and create new immutable
`evidence_instrument_link` child rows for N+1; prior link rows remain unchanged.

### Example 37 - Derived Support Set Change

Given a DERIVED EvidenceSeries origin_key was computed from supporting IDs
V1+V2.

When the support set changes to V1+V3.

Then `origin_key` changes, `series_identity_hash` changes, the service creates a
new DERIVED EvidenceSeries starting at version 1, links it to the replaced exact
EvidenceVersion through non-null `supersedes_evidence_version_id`, records
non-null CORRECTION status audit fields, and must not append this changed
support set inside the old series.

### Example 38 - Derived Link Metadata-Only Change

Given a DERIVED EvidenceSeries keeps the same supporting EvidenceVersion ID set
V1+V2.

When only derivation `role`, `support_order`, `support_weight`, or derived
expression changes.

Then the identity dimensions remain unchanged, the service may append
EvidenceVersion N+1 in the same EvidenceSeries, and N+1 receives new immutable
`evidence_derivation_link` child rows.

### Example 39 - Identity Field Correction

Given `metric_key`, `period_start`, and `period_end` are part of
`series_identity_hash`.

When a correction changes any of those fields.

Then the service creates a new EvidenceSeries starting at version 1 and links it
to the replaced exact EvidenceVersion through non-null
`supersedes_evidence_version_id`; because this is replacement v1, it records
non-null CORRECTION status audit fields and must not append the identity-changed
payload inside the original series.

### Example 40 - Ordinary Correction Audit

Given current EvidenceVersion N has status VERIFIED.

When ordinary correction changes content, normalized value, display text,
locator, or grade snapshot without changing any identity dimension.

Then the service appends EvidenceVersion N+1 with status UNREVIEWED,
`status_change_kind='CORRECTION'`, non-null `status_changed_at`,
`status_changed_by_actor`, and `status_reason`, and old version N remains
unchanged.

### Example 41 - Retraction Tombstone Complete Snapshot

Given a source-backed VERIFIED EvidenceVersion has non-null required snapshot
fields, a valid SourceDocumentVersion, source grade snapshot, and SourceLocator
child rows.

When `retract_evidence` runs.

Then the service appends a complete RETRACTED EvidenceVersion N+1 that copies
all required snapshot/provenance/source/display/value/time fields, sets
`status_change_kind='RETRACTION'`, non-null status audit fields,
`supersedes_evidence_version_id`, and created_at, creates copied immutable
SourceLocator child rows for N+1, and leaves the old EvidenceVersion and old
child rows unchanged. Current valid reads N+1 first and does not fall back to
the old version.

### Example 42 - Ordinary Identity-Changing Replacement v1 Audit

Given EvidenceSeries S1 current EvidenceVersion V3 has
`verification_status=VERIFIED`, `metric_key='revenue_growth_yoy'`, and immutable
child rows already committed.

When an ordinary correction changes the identity dimension `metric_key` to
`revenue_growth_qoq`.

Then the service creates new EvidenceSeries S2 and replacement EvidenceVersion
S2/v1. It does not create S1/V4 and does not mutate S1/V3 or S1's historical
child rows.

Then S2/v1 has `verification_status=UNREVIEWED`,
`supersedes_evidence_version_id=V3`, non-null `status_changed_at`, non-null
`status_changed_by_actor`, `status_change_kind='CORRECTION'`, and non-null
`status_reason`.

Then a null lifecycle audit tuple or partial lifecycle audit tuple for S2/v1 is
rejected, even though S2/v1 has `version=1`.

## 25. Decision Records and Rejected Alternatives

### D-01 Evidence Unit

Selected Decision: one EvidenceVersion represents one atomic claim, estimate,
inference, or hypothesis. Tables and multi-fact documents are split into one
EvidenceSeries per machine-meaningful claim. Raw quote, raw value, normalized
value, unit, period, locator, and display text are separate fields.

Invariant: one EvidenceVersion has one claim key and one primary normalized
meaning.

Alternatives Considered: one Evidence row per document; one Evidence row per
Research module; unstructured JSON only.

Rejected Alternatives: document-level Evidence hides atomic citation and makes
Thesis support ambiguous; module-level Evidence repeats WP03; free JSON cannot
enforce locators or units.

Rationale: Thesis validation must cite exact facts and estimates.

Downstream Impact: WP04-01 implements atomic tables; parser outputs may fan out.

Validation or Constraint: non-empty display_text, claim_key, InformationType,
provenance, and locator/provenance rule.

Example: one income statement table yields separate EvidenceVersions for
revenue, gross margin, and net profit.

### D-02 Stable Identity and Immutable Version

Selected Decision: SourceDocument and EvidenceSeries are stable logical rows;
SourceDocumentVersion and EvidenceVersion are immutable append-only rows.
Versions start at 1 and increase by one per aggregate. Current is derived by
highest version.

Invariant: no UPDATE to historical content fields and no DELETE of history.
EvidenceVersion appends cannot change EvidenceSeries identity dimensions; an
identity-dimension change creates a new EvidenceSeries starting at version 1.
That replacement version 1 is not brand-new initial evidence: it must set
`supersedes_evidence_version_id` and non-null CORRECTION status audit fields.

Alternatives Considered: single mutable Evidence table; mutable current pointer.

Rejected Alternatives: mutable table breaks audit; current pointer adds a second
truth for latest.

Rationale: Research and Thesis references must replay exact historical evidence.

Downstream Impact: WP04 services append rows and use expected_version for
existing aggregates; identity-changing corrections use a new EvidenceSeries and
`supersedes_evidence_version_id` link to the prior exact EvidenceVersion.

Validation or Constraint: unique `(aggregate_id, version)` and check
`version >= 1`; SourceDocumentVersion additionally uses unique
`(source_document_id, version_fingerprint)` and EvidenceSeries uses unique
`series_identity_hash`.

Example: normalized value correction appends version 2 while version 1 remains
readable; metric_key correction creates a new EvidenceSeries because identity
changed, and its replacement EvidenceVersion v1 carries
`status_change_kind='CORRECTION'` plus the full status audit tuple.

### D-03 Information Type

Selected Decision: fixed enum `FACT`, `ESTIMATE`, `THESIS_INFERENCE`,
`USER_HYPOTHESIS`. Type is immutable inside one EvidenceSeries.

Invariant: user belief never becomes fact by label change.

Alternatives Considered: free string; changing type inside series.

Rejected Alternatives: free string pollutes downstream scoring; type mutation
breaks audit.

Rationale: PRD and task contract require four exact values.

Downstream Impact: Thesis service can enforce support rules by type.

Validation or Constraint: database check and Pydantic enum.

Example: a user's "sales will double" is USER_HYPOTHESIS until supported by
Source-backed FACT or ESTIMATE Evidence.

### D-04 Source Grade

Selected Decision: store SourceGrade on SourceDocumentVersion and snapshot it on
source-backed EvidenceVersion. Source-less EvidenceVersion stores null
`source_grade_snapshot`. F-grade cannot support core Thesis.

Invariant: historical reads see the grade known at commit time.

Alternatives Considered: grade only on EvidenceVersion; grade only on source.

Rejected Alternatives: Evidence-only loses source lineage; source-only loses
audit snapshot after reclassification.

Rationale: grade can change as metadata interpretation changes.

Downstream Impact: WP04 and WP05 enforce grade at link boundaries.

Validation or Constraint: check S-F and the complete SourceType/SourceGrade
matrix in section 11.

Example: social media rumor is F and remains in intelligence pool.

### D-05 Source Type Policy

Selected Decision: closed enum and complete SourceType/SourceGrade allowed-pair
matrix listed in section 11.

Invariant: unknown source type is rejected.

Alternatives Considered: open string with naming rules.

Rejected Alternatives: open string would create incompatible values before
client/schema generation exists.

Rationale: V1 has a small known source universe.

Downstream Impact: adding a source type is a schema change.

Validation or Constraint: check constraint, public enum, and allowed-pair matrix.

Example: a broker PDF uses `BROKER_RESEARCH`.

### D-06 Verification Status

Selected Decision: fixed VerificationStatus state machine in section 12. Status
changes append EvidenceVersion rows with unified status metadata fields.

Invariant: reliability state is historically replayable, and current valid reads
the latest version first with no fallback to older eligible rows.
Only brand-new initial version 1 UNREVIEWED creation with
`supersedes_evidence_version_id` null may omit status audit fields.

Alternatives Considered: mutable status column; separate lifecycle enum.

Rejected Alternatives: mutable status rewrites history; separate lifecycle adds
ambiguous combinations in V1.

Rationale: exact EvidenceVersion reads must show what was known then.

Downstream Impact: review/retraction commands append versions.

Validation or Constraint: transition table enforced by service; status-changing
rows record `status_changed_at`, `status_changed_by_actor`,
`status_change_kind`, and `status_reason`; the four fields are all-null only for
brand-new no-predecessor version 1 UNREVIEWED and otherwise all-non-null. Any
row with non-null `supersedes_evidence_version_id` requires the four fields even
when `version=1`.

Example: VERIFIED version can append DISPUTED version without changing the old
row; ordinary correction to UNREVIEWED still records CORRECTION audit metadata.

### D-07 Correction, Dispute, Invalidation and Retraction

Selected Decision: correction, invalidation, and retraction append versions;
dispute notes are audit events, and status-changing dispute appends a version.
Ordinary correction creates UNREVIEWED; only named deterministic trusted
correction may directly create VERIFIED.
Identity-changing correction creates replacement EvidenceSeries v1, but keeps
correction audit semantics: non-null `supersedes_evidence_version_id` and
non-null CORRECTION status audit fields.
Invalidation and retraction tombstones are complete EvidenceVersion snapshots,
not sparse rows.

Invariant: no UPDATE or DELETE expresses these actions.

Alternatives Considered: boolean flags on old row; physical delete.

Rejected Alternatives: flags mutate history; delete breaks references.

Rationale: cited versions must remain resolvable.

Downstream Impact: UI/API show lineage hints.

Validation or Constraint: tombstone/status metadata schema, all-null/all-non-null
status audit check, complete snapshot copy, mandatory child-row copy, and status
transition checks; source retraction notice is represented on
SourceDocumentVersion by `source_status`, `source_status_changed_at`,
`source_status_actor`, and `source_status_reason`.

Example: source retraction appends a complete RETRACTED version with copied
locator/derivation/instrument child rows where required.

### D-08 Source Identity and Provenance

Selected Decision: capture canonical URL, publisher, issuer, external ID,
times, content_hash, version_fingerprint, media type, object key, language,
parser/extractor version, actor, and manual/automatic distinction.

Invariant: EvidenceVersion can explain source, collection, extraction, commit,
manual provenance, derivation, and corroboration without fake source rows.

Alternatives Considered: URL plus title only.

Rejected Alternatives: URLs drift and cannot reproduce bytes or parser context.

Rationale: Fact over narrative requires reproducible source chain.

Downstream Impact: WP04 commands require provenance fields.

Validation or Constraint: source-less Evidence allowed only for user-authored
estimate, user hypothesis, or inference with exact derivation links; source-less
Evidence has null SourceGrade and no SourceLocator.

Example: PDF filing stores hash, MinIO key, publication time, and page locator.

### D-09 Deduplication

Selected Decision: separate source identity dedupe, source-version fingerprint
dedupe, content-hash object reuse, candidate dedupe, series_identity_hash
matching, and similarity suggestions.

Invariant: vector similarity never auto-merges different source lineages, and
same facts from different `primary_source_document_id` values remain different
EvidenceSeries.
Changing CROSS_INSTRUMENT membership or DERIVED support ID set also creates a
different EvidenceSeries because `scope_key` or `origin_key` changes.

Alternatives Considered: one global semantic dedupe key.

Rejected Alternatives: global semantic dedupe would merge independent sources.

Rationale: independent sources are valuable corroboration.

Downstream Impact: similarity is review input, not write decision.

Validation or Constraint: unique `(source_document_id, version_fingerprint)`,
unique `series_identity_hash`, link-table uniqueness, and domain service checks.

Example: same fact in two announcements remains two Evidence lineages connected
only by optional corroboration links.

### D-10 Idempotency

Selected Decision: explicit idempotency table with scope, key, request hash,
status, and response reference.

Invariant: same key with different request hash conflicts.

Alternatives Considered: rely only on unique business constraints.

Rejected Alternatives: business constraints cannot distinguish replay from
semantic conflict.

Rationale: WP03 pattern already proves hash-based idempotency.

Downstream Impact: every mutation command accepts idempotency key; source import
reconciles MinIO object reuse before committing source metadata.

Validation or Constraint: primary key `(scope, idempotency_key)`.

Example: repeated import with same key/hash returns same source version; same
bytes with new observed_at only records observation metadata.

### D-11 Optimistic Concurrency

Selected Decision: expected_version is required for appending to existing
SourceDocument and EvidenceSeries aggregates. `expected_research_version` is
required when creating ResearchPackage N+1 with typed Evidence links.

Invariant: concurrent commands based on N cannot both create N+1 for the same
aggregate; Research reference refresh protects the instrument's ResearchPackage
version sequence.
Concurrent identity-changing replacements race on the new unique
`series_identity_hash`, not on appending to the old series.

Alternatives Considered: last write wins; serial global lock.

Rejected Alternatives: last write wins overwrites semantics; global lock is
unnecessary.

Rationale: WP03 already uses expected_version and DB constraints.

Downstream Impact: APIs expose expected/current version conflict details.

Validation or Constraint: lock aggregate or unique `(aggregate_id, version)`;
Research refresh locks current instrument ResearchPackage and creates
ResearchPackage/module/link rows atomically; replacement series creation uses
unique `series_identity_hash`.

Example: two same-series corrections race; one commits version 3, the other
receives current_version 3. Two replacements with the same new identity race on
`series_identity_hash`.

### D-12 Storage Boundaries

Selected Decision: PostgreSQL owns structured truth; MinIO owns immutable raw
bytes; pgvector owns rebuildable retrieval index; Redis owns live coordination.

Invariant: Redis, events, LLM output, and vectors are not system of record.

Alternatives Considered: Redis Streams as event truth; pgvector as Evidence
store.

Rejected Alternatives: Redis can be lost; vectors are derived.

Rationale: audit and replay require transactional structured records.

Downstream Impact: WP04-01 starts with PostgreSQL schema.

Validation or Constraint: storage matrix in section 19.

Example: embedding rebuild cannot change EvidenceVersion ID.

### D-13 Cross-Module References

Selected Decision: target references are exact EvidenceVersion IDs; WP03
source_refs strings remain legacy notes until a specific integration task.
Research typed links are immutable children of a ResearchModule snapshot and are
created only with ResearchPackage N+1.

Invariant: audit links never point to latest/current, and historical
ResearchModule link sets are never modified post-hoc.

Alternatives Considered: keep free strings; link to EvidenceSeries only; allow
post-hoc link insert into an existing ResearchModule.

Rejected Alternatives: free strings are not enforceable; series-only references
float over time; post-hoc insert mutates the meaning of an append-only WP03
ResearchModule snapshot.

Rationale: Research/Thesis replay needs exact version.

Downstream Impact: WP04-04 implements `research_module_evidence_link` as
snapshot child rows created by ResearchPackage N+1 refresh.

Validation or Constraint: foreign key to `evidence_version.id`, unique
`(research_module_id, evidence_version_id, link_role)`, and no standalone link
mutation command.

Example: old Research package continues citing old EvidenceVersion after
correction.

### D-14 Database Blueprint

Selected Decision: implement the tables in section 21 using SQLAlchemy 2.x,
Alembic, string UUID PKs, named constraints, timezone timestamps, SHA-256
identity hashes, and JSON only for bounded locator payloads and canonical
versioned metadata.

Invariant: schema supports versioning and audit without later semantic redesign.
The schema distinguishes same-series version appends from new EvidenceSeries
creation when identity dimensions change, and tombstones satisfy the same
non-null snapshot constraints as ordinary EvidenceVersion rows.
Replacement EvidenceVersion v1 is constrained separately from brand-new initial
v1 so it cannot use the no-predecessor audit-null exception.

Alternatives Considered: one evidence table copied from old TAD.

Rejected Alternatives: flat table cannot represent immutable source and
Evidence versions.

Rationale: WP04-01 needs implementation-ready field/constraint guidance.

Downstream Impact: WP04-01 migration can be dispatched directly.

Validation or Constraint: constraints and indexes listed per table.

Example: `evidence_version` has unique `(evidence_series_id, version)`;
`source_document_version` has unique `(source_document_id,
version_fingerprint)`; `evidence_series` has unique `series_identity_hash`;
tombstone rows retain complete snapshot fields and mandatory child rows;
replacement v1 rows set `supersedes_evidence_version_id` and non-null status
audit fields.

### D-15 Domain Command and Query Blueprint

Selected Decision: section 22 defines minimum service command/query semantics
before API design.

Invariant: domain service owns validation and commits.

Alternatives Considered: define HTTP endpoints first.

Rejected Alternatives: API-first would leak unresolved domain semantics.

Rationale: WP04-01 and WP04-02 are persistence/service first.

Downstream Impact: API can wrap stable domain commands later.

Validation or Constraint: each mutation has transaction, idempotency,
expected_version or expected_research_version rules, provenance validation, and
latest-first eligibility semantics. Commands that change identity dimensions use
`create_replacement_evidence_series`, not same-series append; replacement v1
must set `supersedes_evidence_version_id` and non-null CORRECTION status audit
fields.

Example: `create_evidence_series_version` validates locator before commit;
`revise_correct_evidence` rejects identity-dimension changes and routes them to
replacement series creation with full replacement v1 audit.

### D-16 Error Contract Blueprint

Selected Decision: stable `EVIDENCE_*` errors in section 23.

Invariant: domain errors are public contracts once API exists.

Alternatives Considered: use free-form HTTP detail strings.

Rejected Alternatives: strings cannot support generated clients.

Rationale: WP03 repairs showed typed error contracts are critical.

Downstream Impact: WP04-03 implements Pydantic/OpenAPI error schemas.

Validation or Constraint: each error has code, status suggestion, retryability,
and detail fields.

Example: stale expected_version returns `EVIDENCE_VERSION_CONFLICT`.

### D-17 V1 and Deferred Boundaries

Selected Decision: V1 supports single-user Evidence history and defers
multi-user, tenant, UI, worker, embedding pipeline, RAG implementation, and
Thesis engine.

Invariant: deferrals do not alter IDs, versions, provenance, or exact reference
semantics.

Alternatives Considered: add `user_id` now; implement worker/RAG in WP04-01.

Rejected Alternatives: no current auth/tenant model; broad implementation would
blur scope.

Rationale: contract must unblock persistence without inventing adjacent systems.

Downstream Impact: later features build on the same IDs.

Validation or Constraint: no user_id/tenant in core table blueprint.

Example: worker can later call the same import command.

### D-18 Follow-Up Task Boundaries

Selected Decision: follow-up tasks are WP04-01 persistence, WP04-02 service,
WP04-03 API/client, WP04-04 Research exact Evidence references.

Invariant: each task is a separately testable slice.

Alternatives Considered: one large WP04 implementation.

Rejected Alternatives: large slice would hide contract, DB, API, and Research
migration failures.

Rationale: existing WP03 succeeded through small accepted slices and repairs.

Downstream Impact: dispatcher can issue small task contracts.

Validation or Constraint: dependencies listed in section 27.

Example: WP04-04 cannot start before exact EvidenceVersion exists.

## 26. V1 Scope and Explicit Deferrals

V1 contract supports:

- Single-user local system.
- Manual and automatic source import.
- Immutable raw source versions.
- Atomic Evidence.
- SourceGrade S-F.
- Four InformationType values.
- Exact source-backed SourceLocator, manual provenance, derivation links, and
  corroboration links.
- Version history.
- Correction, dispute, invalidation, and retraction.
- Idempotency.
- Optimistic concurrency.
- Research migration to exact EvidenceVersion references.

Explicit deferrals that do not block WP04-01:

- Multi-user permissions and tenant partitioning.
- Advanced entity resolution.
- Automatic fact graph.
- Large-scale OCR.
- Full semantic deduplication automation.
- Cross-source conflict adjudication.
- Browser UI.
- WP05 Thesis full implementation.
- Worker orchestration.
- Durable outbox implementation.
- Embedding pipeline.
- RAG query implementation.

## 27. WP04 Follow-Up Task Boundaries

1. `TASK-WP04-01` - Evidence persistence foundation.
   - Implement models, migration, registry import, repository helpers, and
     persistence tests for source/evidence identity, versions,
     evidence_instrument_link, evidence_corroboration_link, and
     evidence_derivation_link. Tests must cover identity-dimension changes
     creating new EvidenceSeries and tombstone rows satisfying complete
     EvidenceVersion constraints. Migration tests must distinguish brand-new
     no-predecessor v1 UNREVIEWED rows from replacement v1 rows and must reject
     replacement v1 with null status audit fields.
   - Depends on this contract.

2. `TASK-WP04-02` - Evidence domain service.
   - Implement versioning, idempotency, expected_version, locator validation,
     latest-first eligibility, state transitions, manual provenance,
     derivation/corroboration validation, status audit metadata enforcement,
     replacement-series routing, complete tombstone child-row copy, and service
     tests.
   - Depends on WP04-01.

3. `TASK-WP04-03` - Evidence API and OpenAPI.
   - Implement endpoints, Pydantic schemas, public error contracts, and
     generated client contract tests.
   - Depends on WP04-02.

4. `TASK-WP04-04` - Research exact Evidence references.
   - Add typed immutable EvidenceVersion references from Research modules while
     preserving legacy `source_refs` compatibility. Typed links are created
     only by ResearchPackage N+1 snapshot creation with
     `expected_research_version`.
   - Depends on WP04-03 and accepted Research API/client contracts.

## 28. Traceability Matrix

| Contract decision | Source evidence |
|---|---|
| LLM is not system of record and only proposes | `AGENTS.md`, `README.md`, `STRUCTURED_OUTPUT_CONTRACTS.md`, `AGENT_RUNTIME_ARCHITECTURE.md`. |
| PostgreSQL owns structured truth | `AGENTS.md`, TAD storage split, Agent Runtime PostgreSQL durable truth. |
| MinIO owns raw files | `AGENTS.md`, TAD object storage, `backend/common/storage.py`. |
| pgvector is rebuildable retrieval index | TAD DB/RAG split, Agent Runtime context and failure semantics. |
| Redis is coordination/live projection only | `backend/common/events.py`, Agent Runtime event taxonomy, Project Status Audit RSK-002. |
| InformationType four values | Task contract, TAD Evidence, PRD Evidence体系. |
| SourceGrade S-F and F restriction | Task contract and PRD section 11. |
| SourceDocumentVersion identity by version_fingerprint | TASK-WP04-00-R1 findings, storage split, MinIO byte identity, immutable source snapshots. |
| EvidenceSeries lineage by series_identity_hash | TASK-WP04-00-R1 findings, independent source lineage requirement, PostgreSQL NULL semantics. |
| Identity-dimension changes create new EvidenceSeries | TASK-WP04-00-R2 findings; `series_identity_hash` must remain the single lineage identity. |
| Replacement v1 is audited correction lineage, not brand-new initial evidence | TASK-WP04-00-R3 finding; `version=1` alone must not bypass lifecycle audit when `supersedes_evidence_version_id` is non-null. |
| CROSS_INSTRUMENT and DERIVED child-set identity | TASK-WP04-00-R2 findings; `scope_key` and `origin_key` are identity inputs. |
| Atomic Evidence and source locator/manual provenance | Structured Output Contracts `EvidenceExtractionResult@1`, task canonical boundary. |
| Corroboration and derivation do not merge lineage | Fact > narrative principle, source lineage audit requirement. |
| Immutable versions and exact references | AGENTS immutable history, WP03 append-only version model, Agent Runtime exact domain version references. |
| Latest-first current valid semantics | TASK-WP04-00-R1 lifecycle finding and audit replay requirement. |
| Lifecycle audit metadata and complete tombstones | TASK-WP04-00-R2 findings; append-only history must retain who/when/why and legal non-null snapshots. |
| Idempotency and expected_version style | WP03 API/docs/services/tests and acceptance reports. |
| Research typed links as snapshot children | WP03 append-only ResearchPackage/ResearchModule implementation and R1 immutable snapshot finding. |
| WP03 source_refs migration gap | WP03 models/schemas/generated types/docs/tests showing `source_refs: list[str]`. |

## 29. Non-Blocking Future Considerations

- A later architecture update can reconcile old TAD flat `evidence` sketch with
  this versioned model.
- A future SourceType extension process can add provider-specific values once
  real data connectors exist.
- A future storage retention policy can define archival of raw objects while
  preserving exact audit references.
- A future UI can render lineage, retraction tombstones, dispute banners, and
  Research reference migration status.
- A future outbox can project Evidence domain events into Redis while keeping
  PostgreSQL as truth.
- A future evaluator can compare extraction accuracy across parsers and LLM
  providers without changing committed Evidence identity.
