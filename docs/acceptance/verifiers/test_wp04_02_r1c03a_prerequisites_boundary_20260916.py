"""New verifier-owned boundary oracle; not a restored historical verifier.

Shared fixture and constraint-legal legacy seed only are imported from candidate.
Public commands, expected outcomes and persisted row comparisons are owned here.
No diagnostic monkeypatch or production rule injection is used.
"""

import os

import pytest
from backend.evidence import services
from backend.evidence.errors import EvidenceValidationError
from backend.evidence.models import (
    EvidenceAuditEvent,
    EvidenceDerivationLink,
    EvidenceIdempotencyRecord,
    EvidenceInstrumentLink,
    EvidenceSeries,
    EvidenceSourceLocator,
    EvidenceVersion,
    SourceDocument,
    SourceDocumentVersion,
)
from sqlalchemy import select
from tests.test_evidence_services import db as db
from tests.test_evidence_services import dt, r1c03a_legacy_prior
from tests.test_evidence_services import pg_sessionmaker as pg_sessionmaker

pytestmark = pytest.mark.asyncio
ROUTES = ["same", "automatic", "direct", "initial", "underlying-replacement"]
MODELS = [
    EvidenceSeries,
    EvidenceVersion,
    EvidenceSourceLocator,
    EvidenceInstrumentLink,
    EvidenceDerivationLink,
    EvidenceIdempotencyRecord,
    EvidenceAuditEvent,
    SourceDocument,
    SourceDocumentVersion,
]


def columns(row):
    return {col.name: getattr(row, col.name) for col in row.__table__.columns}


def exact_snapshot(row):
    return {
        "version": columns(row),
        **{
            rel: sorted([columns(c) for c in getattr(row, rel)], key=lambda x: x["id"])
            for rel in ["source_locators", "instrument_links", "derived_links"]
        },
    }


async def durable_rows(session):
    """Compare all columns of all rows, including audit and idempotency."""
    result = {}
    for model in MODELS:
        rows = (await session.execute(select(model.__table__))).mappings().all()
        result[model.__tablename__] = sorted([dict(r) for r in rows], key=repr)
    return result


async def command(session, prior, route, rule_kwargs, key):
    audit = {
        "status_changed_at": dt(day=16),
        "status_changed_by_actor": "IMPORTER",
        "status_reason": "Verifier-owned boundary correction",
        "idempotency_key": key,
    }
    if route in {"same", "automatic"}:
        changed = {}
        if route == "automatic":
            old_support = await services.get_exact_evidence_version(
                session, prior.derived_links[0].supporting_evidence_version_id
            )
            assert old_support.supersedes_evidence_version_id is not None
            changed["derivation_links"] = [
                services.DerivationLinkInput(
                    supporting_evidence_version_id=old_support.supersedes_evidence_version_id,
                    role="INPUT_FACT",
                    support_order=1,
                )
            ]
        return await services.revise_correct_evidence(
            session,
            evidence_series_id=prior.evidence_series_id,
            expected_version=prior.version,
            display_text="Verifier-owned corrected text",
            **changed,
            **audit,
            **rule_kwargs,
        )
    series = await session.get(EvidenceSeries, prior.evidence_series_id)
    fields = {
        "scope_type": series.scope_type,
        "scope_key": series.scope_key,
        "information_type": prior.information_type,
        "claim_key": prior.claim_key,
        "metric_key": "verifier-owned-new-metric",
        "period_start": prior.period_start,
        "period_end": prior.period_end,
        "provenance_kind": prior.provenance_kind,
        "primary_source_document_id": series.primary_source_document_id,
        "source_document_version_id": prior.source_document_version_id,
        "display_title": prior.display_title,
        "display_text": "Verifier-owned corrected text",
        "raw_value": prior.raw_value,
        "raw_unit": prior.raw_unit,
        "normalized_value": prior.normalized_value,
        "normalized_unit": prior.normalized_unit,
        "as_of": prior.as_of,
        "extractor_name": prior.extractor_name,
        "extractor_version": prior.extractor_version,
        "locators": [
            services.SourceLocatorInput(
                locator_type=c.locator_type,
                raw_locator=c.raw_locator,
                short_citation=c.short_citation,
                locator_payload=dict(c.locator_payload),
                quote_hash=c.quote_hash,
            )
            for c in prior.source_locators
        ],
        "instrument_links": [
            services.InstrumentLinkInput(
                instrument_id=c.instrument_id,
                role=c.role,
                link_order=c.link_order,
                link_metadata=dict(c.link_metadata or {}),
            )
            for c in prior.instrument_links
        ],
    }
    if route == "direct":
        return await services.create_replacement_evidence_series(
            session, prior_evidence_version_id=prior.id, **fields, **audit, **rule_kwargs
        )
    if route == "initial":
        return await services.create_evidence_series_version(
            session, **fields, idempotency_key=key, **rule_kwargs
        )
    assert route == "underlying-replacement"
    return await services.create_evidence_series_version(
        session,
        **fields,
        supersedes_evidence_version_id=prior.id,
        verification_status="VERIFIED",
        status_change_kind="CORRECTION",
        **audit,
        **rule_kwargs,
    )


async def test_empty_production_approval_and_normal_environment():
    assert frozenset() == services._APPROVED_TRUSTED_CORRECTION_RULES
    for name in ["TG_TEST_ADMIN_DATABASE_URL", "TG_R1C_REPLAY_BASELINE", "TG_R1C02_REPLAY_PRIOR"]:
        assert name not in os.environ


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize(
    "rule",
    [
        "",
        " \t\n",
        "unknown-rule",
        "same-source-parser-v1",
        "SAME-SOURCE-PARSER-V1",
        False,
        1,
        {},
        [],
    ],
    ids=[
        "empty",
        "whitespace",
        "unknown",
        "legacy-fixture",
        "case",
        "bool",
        "int",
        "mapping",
        "list",
    ],
)
async def test_rejected_trusted_commit_preserves_every_durable_row(
    db, pg_sessionmaker, route, rule
):
    prior = await r1c03a_legacy_prior(db, derived=route == "automatic")
    before = await durable_rows(db)
    old = exact_snapshot(prior)
    with pytest.raises(EvidenceValidationError) as error:
        await command(db, prior, route, {"trusted_correction_rule": rule}, "owned-denied")
    assert error.value.code == "EVIDENCE_VALIDATION_ERROR"
    assert error.value.details["validation_path"] == "trusted_correction_rule"
    assert error.value.details["trusted_correction_rule"] == rule
    assert error.value.details["rule_type"] == type(rule).__name__
    assert error.value.details["reason"] == (
        "unapproved_rule" if isinstance(rule, str) else "invalid_rule_type"
    )
    assert not db.new and not db.dirty
    await db.commit()
    async with pg_sessionmaker() as fresh:
        assert await durable_rows(fresh) == before
        original = await services.get_exact_evidence_version(fresh, prior.id)
        assert exact_snapshot(original) == old
        assert original.trusted_correction_rule == "legacy-historical-rule"
        assert (await services.get_current_evidence(fresh, prior.evidence_series_id)).id == prior.id


@pytest.mark.parametrize("route", [r for r in ROUTES if r != "initial"])
@pytest.mark.parametrize(
    "rule_kwargs", [{}, {"trusted_correction_rule": None}], ids=["omitted", "none"]
)
async def test_ordinary_never_inherits_and_retains_correction_routing(
    db, pg_sessionmaker, route, rule_kwargs
):
    prior = await r1c03a_legacy_prior(db, derived=route == "automatic")
    old = exact_snapshot(prior)
    corrected = await command(db, prior, route, rule_kwargs, "owned-ordinary")
    result_id = corrected.id
    await db.commit()
    async with pg_sessionmaker() as fresh:
        original = await services.get_exact_evidence_version(fresh, prior.id)
        result = await services.get_exact_evidence_version(fresh, result_id)
        assert exact_snapshot(original) == old
        assert original.trusted_correction_rule == "legacy-historical-rule"
        assert result.verification_status == "UNREVIEWED"
        assert result.trusted_correction_rule is None
        assert result.supersedes_evidence_version_id == prior.id
        assert (
            result.status_changed_at,
            result.status_changed_by_actor,
            result.status_change_kind,
            result.status_reason,
        ) == (dt(day=16), "IMPORTER", "CORRECTION", "Verifier-owned boundary correction")
        assert result.display_text == "Verifier-owned corrected text"
        assert await services.get_current_valid_evidence(fresh, result.evidence_series_id) is None
        if route == "same":
            assert result.evidence_series_id == prior.evidence_series_id
            assert result.version == prior.version + 1
        else:
            assert result.evidence_series_id != prior.evidence_series_id
            assert result.version == 1
            assert (
                await services.get_current_evidence(fresh, prior.evidence_series_id)
            ).id == prior.id
        for rel in ["source_locators", "instrument_links", "derived_links"]:
            a, b = getattr(original, rel), getattr(result, rel)
            assert len(a) == len(b)
            assert {c.id for c in a}.isdisjoint(c.id for c in b)
        events = list(
            await fresh.scalars(
                select(EvidenceAuditEvent).where(EvidenceAuditEvent.aggregate_id == result_id)
            )
        )
        assert len(events) == 1
        assert events[0].event_type == "EVIDENCE_CORRECTION"
        assert events[0].actor == "IMPORTER"
        assert events[0].occurred_at == dt(day=16)


@pytest.mark.parametrize("route", ["direct", "initial"])
@pytest.mark.parametrize("trusted", [False, True], ids=["same-request", "new-trusted-request"])
async def test_replay_is_read_only_and_never_absorbs_new_trust(db, pg_sessionmaker, route, trusted):
    prior = await r1c03a_legacy_prior(db, derived=False)
    result = await command(db, prior, route, {}, "owned-replay")
    result_id = result.id
    await db.commit()
    before = await durable_rows(db)
    async with pg_sessionmaker() as caller:
        original = await services.get_exact_evidence_version(caller, prior.id)
        if trusted:
            with pytest.raises(EvidenceValidationError) as error:
                await command(
                    caller,
                    original,
                    route,
                    {"trusted_correction_rule": "unknown-rule"},
                    "owned-replay",
                )
            assert error.value.code == "EVIDENCE_VALIDATION_ERROR"
            assert error.value.details["validation_path"] == "trusted_correction_rule"
        else:
            replayed = await command(caller, original, route, {}, "owned-replay")
            assert replayed.id == result_id
        await caller.commit()
    async with pg_sessionmaker() as fresh:
        assert await durable_rows(fresh) == before
        persisted = await services.get_exact_evidence_version(fresh, result_id)
        assert persisted.trusted_correction_rule is None
        assert persisted.verification_status == "UNREVIEWED"
